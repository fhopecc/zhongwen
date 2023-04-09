'日期處理'
import re
from datetime import date, datetime, timedelta
import pandas as pd


def 取日期(d, 錯誤為空值=True, first=True, defaulttoday=True, default=None) -> date:
    match d:
        case float():
            return 取日期(f'{d:.0f}')
        case int():
            return 取日期(f'{d:07}')
        case datetime():
            return date(d.year, d.month, d.day)
        case date():
            return date(d.year, d.month, d.day)
        case str(d):
            # 省略年自動推論為今年
            pat = r'(\d{1,2})([./])\d{1,2}'
            if m:=re.match(pat, d):
                if int(m[1]) <= 12: 
                    year = datetime.now().year  
                    od = d
                    sep = m[2]
                    d = 取日期(f'{year}{sep}{d}')
                    if d > datetime.now().date(): # 省略年推論為今年大於今日，則推論為去年
                        return 取日期(f'{year-1}{sep}{od}')
                    return d
         
            # 日期2022/5/27
            pat = r'\d{4}([-./])\d{1,2}[-./]\d{1,2}'
            if m:=re.match(pat, d):
                s = m[1]
                try:
                    return datetime.strptime(m[0], f'%Y{s}%m{s}%d').date()
                except:breakpoint()

            # 日期20220527
            pat = r'\d{4}\d{2}\d{2}'
            if m:=re.match(pat, d):
                return datetime.strptime(m[0], f'%Y%m%d').date()
 
            # 民國日期帶增減日數形式，如【111.4.29+150】。
            pat = r'(\d{2,3})[-./](\d{1,2})[-./](\d{1,2})([+])(\d+)'
            if m:=re.match(pat, d):
                d = datetime(int(m[1])+1911, int(m[2]), int(m[3]))+timedelta(days=int(m[5]))
                return d.date()

            # 民國日期形式如980731, 1110527。
            pat = r'(\d{2,3})(\d{2})(\d{2})'
            if m:=re.match(pat, d):
                try:
                    return datetime(int(m[1])+1911, int(m[2]), int(m[3])).date()
                except ValueError as e: 
                    if 錯誤為空值: return pd.NaT
                    raise ValueError(f'【{d}】引發例外{e}！')

            # 民國日期其形式如 109/05/29 、109.05.29及109-5-29 等。
            pat = r'(\d{2,3})[-./](\d{1,2})[-./](\d{1,2})'
            if m:=re.match(pat, d):
                return datetime(int(m[1])+1911, int(m[2]), int(m[3])).date()

            pat = r'民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日'
            if m:=re.match(pat, d):
                try:
                    return date(int(m[1])+1911, int(m[2]), int(m[3]))
                except ValueError: return pd.NaT

            if default: return default 
            return d
        case _:
            if defaulttoday:
                d = datetime.now()    
                return datetime(d.year, d.month, d.day)
            raise TypeError(f'不支援類型[{type(d)}]、值[{d}]！')

def 上月():
    d = date.today()
    return f'{d.year-1911:03}{d.month-1:02}'

def 民國日期(d, fmt='%Y%m%d', 昨今明表達=False):
    '%Y表年數、%m表月數前置0、%d表日數前置0、%M表月數不前置0'

    from datetime import timedelta
    d = 取日期(d)
    if 昨今明表達:
        if d == 今日()-timedelta(days=1):
            return '昨'
        if d == 今日():
            return '今'
        if d == 今日()+timedelta(days=1):
            return '明'
        if d == 今日()+timedelta(days=2):
            return '後天'

    fmt = fmt.replace(
            '%Y', '%(year)03d'
            ).replace(
            '%m', '%(month)02d'
            ).replace(
            '%M', '%(month)d'
            ).replace(
            '%d', '%(date)02d'
            )
    year = d.year-1911
    return fmt % {"year":year, "month":d.month, "date":d.day}

def 經過日數(起, 迄):
    起=取日期(起)
    迄=取日期(迄)
    return (迄-起).days

def 約年(日數):
    return f'{日數/365:0.0f}年餘'

def 逾(起, 迄):
    return f'逾{約年(r(end) - r(start))}'

def 上年度():
    d = date.today()
    return f'{d.year-1911-1}年度'

def 本年度():
    d = date.today()
    return f'{d.year-1911}年度'

def 上上年度():
    d = date.today()
    return f'{d.year-1911-2}年度'

def 今日() -> date:
    return date.today()

def 上年() -> date:
    d = 今日()
    return d.replace(year=d.year-1)

def 季數(日期=今日()) -> (int, int):
    d = 日期
    if 1 <= d.month <= 3: return (d.year, 1)
    if 4 <= d.month <= 6: return (d.year, 2)
    if 7 <= d.month <= 9: return (d.year, 3)
    if 10 <= d.month <= 12: return (d.year, 4)

def 季初(年數, 季數) -> date:
    '指定季之最初日'
    match 季數:
        case 1: return date(年數,  1, 1)
        case 2: return date(年數,  4, 1)
        case 3: return date(年數,  7, 1)
        case 4: return date(年數, 10, 1)

def 季末(年數, 季數):
    '指定季之最末日'
    match 季數:
        case 1: return date(年數, 3, 31)
        case 2: return date(年數, 6, 30)
        case 3: return date(年數, 9, 30)
        case 4: return date(年數, 12, 31)

def 月末(年數, 月數):
    import calendar
    月末日數 = calendar.monthrange(年數, 月數)[1]
    return date(年數, 月數, 月末日數)

def 月起迄(year, mon):
    月初 = date(year, mon, 1)
    return [月初, 月末(year, mon)]



