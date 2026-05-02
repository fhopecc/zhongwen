from pathlib import Path
import pandas as pd
import logging
from zhongwen.date import 全是日期嗎

logger = logging.getLogger(Path(__file__).stem)

def 取日期(日期=None, 傳回全部日期=False, 包含位置=False):
    '''
    一、解析輸入字串所有日期字串並傳回 pd.Timestamp.normalize()，即不包含時間之日期。
    二、預設傳回第一個日期 pd.Timestamp，但可指定「傳回全部日期」參數，傳回所有日期 list。
    四、可指定含字串位置選項，就回傳成(日期, 起, 迄) list。
    五、支援日期格式如次：
        2026.5.2
        2026/5/2
        2026-5-2
        20260502
        2026年5月2日
    六、支援包含星期格式：
        2026/5/2 Sat
        2026/5/2 週五
    七、支援民國年：
        115.5.2 -> 2026.5.2
        115年5月2日 -> 2026.5.2
        0680729 -> 1979.7.29
    八、解析輸入數字之字串表達之日期字串，如20260502整數就解成 2026.5.2
    九、解析輸入 date, datetime, Timestamp 等類日期物件，就回傳其對應之 Timestamp。
'''
    """
    解析輸入字串或物件中的日期。
    """
    import re
    import pandas as pd
    from datetime import date, datetime
    input_data, return_all, include_position = 日期, 傳回全部日期, 包含位置
    if input_data is None:
        return pd.Timestamp.now().normalize()

    # 處理已經是日期物件的情況 (需求九)
    if isinstance(input_data, (date, datetime, pd.Timestamp)):
        ts = pd.Timestamp(input_data).normalize()
        result = (ts, 0, 0) if include_position else ts
        return [result] if return_all else result

    if not isinstance(input_data, str):
        input_data = str(input_data)

    # 正規表達式設定
    # 1. 支援 2026.5.2, 2026/5/2, 2026-5-2, 2026年5月2日, 115.5.2 等
    # 2. 支援包含星期 (Sat, 週五)
    # 3. 支援純數字 20260502 或 0680729
    pattern = re.compile(r"""
        (\d{2,4})                     # 年份 (民國或西元)
        [\.\-/年]                     # 分隔符
        (\d{1,2})                     # 月
        [\.\-/月]                     # 分隔符
        (\d{1,2})日?                  # 日
        (?:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri|週[一二三四五六日]))? # 星期(選填)
        |
        (?<!\d)(\d{7,8})(?!\d)         # 純數字格式 (如 20260502 或 0680729)
    """, re.X)

    results = []

    for match in pattern.finditer(input_data):
        groups = match.groups()
        start, end = match.span()
        
        try:
            if groups[3]:  # 處理純數字格式 (如 20260502)
                s = groups[3]
                if len(s) == 7: # 民國 0680729
                    y, m, d = int(s[:3]) + 1911, int(s[3:5]), int(s[5:])
                else: # 西元 20260502
                    y, m, d = int(s[:4]), int(s[4:6]), int(s[6:])
            else: # 處理帶分隔符的格式
                y = int(groups[0])
                m = int(groups[1])
                d = int(groups[2])
                if y < 1000: # 民國年轉換
                    y += 1911
            
            # 轉為 Timestamp 並 normalize (需求一)
            ts = pd.Timestamp(year=y, month=m, day=d).normalize()
            
            if include_position:
                results.append((ts, start, end))
            else:
                results.append(ts)
        except ValueError:
            continue # 忽略非法的日期組合（如 2026/02/30）

    if not results:
        return [] if return_all else None
    
    # 根據參數回傳 (需求二、四)
    return results if return_all else results[0]

def 取時間(時間=None):
    '''
    一、時間為表達時間之物件，如 "14:38" 字串。
    二、未指定則為現在時間。
    '''
    import pandas as pd
    import re
    if not 時間:
        return pd.Timestamp.now()

    pat = r'^([01]\d|2[0-3]):[0-5]\d$'
    if m:=re.match(pat, 時間):
        return pd.Timestamp(時間)

    return 時間

def 是工作日(日期):
    import datetime
    import holidays
    return 日期.weekday() < 5 and 日期 not in holidays.Taiwan()

# def 取日期(日期=None, 無效值以今日填補=True):
#     from zhongwen.date import 取日期
#     if not 日期:
#         if 無效值以今日填補:
#             return pd.Timestamp.today().normalize()
#         else:
#             return pd.NaT
#     return 取日期(日期)

def 取期間(期間, 全取=False):
    '''
    一、如有多個期間傳為首個，可指定全取則回傳全部期間之串列。
    二、期間非字串、期間或整數型態者，傳回 pd.NaT。
    '''
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
    
    if ms:=re.findall(r'(\d{4})-([01]?\d)', s):
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

def 取季別(季別表達):
    '''
    一、季別表達具年月，則為年月所在之季別。
    '''
    年數 = 季別表達.year
    季數 = ((季別表達.month-1) // 3)+1
    return 取期間(f'{年數}Q{季數}')

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
    '形式如2024年第3季。'
    try:
        季別 = 取季別(季別)
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

    if not d: d = 今日
    if pd.isnull(d):
        return ''
    if 昨今明表達:
        if d == 今日-Timedelta(days=1):
            return '昨'
        if d == 今日:
            return '今'
        if d == 今日+Timedelta(days=1):
            return '明'
        if d == 今日+Timedelta(days=2):
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

def 取民國季度(時間):
    '取民國113年11月之表達字串113年第4季'
    年數, 季數 = 取季別年數季數(時間)
    return f"{年數-1911}年第{季數}季"

def 取民國年度(日期=None):
    '以形式如【113年度】表達期間'
    return 取民國日期(日期, 格式='%Y年度')

def 取民國年數(日期=None):
    '日期民國113年1月1日取表達整數113，預設為今日'
    d = 取日期(日期)
    return d.year - 1911

def 取正式民國日期(d=None, 含星期=False):
    '格式如：112年7月29日'
    from zhongwen.數 import 取中文數字
    import pandas as pd
    if not d:
        d = 今日
    if isinstance(d, pd.Period):
        d = d.end_time.normalize()
    正式民國日期 = 取民國日期(d, "%Y年%M月%D日")
    if 含星期:
        正式民國日期 += f'({取中文數字(取日期(d).dayofweek+1).replace("七", "日")})'
    return 正式民國日期

def 取小寫民國日期(日期, 本年度省略年=True):
    '''
    一、格式如：一百一十年一月一日。
    二、預設本年度省略年。
    '''
    from zhongwen.數 import 取中文數字
    日期 = 取日期(日期)
    if 日期.year == 今年數:
        return f'{取中文數字(日期.month)}月{取中文數字(日期.day)}日'
    return f'{取中文數字(日期.year-1911)}年{取中文數字(日期.month)}月{取中文數字(日期.day)}日'

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
    return 取民國日期(年月+"01", 格式='%Y%m')

def 取季別年數季數(季別):
    import pandas as pd
    if isinstance(季別, pd.Timestamp):
        季別 = pd.Period(季別, freq='Q')
    else:
        季別 = 取期間(季別)
    return 季別.year, 季別.quarter

def 擇日():
    '''
    一、跳出日曆選單點選日期。
    二、支援鍵盤快捷鍵：d/D, w/W, m/M, y/Y, t。
    三、配色：黑底淺綠字 (Dark Mode)。
    '''
    from tkcalendar import Calendar
    from datetime import timedelta, datetime
    import tkinter as tk
    import pandas as pd

    root = tk.Tk()
    root.title("擇日")
    root.attributes('-topmost', True)
    root.configure(bg='#121212') # 設定視窗背景為深黑
    
    # 設定日曆配色
    cal = Calendar(root, 
                   selectmode='day', 
                   date_pattern='y-mm-dd', 
                   font=("Arial", 16),
                   background='#121212',      # 整體背景
                   foreground='#90EE90',      # 淺綠色文字 (LightGreen)
                   bordercolor='#333333',     # 邊框顏色
                   headersbackground='#1E1E1E', # 上方星期欄背景
                   headersforeground='#90EE90', # 上方星期欄文字
                   selectbackground='#006400',  # 選中時的深綠色背景
                   selectforeground='white',    # 選中時的文字顏色
                   normalbackground='#121212',  # 普通日期背景
                   normalforeground='#90EE90',  # 普通日期文字
                   weekendbackground='#121212', # 週末背景
                   weekendforeground='#32CD32', # 週末文字 (稍深的綠)
                   othermonthforeground='#444444', # 非本月日期的文字
                   othermonthbackground='#121212'  # 非本月日期的背景
                  )
    cal.pack(padx=20, pady=20)
    
    data = {'picked': pd.NaT}

    def on_ok(event=None):
        try:
            date_str = cal.get_date()
            data['picked'] = pd.to_datetime(date_str)
        except:
            pass
        finally:
            root.destroy()

    def on_cancel(event=None):
        root.destroy()

    def move_date(event):
        current_date = cal.selection_get()
        key = event.char
        
        # 處理日期邏輯
        if key == 'd': new_date = current_date + timedelta(days=1)
        elif key == 'D': new_date = current_date - timedelta(days=1)
        elif key == 'w': new_date = current_date + timedelta(weeks=1)
        elif key == 'W': new_date = current_date - timedelta(weeks=1)
        elif key == 'm': new_date = current_date + pd.DateOffset(months=1)
        elif key == 'M': new_date = current_date - pd.DateOffset(months=1)
        elif key == 'y': new_date = current_date + pd.DateOffset(years=1)
        elif key == 'Y': new_date = current_date - pd.DateOffset(years=1)
        elif key == 't': new_date = datetime.now().date() # 回到今天
        else: return

        # 更新選取並讓視圖跳轉
        cal.selection_set(new_date.date() if hasattr(new_date, 'date') else new_date)
        cal.see(new_date)

    # 按鈕也改成黑底綠字
    btn = tk.Button(root, text="擇定", 
                    command=on_ok, 
                    bg='#1E1E1E', 
                    fg='#90EE90', 
                    activebackground='#90EE90', 
                    activeforeground='#121212',
                    font=("Arial", 12))
    btn.pack(pady=10)
    
    # 綁定鍵盤
    root.bind('<Return>', on_ok)
    root.bind('<Escape>', on_cancel) # 按 Esc 退出
    root.bind('<Key>', move_date)
    
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()
    
    return data['picked']

def 取本週五():
    '周六為一週起始'
    import pandas as pd
    today = 今日
    # Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    current_weekday = today.weekday()
    
    # 定義距離「本週五」的天數差 (基於週六為一週起始)
    # 週六(5) 到 下週五 差 6 天
    # 週日(6) 到 下週五 差 5 天
    # 週一(0) 到 本週五 差 4 天
    # ...以此類推
    wait_days = {
        5: 6,  # Saturday
        6: 5,  # Sunday
        0: 4,  # Monday
        1: 3,  # Tuesday
        2: 2,  # Wednesday
        3: 1,  # Thursday
        4: 0   # Friday
    }
    
    days_to_friday = wait_days[current_weekday]
    return today + pd.Timedelta(days=days_to_friday)
    
一日 = pd.Timedelta(days=1)
一週 = pd.Timedelta(days=7)
一月 = pd.DateOffset(months=1)
一季 = pd.DateOffset(months=3)
半年 = pd.DateOffset(months=6)
一年 = pd.DateOffset(years=1)
今日 = 取日期()
今年數 = 今日.year
上年數 = 今年數-1
民國年數 = 今年數-1911
年底 = 取日期(f"{今日.year}.12.31")
年初 = 取日期(f"{今日.year}.1.1")
最近工作日 = pd.offsets.BDay().rollback(今日)
昨日 = 今日 - 一日
一週前 = 今日 - 一週
半月前 = 今日 - pd.Timedelta(days=14)
一季前 = 今日 - 一季
半年前 = 今日 - 半年
一年前 = 今日 - 一年
一月後 = 今日 + 一月
三月後 = 今日 + 一季
一年後 = 今日 + 一年
五年又一個月前 = 今日 - pd.DateOffset(months=61)
本月 = pd.Period(今日, 'M')
上月 = 本月 - 1
本月數 = 本月.month
上月數 = 上月.month
本季 = pd.Period(今日, 'Q-DEC')
上季 = 本季 - 1
上季末 = 上季.end_time.normalize()
季初 = 本季.start_time.normalize()
季末 = 本季.end_time.normalize()
本年度 = pd.Period(今日, 'Y')
上年度 = 本年度 - 1
現在 = 取時間()
一分鐘 = pd.Timedelta(minutes=1)
