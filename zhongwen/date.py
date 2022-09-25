'日期處理'
import re
from datetime import date
from datetime import datetime
import pandas as pd

def 今日():
    return 取日期(datetime.now())

def 取日期(d, first=True, defaulttoday=True):
    match d:
        case datetime():
            return datetime(d.year, d.month, d.day)
        case str(d):
            # 省略年自動推論為今年
            pat = r'\d{1,2}([./])\d{1,2}'
            if m:=re.match(pat, d):
                year = datetime.now().year  
                od = d
                d = 取日期(f'{year}{m[1]}{d}')
                if d > datetime.now(): # 省略年推論為今年大於今日，則推論為去年
                    return 取日期(f'{year-1}{m[1]}{od}')
                return d
         
            pat = r'\d{4}([-./])\d{1,2}[-./]\d{1,2}'
            if m:=re.match(pat, d):
                s = m[1]
                return datetime.strptime(m[0], f'%Y{s}%m{s}%d')

            # 民國日期格式109/05/29
            pat = r'(\d{3})/(\d{1,2})/(\d{1,2})'
            if m:=re.match(pat, d):
                return datetime(int(m[1])+1911, int(m[2]), int(m[3]))

            # 民國日期格式109.05.29
            pat = r'(\d{3}).(\d{1,2}).(\d{1,2})'
            if m:=re.match(pat, d):
                return datetime(int(m[1])+1911, int(m[2]), int(m[3]))
            return d
        case _:
            if defaulttoday:
                d = datetime.now()    
                return datetime(d.year, d.month, d.day)
            raise TypeError(f'不支援類型[{type(d)}]、值[{d}]！')

def 上月():
    '上月'
    d = date.today()
    return f'{d.year-1911:03}{d.month-1:02}'

def 民國日期(d, fmt='%Y%m%d'):
    '%Y表年數、%m表月數前置0、%d表日數前置0、%M表月數不前置0'
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
