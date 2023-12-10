
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
    import logging
    logging.debug(f'批次刪除{批號}、{表格}……')
    c = 資料庫.cursor()
    sql = f'delete from {表格} where {批號欄名}=="{批號}"'
    c.execute(sql)
    資料庫.commit()
    logging.debug(f'成功')

def 批次寫入(資料, 批號, 批號欄名, 表格, 資料庫):
    from zhongwen.text import 臚列
    import pandas as pd
    import logging
    import sqlite3
    import re
    try:
        批次刪除(批號, 批號欄名, 表格, 資料庫)
    except sqlite3.OperationalError as e:
        logging.debug(f'批次刪除發生錯誤：{e}')
    logging.debug(f'批次寫入{批號}批號資料至{表格}……')
    try:
        資料.to_sql(表格, 資料庫, if_exists='append')
        logging.debug(f'寫入成功！')
    except sqlite3.OperationalError as e:
        df = pd.read_sql_query(f'select * from {表格} limit 1', 資料庫)
        寫入資料欄位 = 資料.columns.to_list()
        資料庫欄位 = df.columns.to_list()
        差異欄位 = set(寫入資料欄位) - set(資料庫欄位)
        logging.debug(f'寫入資料之{臚列(差異欄位)}等欄位，資料庫尚未建立……')
        cursor = 資料庫.cursor()
        for c in 差異欄位:
            alter_query = f'ALTER TABLE {表格} ADD COLUMN "{c}" INT'
            cursor.execute(alter_query)
        資料庫.commit()
        logging.debug('前開資料庫未建立欄位已新增……')
        資料.to_sql(表格, 資料庫, if_exists='append')
        logging.debug(f'寫入成功！')

def 結果批次寫入(資料庫檔, 資料名稱, 批號欄名, 預設批號組=[]):
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
        sql = f"select * from {表格}"
        df = pd.read_sql_query(sql, c, index_col='index', parse_dates=時間欄位) 
        return df
