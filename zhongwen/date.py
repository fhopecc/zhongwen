'日期處理'
import re
from datetime import date
from datetime import datetime

def 取日期(d, first=True):
    pat = r'\d{4}/\d{1,2}/\d{1,2}'
    if m:=re.match(pat, d):
        return datetime.strptime(m[0], '%Y/%m/%d')
    pat = r'\d{4}.\d{1,2}.\d{1,2}'
    if m:=re.match(pat, d):
        return datetime.strptime(m[0], '%Y.%m.%d')

    # 民國日期格式109/05/29
    pat = r'(\d{3})/(\d{1,2})/(\d{1,2})'
    if m:=re.match(pat, d):
        return datetime(int(m[1])+1911, int(m[2]), int(m[3]))

    # 民國日期格式109.05.29
    pat = r'(\d{3}).(\d{1,2}).(\d{1,2})'
    if m:=re.match(pat, d):
        return datetime(int(m[1])+1911, int(m[2]), int(m[3]))
    return d

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
