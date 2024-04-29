from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 通知執行時間(f):
    from functools import wraps
    from time import time
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logger.info(f'{f.__name__}費時{time()-ts:.2f}秒。')
        return result
    return wrap

class 查無批號錯誤(Exception): pass

def 批次讀取(批號, 批號欄名, 表格, 資料庫, 日期欄位=None):
    import pandas as pd
    from zhongwen.date import 是日期嗎
    # sql 相等運算子係單等號，而python為雙等號，易誤植
    sql = f'select * from {表格} where {批號欄名}={批號}' 
    if 是日期嗎(批號) or isinstance(批號, str):
        sql = f'select * from {表格} where {批號欄名}="{批號}"' 
    df = pd.read_sql_query(sql, 資料庫, parse_dates=日期欄位)
    if df.empty: 
        raise 查無批號錯誤(f'查無【{批號}】批號！')
    return df

def 批次刪除(批號, 批號欄名, 表格, 資料庫):
    logger.debug(f'{表格}刪除{批號}整批紀錄……')
    c = 資料庫.cursor()
    sql = f'delete from {表格} where {批號欄名}=="{批號}"'
    c.execute(sql)
    資料庫.commit()
    logger.debug(f'成功')

def 批次寫入(資料, 批號, 批號欄名, 表格, 資料庫):
    from zhongwen.text import 臚列
    import pandas as pd
    import logging
    import sqlite3
    import re
    try:
        批次刪除(批號, 批號欄名, 表格, 資料庫)
    except sqlite3.OperationalError as e:
        logger.debug(f'批次刪除發生錯誤：{e}')
    logger.debug(f'整批寫入{批號}資料至{表格}……')
    try:
        資料.to_sql(表格, 資料庫, if_exists='append')
        logging.debug(f'寫入成功！')
    except sqlite3.OperationalError as e:
        df = pd.read_sql_query(f'select * from {表格} limit 1', 資料庫)
        寫入資料欄位 = 資料.columns.to_list()
        資料庫欄位 = df.columns.to_list()
        差異欄位 = set(寫入資料欄位) - set(資料庫欄位)
        logger.debug(f'寫入資料之{臚列(差異欄位)}等欄位，資料庫尚未建立……')
        cursor = 資料庫.cursor()
        for c in 差異欄位:
            alter_query = f'ALTER TABLE {表格} ADD COLUMN "{c}" INT'
            cursor.execute(alter_query)
        資料庫.commit()
        logger.debug('前開資料庫未建立欄位已新增……')
        資料.to_sql(表格, 資料庫, if_exists='append')
        logger.debug(f'寫入成功！')

def 期日資料批次寫入(資料庫檔, 資料名稱, 資料日期欄名, 預設資料日期組=[]):
    '''逐批寫入期日資料，資料日期一定為日期，即有year及month方法，舉如：
爬取損益表(資料日期組=迄每季(季末(2019, 1)))
會爬取自2019第1季至今每一季之損益表。
'''
    from collections.abc import Iterable
    from functools import wraps
    from sqlite3 import connect
    def 增加結果批次寫入(爬取期日資料函數):
        @wraps(爬取期日資料函數)
        def 批次寫入爬取資料(資料日期組=None, **kargs):
            if not 資料日期組:
                資料日期組 = 預設資料日期組
            if not isinstance(資料日期組, Iterable):
                資料日期組 = [資料日期組]
            with connect(資料庫檔) as db: 
                for 資料日期 in 資料日期組:
                    try:
                        資料日期.year
                        資料日期.month
                    except AttributeError:
                        raise TypeError(f'資料日期不為日期型態，而為{type(資料日期)}')
                    df = 爬取期日資料函數(資料日期)
                    批次寫入(df, 資料日期, 資料日期欄名, 資料名稱, db)
                return df
        return 批次寫入爬取資料
    return 增加結果批次寫入
    

def 結果批次寫入(資料庫檔, 資料名稱, 批號欄名, 預設批號組=[]):
    '''「批號組」指定一組批號逐批寫入查詢結果，舉如：
爬取損益表(批號組=迄每季(季末(2019, 1)))
會爬取自2019第1季至今每一季之損益表。
'''
    from collections.abc import Iterable
    from functools import wraps
    from sqlite3 import connect
    def 增加結果批次寫入(爬取資料函數):
        @wraps(爬取資料函數)
        def 批次寫入爬取資料(批號組=None, **kargs):
            if not 批號組:
                批號組 = 預設批號組
            if not isinstance(批號組, Iterable):
                批號組 = [批號組]
            with connect(資料庫檔) as db: 
                for 批號 in 批號組:
                    df = 爬取資料函數(批號)
                    批次寫入(df, 批號, 批號欄名, 資料名稱, db)
                return df
        return 批次寫入爬取資料
    return 增加結果批次寫入

class 批號存在錯誤(Exception):
    def __init__(self, 批號, 批號欄名, 表格):
        self.批號 = 批號
        self.批號欄名 = 批號欄名
        self.表格 = 表格

    def __str__(self):
        return f'批號【{self.批號}】已存在，請指定覆寫=True！'

def 載入批次資料(資料庫檔, 表格, 批次欄名, 時間欄位=None):
    '批次欄名'
    import pandas as pd
    import sqlite3
    with sqlite3.connect(資料庫檔) as c:
        sql = f"select distinct * from {表格}"
        try:
            df = pd.read_sql_query(sql, c, index_col='index', parse_dates=時間欄位) 
        except KeyError as e:
            logger.info(f'{表格}無 index 欄位！')
            df = pd.read_sql_query(sql, c, parse_dates=時間欄位) 
        return df

def 增加定期更新功能(更新頻率='每月十日之前'):
    '已廢棄請使用「增加定期更新」'
    import logging
    from pathlib import Path
    from diskcache import Cache
    cache = Cache(Path.home() / 'cache' / Path(__file__).stem)
    from warnings import warn
    warn(f'【增加定期更新功能】將廢棄，請使用【增加定期更新】', DeprecationWarning, stacklevel=2)
    def _增加按期更新查詢結果功能(查詢資料):
        from functools import wraps
        @wraps(查詢資料)
        def 查詢按期更新資料(*args, 更新=False,**kargs):
            if 更新頻率=='每月十日之前':
                from zhongwen.date import 今日 
                if 今日().day <= 10 or 更新:
                    df = 查詢資料(*args, **kargs)
                    cache.set(查詢資料.__name__, df)
                    return df
            return cache.read(查詢資料.__name__)
        return 查詢按期更新資料
    return _增加按期更新查詢結果功能

def 應更新資料時期(更新頻率='次月十日前'):
    from zhongwen.date import 今日, 上月
    if 更新頻率=='次月十日前':
        if 今日().day <= 10:
            return 上月()

def 解析更新期限(更新期限='次月10日前'):
    '解析更新期限，目前支援"次月10日前"、"次季45日前"、"次月底前"及"財報"等形式，傳回(應更新資料時期、應更新資料期限及定期更新資訊)'
    from zhongwen.date import  上年底, 上月, 上季, 今日, 月底, 取日期, 季別
    from zhongwen.date import  民國正式日期, 民國年月, 民國年, 民國季別
    from datetime import timedelta
    import re
    today = 今日()
    應更新資料時期, 應更新資料期限 = None, None

    if '財報' in 更新期限:
        '''證交所規定上市公司公告申報財務報表之期限如下：
    一、年度財務報告：每會計年度終了後3個月內(3/31前)。
    二、第一季、第二季、第三季財務報告：
    (一)一般公司(含投控公司)：每會計年度第1季、第2季及第3季終了後45日內(5/15、8/14、11/14前)。
    (二)保險公司：每會計年度第1季、第3季終了後1個月內(4/30、10/31前)，每會計年度第2季終了後2個月內(8/31前)。
    (三)金控、證券、銀行及票劵公司：每會計年度第1季、第3季終了後45日內(5/15、11/14前)，每會計年度第2季終了後2個月內(8/31前)。惟金控公司編製第1季、第3季財務報告時，若作業時間確有不及，應於每季終了後60日內(5/30、11/29前)補正。'''
        應更新資料時期 = 上季()
        _, 季數 = 季別(應更新資料時期)
        match 季數: 
            case 2:
                應更新資料期限 = 取日期(f'{應更新資料時期.year}.8.31')
            case 4:
                應更新資料期限 = 取日期(f'{應更新資料時期.year+1}.3.31')
            case _:
                應更新資料期限 = 應更新資料時期 + timedelta(days=45)
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國季別(應更新資料時期)}資訊。')
        

    if '次月' in 更新期限:
        應更新資料時期 = 上月()
    elif '次年' in 更新期限:
        應更新資料時期 = 上年底()
    elif '次季' in 更新期限:
        應更新資料時期 = 上季()

    pat = r'(\d+)(日|個月)(內|前)'
    if m:=re.search(pat, 更新期限):
        n = int(m[1])
        if m[2] == "日":
            應更新資料期限 = 應更新資料時期 + timedelta(days=n)
        elif m[2] == "個月":
            from datetime import datetime, timedelta
            import calendar
            data_date = 應更新資料時期 + timedelta(days=1)
            month = data_date.month-1
            year = data_date.year
            # breakpoint()
            # 計算2個月後的日期
            future_month = month + n
            if future_month > 12:
                future_month -= 12
                year += 1

            # 確定未來月份的天數
            _, days_in_future_month = calendar.monthrange(year, future_month)

            # 設定未來日期
            future_date = data_date.replace(year=year, month=future_month, day=max(data_date.day, days_in_future_month))

            應更新資料期限 = future_date
        if today.month == 2: # 因應2月初通常為春節假期，是以延長更新期限至2月底
            應更新資料期限 = 月底()

    pat = r'月底前'
    if m:=re.search(pat, 更新期限):
        應更新資料期限 = 月底()
    if '次月' in 更新期限:
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國年月(應更新資料時期)}資訊。')
    elif '次年' in 更新期限:
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國年(應更新資料時期)}資訊。')
    elif '次季' in 更新期限:
        return (應更新資料時期, 應更新資料期限, f'{民國正式日期()}應公布{民國季別(應更新資料時期)}資訊。')

def 增加定期更新(更新期限='次月10日前', 更新程序=解析更新期限):
    '''更新期限包含「次月10日前」、「次季45日前」及「次月底前」等。
查詢函數之參數「更新」設為True，則強制更新該批資料。
次季45日前係自季初連續45日更新上季資料，逾45日則停更，但實作上會延長3日作緩衝，防止公司遇假日未及更新。
'''
    import logging
    from pathlib import Path
    from functools import wraps
    from zhongwen.batch_data import 解析更新期限
    from zhongwen.date import 今日
    from datetime import timedelta
    緩衝期 = timedelta(days=3)
    def 增加定期更新功能(查詢資料):
        @wraps(查詢資料)
        def 查詢定期更新資料(*args, 更新=False,**kargs):
            資料時期, 公布期限, 資訊 = 解析更新期限(更新期限)
            if 更新 or (資料時期 < 今日() <= 公布期限 + 緩衝期):
                更新程序(資料時期)
            return 查詢資料()
        return 查詢定期更新資料
    return 增加定期更新功能

def 去除重覆(資料庫, 表格, 批號, 時間欄位=None):
    import sqlite3
    df = 載入批次資料(資料庫, 表格, 批號, 時間欄位)
    df = df.drop_duplicates()
    with sqlite3.connect(資料庫) as c:
        sql = f'drop table {表格}'
        c.execute(sql)
        c.commit()
        df.to_sql(表格, c)
    logger.info(f'{表格}去除重覆紀錄完成！') 
 
if __name__ == '__main__':
    pass
    from 股票分析.公開資訊觀測站爬蟲 import 股利分派資料庫
    # 去除重覆(股利分派資料庫, '股利分派表', '股東會召開年度', 時間欄位=['股利所屬年度'])
