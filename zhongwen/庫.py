from zhongwen.batch_data import 通知執行時間, 取資料庫, 批次寫入, 結果批次寫入
from zhongwen.batch_data import 增加定期更新
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

def 批次載入(資料庫檔, 表格, 批號欄名, 時間欄位=None, 期間欄位=None, 最小批號=None):
    '指定最小批號則載入批號大於或等於最小批號之紀錄，如不指定則載入最大批號之紀錄'
    from zhongwen.時 import 取日期, 取期間
    from collections.abc import Iterable 
    import pandas as pd
    import sqlite3
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
