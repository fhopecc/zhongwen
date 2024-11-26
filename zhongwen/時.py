from zhongwen.date import 取日期
from zhongwen.date import 今日, 季末, 年底, 本年度, 上年底
from zhongwen.date import 民國日期, 民國年月
from zhongwen.date import 自起日按日列舉迄今

def 本年數():
    return 今日().year

def 正式民國日期(d=None):
    '格式如：112年7月29日'
    if not d:
        d = 今日()
    return 民國日期(d, "%Y年%M月%D日")

def 上月():
    import pandas as pd
    return pd.Period(今日(), 'M') - 1

def 上季():
    import pandas as pd
    return pd.Period(今日(), 'Q-DEC') - 1

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

def 自指定季別迄上季(始季):
    from pandas import Period
    季別 = 取期間(始季)
    while 季別 <= 上季():
        yield 季別
        季別+=1
    return 上季()

def 去年同期(期間):
    import pandas as pd
    p = 期間
    if 'Q' in p.freqstr:
        return pd.Period(year=p.year-1, quarter=p.quarter, freq=p.freq)
    elif 'M' in p.freqstr:
        return pd.Period(year=p.year-1, month=p.month, freq=p.freq)
    
def 取期間(期間字串, 全取=False):
    '指定全取則回傳期間串列，否則傳為首個期間'
    from pandas import Period
    import re
    if isinstance(期間字串, Period):
        return 期間字串
    s = 期間字串
    if ms:=re.findall(r'(\d{4})-([01]?\d)', s):
        ps = [Period(f'{int(m[0])}{int(m[1]):02}', 'M') for m in ms]
    elif qs:=re.findall(r'\d{4}Q[1234]', s):
        ps = [Period(q) for q in qs]
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

class 無法於一階差分內穩定(Exception):pass
def 取穩定階數(時序):
    '回傳是否穩定及穩定差分階數'
    from statsmodels.tools.sm_exceptions import ConvergenceWarning
    from 股票分析.股票基本資料分析 import 查股票代號
    from statsmodels.tsa.stattools import adfuller
    import warnings

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=ConvergenceWarning)

    ts = 時序
    try:
        _, pvalue, *_ = adfuller(ts)
        if pvalue < 0.05:
            return 0
        else:
            _, pvalue, *_ = adfuller(ts.diff().dropna())
            if pvalue < 0.05:
                return 1
            raise 無法於一階差分內穩定()
    except ValueError:
        raise 無法於一階差分內穩定('樣本數僅{len(ts)}太少。')

def 自起日按日列舉迄今(起日):
    from pandas import Timedelta
    curdate = 取日期(起日)
    while curdate <= 今日():
        yield curdate
        curdate += Timedelta(days=1)

def 全年期別分割(分割期別):
    import pandas as pd
    p = 分割期別
    # p = pd.Period('2024Q3', freq='Q-DEC')
    if p.freqstr == 'Q-DEC':
        ps = pd.period_range(p-p.quarter+1, p, freq=p.freq)
        rps = pd.period_range(p+1, p+(4-p.quarter), freq=p.freq)
    elif p.freqstr == '6M':
        ps = pd.period_range(p-(round(p.month/6))+1, p, freq=p.freq)
        rps = pd.period_range(p+1, p+(2-round(p.month/6)), freq=p.freq)
    elif p.freqstr == 'Y-DEC':
        ps = [p]
        rps = []
    return ps, rps
