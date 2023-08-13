'日期處理'
from datetime import date, datetime, timedelta
from functools import lru_cache

def 是日期嗎(v):
    import pandas as pd
    return not pd.isnull(v) and (isinstance(v, date) or isinstance(v, datetime))

def 取過去日期(d):
    return 取日期(d, 日期大於今日省略年推論為去年=True)

def 取日期(d, 錯誤為空值=True, first=True, defaulttoday=True, default=None,
           日期大於今日省略年推論為去年=False) -> date:
    import re
    import pandas as pd
    if not default: 
        default=pd.NaT
    if pd.isnull(d):
        return pd.NaT
    match d:
        case float():
            return 取日期(f'{d:.0f}')
        case int():
            if d > 2_01_01:
                return 取日期(f'{d:07}')
            return 取日期(f'{d:05}')
        case datetime():
            return date(d.year, d.month, d.day)
        case date():
            return date(d.year, d.month, d.day)
        case str(d):
            # 省略日自動推論為月底
            pat = r'^(\d\d\d)(\d\d)$'
            if m:=re.match(pat, d):
                year = int(m[1]) + 1911
                mon = int(m[2])
                import calendar
                _, last_day = calendar.monthrange(year, mon)
                return date(year, mon, last_day)
            # 省略年自動推論為今年
            pat = r'(\d{1,2})([./])\d{1,2}'
            if m:=re.match(pat, d):
                if int(m[1]) <= 12: 
                    year = datetime.now().year  
                    od = d
                    sep = m[2]
                    d = 取日期(f'{year}{sep}{d}')
                    if 日期大於今日省略年推論為去年 and d > datetime.now().date(): 
                        # 省略年推論為今年大於今日，則推論為去年
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

@lru_cache()
def 上月() -> date:
    '上月底'
    return 今日().replace(day=1) - timedelta(days=1)

@lru_cache()
def 上上月() -> date:
    '上月底'
    return 上月().replace(day=1) - timedelta(days=1)

def 民國日期(d, fmt='%Y%m%d', 昨今明表達=False):
    '%Y表年數、%m表月數前置0、%d表日數前置0、%M表月數不前置0'
    from datetime import timedelta
    d = 取日期(d)
    import pandas as pd
    if pd.isnull(d):
        return ''
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
            ).replace(
            '%D', '%(date)d'
            )

    year = d.year-1911
    return fmt % {"year":year, "month":d.month, "date":d.day}

def 公文日期(d):
    '格式如：112年7月29日'
    return 民國日期(d, "%Y年%M月%d日")

def 民國月份(d):
    '格式如：112年7月'
    return 民國日期(d, "%Y年%M月")

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

def 上年底() -> date:
    d = 今日()
    return d.replace(year=d.year-1, month=12, day=31)

def 季別(日期=今日()) -> (int, int):
    '指定日期之季數，以(年數, 季數)表達。'
    d = 日期
    if 1 <= d.month <= 3: return (d.year, 1)
    if 4 <= d.month <= 6: return (d.year, 2)
    if 7 <= d.month <= 9: return (d.year, 3)
    if 10 <= d.month <= 12: return (d.year, 4)

def 季數(日期=今日()):
    from warnings import warn
    warn(f'配合證交所資料項目名稱，【季數】將廢棄，請使用【季別】', DeprecationWarning, stacklevel=2)
    return 季別(日期)


def 季初(年數, 季數) -> date:
    '指定季之最初日'
    match 季數:
        case 1: return date(年數,  1, 1)
        case 2: return date(年數,  4, 1)
        case 3: return date(年數,  7, 1)
        case 4: return date(年數, 10, 1)

def 季末(年數或日數=None, 季別=None):
    '指定季之最末日，未指定為本季'
    _季數 = 季別
    if 是日期嗎(年數或日數):
        年數, _季數 = 季數(年數或日數)
    else:
        if not 年數或日數 or not _季數:
            年數, _季數 = 季數()
        else:
            年數=年數或日數 
    match _季數:
        case 1: return date(年數, 3, 31)
        case 2: return date(年數, 6, 30)
        case 3: return date(年數, 9, 30)
        case 4: return date(年數, 12, 31)

def 本季初():
    return 季初(*季數()) 

def 上季數() -> (int, int):
    '上季數之(年數, 季數)。'
    return 季數(本季初()-timedelta(days=1))

def 上季初():
    return 季初(*上季數())

def 月末(日期或年數=None, 月數=None):
    '預設為本月末'
    年數 = 日期或年數
    if not 日期或年數:
        年數=今日().year
    if not 月數:
        月數=今日().month
    if 是日期嗎(日期或年數):
        年數=日期或年數.year
        月數=日期或年數.month
    import calendar
    月末日數 = calendar.monthrange(年數, 月數)[1]
    return date(年數, 月數, 月末日數)

def 與季末相距月數(日期):
    from dateutil.relativedelta import relativedelta
    return relativedelta(季末(日期), 日期).months

def 月起迄(year, mon):
    月初 = date(year, mon, 1)
    return [月初, 月末(year, mon)]

def 前幾月(月數):
    from dateutil.relativedelta import relativedelta
    return 今日() - relativedelta(months=月數)

def 近幾個月底(月數):
    import pandas as pd
    start = 前幾月(月數)
    end = 今日()
    curdate = 月末(start)
    while curdate <= end:
        yield curdate
        curdate += timedelta(days=1)
        curdate = 月末(curdate)

def 前幾季(季數):
    from dateutil.relativedelta import relativedelta
    return 今日() - relativedelta(months=季數*3)

def 近幾季(季數):
    import pandas as pd
    start = 前幾季(季數)
    end = 今日()
    curdate = 季末(start)
    while curdate <= end:
        yield curdate
        curdate += timedelta(days=1)
        curdate = 季末(curdate)

def 民國年月(日期):
    '日期格式如112年8月'
    return 民國日期(日期, '%Y年%M月')

if __name__ == '__main__':
    for 月 in 近幾個月底(112):
        print(月)
