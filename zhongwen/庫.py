from zhongwen.batch_data import 取資料庫, 結果批次寫入
from zhongwen.batch_data import 增加定期更新, 批次刪除
from pathlib import Path
import logging

logger = logging.getLogger(Path(__file__).stem)

def 轉儲存字串(日期或期間):
    from zhongwen.時 import 取日期, 取期間
    import pandas as pd
    try:
        if isinstance(日期或期間, pd.Timestamp):
            d = 取日期(日期或期間)
            return f"{d.year}-{d.month:02d}-{d.day:02d}"
        elif isinstance(日期或期間, pd.Period):
            return str(日期或期間)
    except AttributeError:
        logger.debug(f"{日期或期間}非有效日期或期間。")
        return 日期或期間

class 查無批號錯誤(Exception): pass

def 載入上批資料(資料庫檔, 表格, 批號欄名, 時間欄位=None, 期間欄位=None):
    '載入最大批號之紀錄'
    return 批次載入(資料庫檔, 表格, 批號欄名, 時間欄位, 期間欄位, 最小批號=float('inf'))

def 批次載入(資料庫檔, 表格, 批號欄名, 時間欄位=None, 期間欄位=None, 起始批號=None, 最小批號=None):
    '指定起始批號則載入批號大於或等於其批號之紀錄，如不指定則載入最末批號之紀錄'
    from zhongwen.時 import 取日期, 取期間
    from collections.abc import Iterable 
    import pandas as pd
    import sqlite3

    if not 起始批號 is None:
        最小批號 = 起始批號

    cs, ps = 時間欄位, 期間欄位
    if isinstance(cs, str) or not isinstance(cs, Iterable):
        if cs is None:
            cs = []
        else:
            cs = [cs]
    if isinstance(ps, str) or not isinstance(ps, Iterable):
        if ps is None:
            ps = []
        else:
            ps = [ps]
    
    with sqlite3.connect(資料庫檔) as c:
        sql = f"select * from {表格}"
        if 最小批號:
            if 最小批號==float('inf'):
                sql += f" where {批號欄名} = (SELECT MAX({批號欄名}) FROM {表格})"
            else:
                batchno = 轉儲存字串(最小批號)
                sql += f" where {批號欄名} >= '{batchno}'"

        try:
            df = pd.read_sql_query(sql, c, index_col='index') 
        except KeyError as e:
            logger.info(f'{表格}無 index 欄位！')
            df = pd.read_sql_query(sql, c) 
        for c in cs:
            df[c] = df[c].map(取日期)
        for p in ps:
            df[p] = df[p].map(取期間) 
        return df

def 批次寫入(資料, 批號, 批號欄名, 表格, 資料庫, 指定欄位=None):
    '如有指定欄位，原始資料則另寫入原始資料庫'
    from zhongwen.text import 臚列
    from zhongwen.date import 有日期嗎
    from zhongwen.batch_data import 取資料庫檔路徑
    import pandas as pd
    import sqlite3
    import re
    # if '財報季別' in 資料.columns:
        # breakpoint()
    if 資料.empty:
        return 
    資料.loc[:, 批號欄名] = 批號
    表格不存在=False
    try:
        批次刪除(批號, 批號欄名, 表格, 資料庫)
    except sqlite3.OperationalError as e:
        if 'no such table' in str(e):
            logger.debug(f'尚無【{表格}】資料表……')
            表格不存在=True
        else:
            logger.debug(f'批次刪除發生錯誤：{e}')
    logger.debug(f'批號【{批號}】資料擬整批寫入至{表格}……')
    if 指定欄位:
        if 批號欄名 not in 指定欄位:
            指定欄位.append(批號欄名)
        指定欄位 = [c for c in 資料.columns if c in 指定欄位]
        欄位縮減資料庫 = 資料庫
        資料庫檔路徑 = 取資料庫檔路徑(資料庫)
        資料庫檔路徑 = 資料庫檔路徑.with_stem(f'原始{資料庫檔路徑.stem}')
        資料庫 = 取資料庫(資料庫檔路徑)
        try:
            批次刪除(批號, 批號欄名, 表格, 資料庫)
        except sqlite3.OperationalError as e:
            if 'no such table' in str(e):
                logger.debug(f'原始資料庫尚無【{表格}】資料表……')
                表格不存在=True
            else:
                logger.debug(f'批次刪除發生錯誤：{e}')
        批次寫入(資料[指定欄位], 批號, 批號欄名, 表格, 欄位縮減資料庫)
    try:
        for c in 資料.columns:
            if 有日期嗎(資料[c]):
                資料[c] = 資料[c].map(轉儲存字串)
            elif isinstance(資料[c].dtype, pd.PeriodDtype) or '季別' in c:
                資料[c] = 資料[c].map(str)
        資料.to_sql(表格, 資料庫, if_exists='append')
        if 表格不存在:
            logger.debug(f'擬建立表格【{表格}】及其索引【{批號欄名}】……')
            sql = f'CREATE INDEX idx_{批號欄名} ON {表格}({批號欄名})'
            cursor = 資料庫.cursor()
            cursor.execute(sql)
            資料庫.commit()
            logger.debug('完成！')
        logger.debug(f'寫入成功！')
    except sqlite3.OperationalError as e:
        df = pd.read_sql_query(f'select * from {表格} limit 1', 資料庫)
        寫入資料欄位 = 資料.columns.to_list()
        資料庫欄位 = df.columns.to_list()
        差異欄位 = set(寫入資料欄位) - set(資料庫欄位)
        # logger.debug(f'寫入資料之{臚列(差異欄位)}等欄位，資料庫尚未建立……')
        logger.debug(差異欄位)
        cursor = 資料庫.cursor()
        for c in 差異欄位:
            alter_query = f'ALTER TABLE {表格} ADD COLUMN "{c}" INT'
            cursor.execute(alter_query)
        資料庫.commit()
        logger.debug('前開資料庫未建立欄位已新增……')
        資料.to_sql(表格, 資料庫, if_exists='append')
        logger.debug(f'寫入成功！')

def 釐正時間欄位(資料庫檔, 表格, 時間欄位=None, 期間欄位=None):
    from zhongwen.表 import 顯示
    import sqlite3
    import pandas as pd
    from zhongwen.時 import 取日期, 取期間
    with sqlite3.connect(資料庫檔) as c:
        sql = f"select * from {表格}"
        df = pd.read_sql_query(sql, c, index_col='index') 
        if 時間欄位:
            for c in 時間欄位:
                df[c] = df[c].map(取日期).map(轉儲存字串)
        if 期間欄位:
            for p in 期間欄位:
                df[p] = df[p].map(取期間).map(轉儲存字串)
        顯示(df)
        df.to_sql(表格, c, if_exists='replace')

def 通知執行時間(f):
    from zhongwen.程式 import 通知執行時間 as 程式通知執行時間 
    return 程式通知執行時間(f)
