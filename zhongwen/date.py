'日期處理'
from datetime import date
from functools import lru_cache

def 取日數(期間):
    try:
        return 期間.days
    except:
        return float('nan')

def 是日期嗎(v):
    from datetime import datetime
    import pandas as pd
    return not pd.isnull(v) and (isinstance(v, date) or isinstance(v, datetime))

def 取過去日期(d):
    return 取日期(d, 日期大於今日省略年推論為去年=True)

def 昨日():
    from datetime import datetime, timedelta
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    return yesterday.date()

def 取日期(d, 錯誤為空值=True, first=True, defaulttoday=True, default=None,
           日期大於今日省略年推論為去年=False) -> date:
    import re
    import pandas as pd
    from datetime import datetime, timedelta
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
            pat = r'^昨日?$'
            if m:=re.match(pat, d):
                return 昨日()
            # 省略日自動推論為月底
            pat = r'^(\d\d\d)(\d\d)$'
            if m:=re.match(pat, d):
                year = int(m[1]) + 1911
                mon = int(m[2])
                import calendar
                _, last_day = calendar.monthrange(year, mon)
                return date(year, mon, last_day)
            # 省略年自動推論為今年
            pat1 = r'(\d{1,2})([./])\d{1,2}'
            pat2 = r'^(\d\d)()(\d\d)$' # 中間空白括號是表達日期分隔為空字元
            if m:=(re.match(pat1, d) or re.match(pat2, d)):
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

            # 民國日期形式如980731, 1110527。
            pat = r'(\d{2,3})(\d{2})(\d{2})'

            # 民國日期其形式如 109/05/29 、109.05.29及109-5-29 等。
            pat = r'(\d{2,3})[-./](\d{1,2})[-./](\d{1,2})'
            if m:=re.match(pat, d):
                return datetime(int(m[1])+1911, int(m[2]), int(m[3])).date()

            pat = r'民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日'
            if m:=re.match(pat, d):
                try:
                    return date(int(m[1])+1911, int(m[2]), int(m[3]))
                except ValueError: return pd.NaT
            pat = r'(\d+)年\D*(\d+)月'
            if m:=re.match(pat, d):
                try:
                    return 月末(date(int(m[1])+1911, int(m[2]), 1))
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
    from datetime import timedelta
    return 今日().replace(day=1) - timedelta(days=1)

@lru_cache()
def 上上月() -> date:
    '上月底'
    from datetime import timedelta
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

def 年底() -> date:
    d = 今日()
    return d.replace(month=12, day=31)

def 季別(日期=今日()) -> (int, int):
    '指定日期之季數，以(年數, 季數)表達，未指定為今日歸屬季別'
    d = 日期
    if 1 <= d.month <= 3: return (d.year, 1)
    if 4 <= d.month <= 6: return (d.year, 2)
    if 7 <= d.month <= 9: return (d.year, 3)
    if 10 <= d.month <= 12: return (d.year, 4)

def 季數(日期=今日()):
    from warnings import warn
    warn(f'配合證交所資料項目名稱，【季數】將廢棄，請使用【季別】', DeprecationWarning, stacklevel=2)
    return 季別(日期)

def 季初(年數或日期=None, 季別參數=None) -> date:
    '指定季之最初日，未指定為本季'
    y, q = 季別()
    if 是日期嗎(年數或日期):
        d = 年數或日期
        y, q = 季別(d)
    if 年數或日期 and 季別參數:
        y = 年數或日期 
        q = 季別參數
    match q:
        case 1: return date(y,  1, 1)
        case 2: return date(y,  4, 1)
        case 3: return date(y,  7, 1)
        case 4: return date(y, 10, 1)
    raise ValueError(f'年數或日期值「{年數或日期}」及季別參數值「{季別參數}」係錯誤值！')

def 季末(年數或日期=None, 季別參數=None):
    '指定季之最末日，未指定為本季末'
    y, q = 季別()
    if 是日期嗎(年數或日期):
        d = 年數或日期
        y, q = 季別(d)
    if 年數或日期 and 季別參數:
        y = 年數或日期 
        q = 季別參數
    match q:
        case 1: return date(y, 3, 31)
        case 2: return date(y, 6, 30)
        case 3: return date(y, 9, 30)
        case 4: return date(y, 12, 31)

def 本季初():
    from warnings import warn
    warn(f'【季初】無參數即為本季初，原【本季初】函數將廢棄！', DeprecationWarning, stacklevel=2)
    return 季初() 

def 上季數() -> (int, int):
    '上季數之(年數, 季數)。'
    from datetime import timedelta
    return 季別(本季初()-timedelta(days=1))

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

def 與年底相距月數(日期):
    from dateutil.relativedelta import relativedelta
    return relativedelta(年底(), 日期).months

def 月起迄(year, mon):
    月初 = date(year, mon, 1)
    return [月初, 月末(year, mon)]

def 前幾月(月數):
    from dateutil.relativedelta import relativedelta
    return 今日() - relativedelta(months=月數)

def 近幾個月底(月數):
    from datetime import timedelta
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
    return 季末(今日() - relativedelta(months=季數*3))

def 上季():
    from dateutil.relativedelta import relativedelta
    return 前幾季(1)

def 近幾季(季數):
    from datetime import timedelta
    start = 前幾季(季數)
    end = 今日()
    curdate = 季末(start)
    while curdate <= end:
        yield curdate
        curdate += timedelta(days=1)
        curdate = 季末(curdate)

def 迄每季(起季):
    '自起季迄每季'
    from datetime import timedelta
    end = 今日()
    curdate = 季末(起季)
    while curdate <= end:
        yield curdate
        curdate += timedelta(days=1)
        curdate = 季末(curdate)

def 民國年月(日期):
    '日期格式如112年8月'
    return 民國日期(日期, '%Y年%M月')

def 學期(日期=None):
    if not 日期:
        日期=今日()
    學年度 = 日期.year-1911
    if 1 < 日期.month < 7:
        學年度-=1
        return f'{學年度}年下'
    return f'{學年度}年上'

def 應公布財報季別(公司類型='一般公司') -> (int, int):
    '''傳回目前應公布財報年數及季別數組，
一般公司最近一次應公布財報年季。
證交所規定上市公司公告申報財務報表之期限如下：
一、年度財務報告：每會計年度終了後3個月內(3/31前)。
二、第一季、第二季、第三季財務報告：
(一)一般公司(含投控公司)：每會計年度第1季、第2季及第3季終了後45日內(5/15、8/14、11/14前)。
(二)保險公司：每會計年度第1季、第3季終了後1個月內(4/30、10/31前)，每會計年度第2季終了後2個月內(8/31前)。
(三)金控、證券、銀行及票劵公司：每會計年度第1季、第3季終了後45日內(5/15、11/14前)，每會計年度第2季終了後2個月內(8/31前)。惟金控公司編製第1季、第3季財務報告時，若作業時間確有不及，應於每季終了後60日內(5/30、11/29前)補正。'''
    日期 = 今日()
    年 = 今日().year
    q1 = date(年, 5, 15)
    q2 = date(年, 8, 14)
    q3 = date(年, 11, 14)
    q4 = date(年, 3, 31)
    if q4 <= 日期 < q1 :
        年 = 年-1
        季 = 4
    elif q1 < 日期 < q2:
        季 = 1
    elif q2 < 日期 <= q3:
        季 = 2
    elif q3 <= 今日():
        季 = 3
    elif 今日() < q4:
        年 = 年-1
        季 = 3
    return 年, 季 

if __name__ == '__main__':
    for 月 in 近幾個月底(112):
        print(月)
