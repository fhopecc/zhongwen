from zhongwen.date import 取日期
from zhongwen.date import 今日, 年底, 上年底
from zhongwen.date import 民國日期, 民國年月
from zhongwen.date import 自起日按日列舉迄今

def 正式民國日期(d=None):
    '格式如：112年7月29日'
    if not d:
        d = 今日()
    return 民國日期(d, "%Y年%M月%D日")

def 上月():
    import pandas as pd
    return pd.Period(今日(), 'M') - 1

def 上年度():
    import pandas as pd
    return pd.Period(今日(), 'Y') - 1

def 自指定月份迄上月(月份):
    from pandas import Period
    月份 = 取期間(月份)
    while 月份 <= 上月():
        yield 月份
        月份+=1
    return 上月()

def 取期間(期間字串, 全取=False):
    '指定全取則回傳期間串列，否則傳為首個期間'
    from pandas import Period
    import re

    s = 期間字串
    if ms:=re.findall(r'(\d{4})-([01]?\d)', s):
        ps = [Period(f'{int(m[0])}{int(m[1]):02}', 'M') for m in ms]
    elif ms:=re.findall(r'(\d{3})[/]?([01]?\d)', s):
        try:
            ps = [Period(f'{int(m[0])+1911}{int(m[1]):02}', 'M') for m in ms]
        except Exception:
            raise Exception(f"'{期間字串}'無法解析為期間字串！")
   
    if 全取: return ps
    
    try:
        return ps[0]
    except UnboundLocalError:
        raise UnboundLocalError(f"'{期間字串}'無法解析為期間字串！")
