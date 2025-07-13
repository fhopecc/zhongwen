from pathlib import Path
import pandas as pd
import logging
from zhongwen.date import 全是日期嗎

logger = logging.getLogger(Path(__file__).stem)

def 取日期(日期=None):
    from zhongwen.date import 取日期
    if not 日期:
        return pd.Timestamp.today().normalize()
    return 取日期(日期)

def 取期間(期間, 全取=False):
    '指定全取則回傳期間串列，否則傳為首個期間'
    from zhongwen.文 import 刪空格
    from pandas import Period
    import re

    if isinstance(期間, Period):
        return 期間
    elif isinstance(期間, int):
        s = str(期間)
    elif isinstance(期間, str):
        s = 刪空格(期間)
    else:
        logger.error(f'期間型態必須為字串、期間或整數，而非{type(期間)}！')
        return pd.NaT

    if ms:=re.findall(r'(\d{4})([01]\d)', s):
        ps = [Period(f'{int(m[0])}{int(m[1]):02}', 'M') for m in ms]
    elif ms:=re.findall(r'(\d{4})-([01]?\d)', s):
        ps = [Period(f'{int(m[0])}{int(m[1]):02}', 'M') for m in ms]
    elif qs:=re.findall(r'\d{4}Q[1234]', s):
        ps = [Period(q) for q in qs]
    elif ms:=re.findall(r'(?<=\A)(?P<Y1>\d{4})(?=(\D|\Z))|(?<=\D)(?P<Y2>\d{4})(?=(\D|\Z))', s):
        取年數 = lambda t: next((s for s in t if isinstance(s, str) and s.strip()), None)
        ps = [Period(f'{int(取年數(m))}', 'Y') for m in ms]
    elif ms:=re.findall(r'(\d{3})[/]?([01]?\d)', s):
        try:
            ps = [Period(f'{int(m[0])+1911}{int(m[1]):02}', 'M') for m in ms]
        except Exception:
            raise Exception(f"'{期間字串}'無法解析為期間字串！")
    elif ms:=re.findall(r'(\d{2,3})年度', s):
        ps = [Period(f'{int(m)+1911}', 'Y') for m in ms]
    elif ms:=re.findall(r'(\d{2,3})年第([1-4])季', s):
        ps = [Period(f'{int(m[0])+1911}Q{m[1]}', 'Q') for m in ms]
    elif ms:=re.findall(r'(\d{2,3})年([前後])半年度', s):
        取半年開始月數 = lambda 期間: 1 if 期間=='前' else 7
        ps = [Period(f'{int(m[0])+1911}-{取半年開始月數(m[1])}', '6M') for m in ms]
    elif ms:=re.findall(r'(\d{2,3})年([上下])半年', s):
        取半年開始月數 = lambda 期間: 1 if 期間=='上' else 7
        ps = [Period(f'{int(m[0])+1911}-{取半年開始月數(m[1])}', '6M') for m in ms]
    elif ms:=re.findall(r'(\d{2,3})年年度', s):
        ps = [Period(f'{int(m)+1911}', 'Y') for m in ms]
    elif ms:=re.findall(r'(?<=\A)(?P<Y1>\d{3})(?=(\D|\Z))|(?<=\D)(?P<Y2>\d{3})(?=(\D|\Z))', s):
        取年數 = lambda t: next((s for s in t if isinstance(s, str) and s.strip()), None)
        ps = [Period(f'{int(取年數(m))+1911}', 'Y') for m in ms]
 
    if 全取: return ps
    
    try:
        return ps[0]
    except UnboundLocalError:
        logger.error(f"'{期間}'無法解析為期間！")
        return pd.NaT

def 取民國期間(期間):
    p = 取期間(期間)
    if 'Y' in p.freqstr: 
        return f'{p.year-1911}年度'
    elif 'Q' in p.freqstr: 
        return f'{p.year-1911}年第{p.quarter}季'
    elif '6M' in p.freqstr: 
        return f'{p.year-1911}年前半年度' if 1 <= p.month <= 6 else f'{p.year-1911}年後半年度'
    return str(期間)

def 取年底():
    return 取日期(f'{取今日().year}1231')

def 取上年底():
    return 上年度().end_time.normalize()

def 取一年前():
    return 取今日() - pd.DateOffset(years=1)

def 取二年前():
    import pandas as pd
    return 取今日() - pd.DateOffset(years=2)

def 取五年前():
    import pandas as pd
    return 取今日() - pd.DateOffset(years=5)

def 取前年至次年間(取樣頻率='ME'):
    '取樣頻率預設為 ME 即期間內各月底，另可設為 QE 即各季末、YE 即各年底、MS 即各月初等。'
    import pandas as pd
    今年數 = 今日.year
    前年數 = 今年數-1
    次年數 = 今年數+1
    return pd.date_range(f'{前年數}0131', f'{次年數}1231', freq=取樣頻率)

def 取季別名(季別):
    try:
        return f'{季別.year}年第{季別.quarter}季'
    except Exception:
        return 季別

def 取本年度():
    '取表示本年度之整數，如碼本函數時為 2024 年，即傳回整數 2024。'
    return 今日.year

def 取上年度():
    import pandas as pd
    return pd.Period(今日, 'Y') - 1

def 取民國日期(日期=None, 格式='%Y%m%d', 昨今明表達=False):
    '%Y表年數、%m表月數前置0、%d表日數前置0、%M表月數不前置0'
    import pandas as pd
    d = 取日期(日期)
    fmt = 格式

    if not d: d = 今日()
    if pd.isnull(d):
        return ''
    if 昨今明表達:
        if d == 今日()-Timedelta(days=1):
            return '昨'
        if d == 今日():
            return '今'
        if d == 今日()+Timedelta(days=1):
            return '明'
        if d == 今日()+Timedelta(days=2):
            return '後天'

    fmt = fmt.replace(
            '%Y', '%(year)03d'
            ).replace(
            '%m', '%(month)02d'
            ).replace(
            '%M', '%(month)d'
            ).replace(
            '%d', '%(date)02d'
            ).replace(
            '%D', '%(date)d'
            )

    year = d.year-1911
    return fmt % {"year":year, "month":d.month, "date":d.day}

def 取民國月份(時間):
    '取民國113年11月之表達字串113年11月'
    return 取民國日期(時間, 格式='%Y年%M月')


def 取民國年度(日期=None):
    '以形式如【113年度】表達期間'
    return 取民國日期(日期, 格式='%Y年度')

def 取民國年數(日期=None):
    '日期民國113年1月1日取表達整數113，預設為今日'
    d = 取日期(日期)
    return d.year - 1911

def 取正式民國日期(d=None):
    '格式如：112年7月29日'
    import pandas as pd
    if not d:
        d = 今日
    if isinstance(d, pd.Period):
        d = d.end_time.normalize()
    return 取民國日期(d, "%Y年%M月%D日")

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
    while 季別 <= 上季:
        yield 季別
        季別+=1
    return 上季

def 去年同期(期間):
    import pandas as pd
    p = 期間
    if 'Q' in p.freqstr:
        return pd.Period(year=p.year-1, quarter=p.quarter, freq=p.freq)
    elif 'M' in p.freqstr:
        return pd.Period(year=p.year-1, month=p.month, freq=p.freq)
 
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
    while curdate <= 今日:
        yield curdate
        curdate += Timedelta(days=1)

def 自起始年底按年列舉至本年底(起始年度):
    import pandas as pd
    起始年度 = 取期間(起始年度).year
    本年度 = 取本年度()
    ps = pd.date_range(f'{起始年度}1231', f'{本年度}1231', freq='YE')
    return list(ps)

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


def 正式民國日期(d=None):
    return 取正式民國日期(d)

def 取民國年月(年月):
    '取如民國113年11月之表達字串11311'
    return 取民國日期(年月, 格式='%Y%m')

def 取季別年數季數(季別):
    季別 = 取期間(季別)
    return 季別.year, 季別.quarter

今日 = 取日期()
今年數 = 今日.year
民國年數 = 今年數-1911
年底 = 取日期(f"{今日.year}.12.31")
年初 = 取日期(f"{今日.year}.1.1")
最近工作日 = pd.offsets.BDay().rollback(今日)
昨日 = 今日 - pd.Timedelta(days=1)
一週前 = 今日 - pd.Timedelta(days=7)
半月前 = 今日 - pd.Timedelta(days=14)
一季前 = 今日 - pd.DateOffset(months=3)
半年前 = 今日 - pd.DateOffset(months=6)
一年前 = 今日 - pd.DateOffset(years=1)
五年又一個月前 = 今日 - pd.DateOffset(months=61)
本月 = pd.Period(今日, 'M')
上月 = 本月 - 1
本季 = pd.Period(今日, 'Q-DEC')
上季 = 本季 - 1
上季末 = 上季.end_time.normalize()
季初 = 本季.start_time.normalize()
季末 = 本季.end_time.normalize()
本年度 = pd.Period(今日, 'Y')
上年度 = 本年度 - 1
