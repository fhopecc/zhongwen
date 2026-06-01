from pathlib import Path
import functools
import logging
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(Path(__file__).stem)

# -------------------------------------------------------------------
# 連線池快取機制：確保同一個資料庫檔案只會有一個連線池，達到資源共用與加速
# -------------------------------------------------------------------
_ENGINES = {}


def 取連線池引擎(資料庫路徑):
    """根據資料庫路徑獲取或建立 SQLAlchemy Engine 連線池"""
    path_str = str(Path(資料庫路徑).resolve())
    if path_str not in _ENGINES:
        _ENGINES[path_str] = create_engine(
            f"sqlite:///{path_str}",
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            connect_args={"timeout": 30} 
        )
    return _ENGINES[path_str]


def 關閉所有連線池():
    """當程式即將結束、資源要關掉時，呼叫此函數徹底關閉所有連線"""
    global _ENGINES
    for path, engine in _ENGINES.items():
        logger.debug(f"正在關閉資料庫連線池: {path}")
        engine.dispose()
    _ENGINES.clear()
    logger.debug("所有資料庫連線已安全關閉。")


def 解析更新期限(更新期限='次月10日前'):
    '解析更新期限之有效值有【每次更新】、【次月10日前】、【次季45日前】、【次月底前】及【財報】，傳回【應更新資料時期、應更新資料期限及定期更新資訊】'
    from zhongwen.date import 上年底, 上月, 上季, 今日, 月底, 取日期, 季別
    from zhongwen.date import 民國正式日期, 民國年月, 民國年, 民國季別
    from datetime import timedelta
    import re
    today = 今日()
    應更新資料時期, 應更新資料期限 = None, None
    if 更新期限 == '每次更新':
        return 解析更新期限('次月底前')

    if '財報' in 更新期限:
        應更新資料時期 = 上季()
        _, 季數 = 季別(應更新資料時期)
        match 季數: 
            case 2:
                應更新資料期限 = 取日期(f'{應更新資料時期.year}.8.31')
            case 4:
                應更新資料期限 = 取日期(f'{應更新資料時期.year+1}.3.31')
            case _:
                應更新資料期限 = 應更新資料時期 + timedelta(days=60)
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國季別(應更新資料時期)}資訊。')
        
    if '次月' in 更新期限:
        應更新資料時期 = 上月()
    elif '次年' in 更新期限:
        應更新資料時期 = 上年底()
    elif '次季' in 更新期限:
        應更新資料時期 = 上季()

    pat = r'(\d+)(日|個月)(內|前)'
    if m := re.search(pat, 更新期限):
        n = int(m[1])
        if m[2] == "日":
            應更新資料期限 = 應更新資料時期 + timedelta(days=n)
        elif m[2] == "個月":
            from datetime import datetime, timedelta
            import calendar
            data_date = 應更新資料時期 + timedelta(days=1)
            month = data_date.month-1
            year = data_date.year
            future_month = month + n
            if future_month > 12:
                future_month -= 12
                year += 1
            _, days_in_future_month = calendar.monthrange(year, future_month)
            future_date = data_date.replace(year=year, month=future_month, day=max(data_date.day, days_in_future_month))
            應更新資料期限 = future_date
        if today.month == 2: 
            應更新資料期限 = 月底()

    pat = r'月底前'
    if m := re.search(pat, 更新期限):
        應更新資料期限 = 月底()
    if '次月' in 更新期限:
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國年月(應更新資料時期)}資訊。')
    elif '次年' in 更新期限:
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國年(應更新資料時期)}資訊。')
    elif '次季' in 更新期限:
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國季別(應更新資料時期)}資訊。')


def 轉儲存字串(日期或期間):
    from zhongwen.時 import 取日期, 取期間
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
    
    engine = 取連線池引擎(資料庫檔)
    with engine.connect() as conn:
        sql = f"select * from {表格}"
        if 最小批號:
            if 最小批號 == float('inf'):
                sql += f" where {批號欄名} = (SELECT MAX({批號欄名}) FROM {表格})"
            else:
                if isinstance(最小批號, pd.Timestamp) or isinstance(最小批號, pd.Period):
                    batchno = 轉儲存字串(最小批號)
                    sql += f" where {批號欄名} >= '{batchno}'"
                else:
                    sql += f" where {批號欄名} >= {最小批號}"
        try:
            df = pd.read_sql_query(text(sql), conn, index_col='index') 
        except KeyError as e:
            logger.info(f'{表格}無 index 欄位！')
            df = pd.read_sql_query(text(sql), conn) 
        for c in cs:
            df[c] = df[c].map(取日期)
        for p in ps:
            df[p] = df[p].map(取期間) 
        return df


def 批次寫入(資料, 批號, 批號欄名, 表格, 資料庫, 指定欄位=None):
    '如有指定欄位，原始資料則另寫入原始資料庫'
    from zhongwen.date import 有日期嗎
    from zhongwen.batch_data import 取資料庫檔路徑
    
    if 資料.empty:
        return 
    資料.loc[:, 批號欄名] = 批號
    表格不存在 = False

    # ─── 核心相容性升級：如果發現外部傳進來的是舊 sqlite3 連線，自動轉換為連線池連線 ───
    if isinstance(資料庫, sqlite3.Connection):
        資料庫檔路徑 = 取資料庫檔路徑(資料庫)
        engine = 取連線池引擎(資料庫檔路徑)
        with engine.connect() as conn:
            return 批次寫入(資料, 批號, 批號欄名, 表格, conn, 指定欄位=指定欄位)
    
    # ─── 往下執行時，資料庫參數必為 SQLAlchemy Connection 物件 ───
    try:
        # 執行刪除舊批號資料（不帶有 begin 衝突）
        批次刪除(批號, 批號欄名, 表格, 資料庫)
    except Exception as e:
        if 'no such table' in str(e).lower():
            logger.debug(f'尚無【{表格}】資料表……')
            表格不存在 = True
        else:
            logger.debug(f'批次刪除發生錯誤：{e}')
            
    logger.debug(f'批號【{批號}】資料擬整批寫入至{表格}……')
    
    if 指定欄位:
        if 批號欄名 not in 指定欄位:
            指定欄位.append(批號欄名)
        指定欄位 = [c for c in 資料.columns if c in 指定欄位]
        
        db_path_str = 資料庫.engine.url.database
        資料庫檔路徑 = Path(db_path_str)
        資料庫檔路徑 = 資料庫檔路徑.with_stem(f'原始{資料庫檔路徑.stem}')
        
        原始引擎 = 取連線池引擎(資料庫檔路徑)
        with 原始引擎.connect() as 原始連線:
            try:
                批次刪除(批號, 批號欄名, 表格, 原始連線)
            except Exception as e:
                if 'no such table' in str(e).lower():
                    logger.debug(f'原始資料庫尚無【{表格}】資料表……')
                    表格不存在 = True
                else:
                    logger.debug(f'批次刪除發生錯誤：{e}')
            
            批次寫入(資料[指定欄位], 批號, 批號欄名, 表格, 原始連線)
            
    try:
        for c in 資料.columns:
            if 有日期嗎(資料[c]):
                資料[c] = 資料[c].map(轉儲存字串)
            elif isinstance(資料[c].dtype, pd.PeriodDtype) or '季別' in c:
                資料[c] = 資料[c].map(str)
                
        # ─── 修正點：外層統一控管 Transaction ───
        with 資料庫.begin():
            資料.to_sql(表格, 資料庫, if_exists='append')
            if 表格不存在:
                logger.debug(f'擬建立表格【{表格}】及其索引【{批號欄名}】……')
                sql = f'CREATE INDEX idx_{批號欄名} ON {表格}({批號欄名})'
                資料庫.execute(text(sql))
                logger.debug('完成！')
        logger.debug(f'寫入成功！')
        
    except Exception as e:
        # ─── 欄位不符異常修補機制 ───
        logger.debug(f"常規寫入失敗，觸發自動補欄位機制。錯誤原因: {e}")
        
        # 讀取快照（獨立執行，不放入 begin 區塊內避免鎖定）
        df_snapshot = pd.read_sql_query(text(f'select * from {表格} limit 1'), 資料庫)
        寫入資料欄位 = 資料.columns.to_list()
        資料庫欄位 = df_snapshot.columns.to_list()
        差異欄位 = set(寫入資料欄位) - set(資料庫欄位)
        logger.debug(f"偵測到未建立欄位：{差異欄位}")
        
        if 差異欄位:
            with 資料庫.begin():
                for c in 差異欄位:
                    alter_query = f'ALTER TABLE {表格} ADD COLUMN "{c}" INT'
                    資料庫.execute(text(alter_query))
            logger.debug('前開資料庫未建立欄位已新增……')
            
        # 重新嘗試寫入（使用獨立的新交易區塊）
        with 資料庫.begin():
            資料.to_sql(表格, 資料庫, if_exists='append')
        logger.debug(f'補齊欄位後寫入成功！')


def 釐正時間欄位(資料庫檔, 表格, 時間欄位=None, 期間欄位=None):
    from zhongwen.表 import 顯示
    from zhongwen.時 import 取日期, 取期間
    
    engine = 取連線池引擎(資料庫檔)
    with engine.connect() as c:
        sql = f"select * from {表格}"
        df = pd.read_sql_query(text(sql), c, index_col='index') 
        if 時間欄位:
            for c_col in 時間欄位:
                df[c_col] = df[c_col].map(取日期).map(轉儲存字串)
        if 期間欄位:
            for p in 期間欄位:
                df[p] = df[p].map(取期間).map(轉儲存字串)
        顯示(df)
        
        with c.begin():
            df.to_sql(表格, c, if_exists='replace')


def 通知執行時間(f):
    from zhongwen.程式 import 通知執行時間 as 程式通知執行時間 
    return 程式通知執行時間(f)


def 批次刪除(批號, 批號欄名, 表格, 資料庫):
    from zhongwen.date import 全是日期嗎
    import pandas as pd
    logger.debug(f'{表格}刪除{批號}整批紀錄……')
    
    if isinstance(資料庫, sqlite3.Connection):
        from zhongwen.batch_data import 取資料庫檔路徑
        資料庫檔路徑 = 取資料庫檔路徑(資料庫)
        engine = 取連線池引擎(資料庫檔路徑)
        with engine.connect() as conn:
            return 批次刪除(批號, 批號欄名, 表格, conn)
            
    if isinstance(批號, pd.Period):
        批號 = str(批號)
    elif 全是日期嗎(批號) if '全是日期嗎' in locals() else False:
        批號 = 轉儲存字串(批號)
        
    sql = f'delete from {表格} where {批號欄名}=="{批號}"'
    
    # ─── 修正點：移除內層的 with 資料庫.begin() ───
    # 改用常規 execute 執行。如果在外部已有交易，會自動併入；若無，SQLite 會隱式遞交。
    # 這樣可以徹底避開 Transaction 衝突造成的 InvalidRequestError
    資料庫.execute(text(sql))
    logger.debug(f'成功')


def 增加定期更新(更新期限='次月10日前', 更新程序=解析更新期限):
    from zhongwen.batch_data import 解析更新期限
    from zhongwen.date import 今日
    from datetime import timedelta
    from functools import wraps
    緩衝期 = timedelta(days=3)
    def 增加定期更新功能(查詢資料):
        @wraps(查詢資料)
        def 查詢定期更新資料(*args, 更新=False, **kargs):
            資料時期, 公布期限, 資訊 = 解析更新期限(更新期限)
            if 更新 or (資料時期 < 今日() <= 公布期限 + 緩衝期):
                更新程序(資料時期)
            return 查詢資料(*args, **kargs)
        return 查詢定期更新資料
    return 增加定期更新功能


def 應更新資料時期(更新頻率='次月十日前'):
    from zhongwen.date import 今日, 上月
    if 更新頻率 == '次月十日前':
        if 今日().day <= 10:
            return 上月()


def 結果批次寫入(資料庫檔, 資料名稱, 批號欄名, 預設批號組=[], 指定欄位=None):
    from collections.abc import Iterable
    from functools import wraps
    
    def 增加結果批次寫入(爬取資料函數):
        @wraps(爬取資料函數)
        def 批次寫入爬取資料(批號組=None, **kargs):
            if not 批號組:
                批號組 = 預設批號組
            if isinstance(批號組, str) or not isinstance(批號組, Iterable):
                批號組 = [批號組]
            
            engine = 取連線池引擎(資料庫檔)
            df = pd.DataFrame() 
            
            with engine.connect() as db:
                for 批號 in 批號組:
                    df = 爬取資料函數(批號, **kargs)
                    if df.empty:
                        continue
                    批號 = df.iloc[0][批號欄名]
                    批次寫入(df, 批號, 批號欄名, 資料名稱, db, 指定欄位)
            return df
        return 批次寫入爬取資料
    return 增加結果批次寫入
