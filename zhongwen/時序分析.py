from zhongwen.number import 發生例外則回覆非數常數
from pathlib import Path
import pandas as pd
import logging
logger = logging.getLogger(Path(__file__).stem)

@發生例外則回覆非數常數
def 連續消長次數(時序資料):
    s = 時序資料
    d = s - s.shift()
    return 最近連續正負次數(d)
    
@發生例外則回覆非數常數
def 最近連續非零正數次數(時序):
    import numpy as np
    a = np.sign(時序)
    s = 0
    for n in reversed(a):
        if np.isnan(n) or n <= 0: return s
        s+=n
    return s

@發生例外則回覆非數常數
def 最近連續正負次數(時序) -> int:
    import numpy as np
    a = np.sign(時序).dropna()
    s = 0
    for n in a[::-1]:
        if np.isnan(n): return int(s)
        if s != 0 and s*n < 0: return int(s)
        s+=n
    return int(s)

def 趨勢分析(時序, 時序數下限=3, 數據名稱=None, 匯出圖檔=None, 圖示=None, 時序周期="年", 數值單位='元'):
    '回傳趨勢及r方數之數組，如時序數低於下限則回傳(0, 0)'
    from fhopecc.洄瀾打狗人札記 import 網站本地目錄
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    s = 時序
    if not isinstance(s, pd.Series):
        raise ValueError('時序參數型態需為 pd.Series，而傳入型態為{type(時序)}')
    if len(s) < 時序數下限:
        return (0, 0)
    if pd.api.types.is_integer_dtype(s.index):
        s = 序列缺項補零(s)
    X = np.arange(1, len(s)+1).reshape(-1, 1)
    Y = s
    reg = LinearRegression().fit(X, Y)
    std = Y.std()
    趨勢 = reg.coef_[0]/std
    r2 =  r2_score(Y, reg.predict(X))
    if 匯出圖檔 or 圖示:
        title = f'{數據名稱}趨勢圖'
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] 
        plt.title(f'{title}(成長率：{趨勢:.2%}、r方：{r2:.2%})')
        plt.xlabel(f'{時序周期}數')
        plt.ylabel(f'{數值單位}')
        plt.scatter(X, Y)
        line = [reg.coef_* x for x in X] + reg.intercept_
        plt.plot(X, line, color='red')
        if 匯出圖檔:
            png = f'{title}.png'
            plt.savefig(網站本地目錄 / 'images' / png)
            logger.info(f'匯出{png}')
        if 圖示:
            plt.show()
        plt.close()
    return (趨勢, r2)

def 數據周期(數據, 發布周期='年', 圖示=None, 數據名稱=None, 頻譜圖=False):
    '波動幅度未達直流分量三成者或數據時長未大於周期1.5倍者，視作無周期'
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from fhopecc.洄瀾打狗人札記 import 網站本地目錄
    match 數據:
        case pd.Series():
            samples = 數據.tolist()
        case _:
            samples = list(數據)

    if len(samples) < 5: return 0

    y1 = samples
    x1 = np.arange(0, len(samples))
   
    fft = np.fft.fft(samples) #[:int(len(samples)/2)]
    y2 = np.abs(fft)/(int(len(fft)/2)) # 頻幅譜
    x2 = np.fft.fftfreq(len(y2), 1)
    y2[0] = y2[0]/2 # 頻率0表垂直位移，即直流分量，因正負0各疊加一次，須再除以2還原。
   
    argmax = np.argmax(y2[1:]) + 1 # 直流分量不計
    peak = y2[argmax] # 峰值
    if peak / y2[0] < 0.3: # 波動幅度未達直流分量三成者，視作無周期
        return 0
    f = x2[argmax] # 峰值頻率
    y3 = np.angle(fft) # 頻相譜，相位為應變項
    phase = y3[argmax] # 峰值相位

    if 數據名稱:
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
        plt.rcParams['axes.unicode_minus'] = False
        if 頻譜圖:
            p1 = plt.subplot(211)
            p2 = plt.subplot(212)
        else:
            p1 = plt.subplot(111)

        p1.scatter(x1, y1)
        for i, (xi, yi) in enumerate(zip(x1, y1)):
            p1.text(xi, yi, f'{yi:.2f}', ha='center', va='bottom')
        p1.set_xticks(x1)
        p1.set_xlabel(f'{發布周期}數')

        x2h = x2[:int(len(x2)/2)+1]
        y2h = y2[:int(len(x2)/2)+1]

        if 頻譜圖:
            p2.scatter(x2h, y2h)
            for i, (xi, yi) in enumerate(zip(x2h, y2h)):
                p2.text(xi, yi, f'{yi:.2f}', ha='center', va='bottom')
            p2.set_xticks(x2h)
            p2.set_xticklabels([f'{1/f:.2f}' for f in x2h], rotation=90)
            p2.set_xlabel(f'周期({發布周期})')

        p1.axhline(y=y2h[0], color='r', linestyle='-')
        x4 = np.linspace(min(x1), max(x1), 100)
        y4 = y2[0] + peak*np.cos(f*2*np.pi*x4 + phase) # 峰值頻率餘弦諧波
        p1.plot(x4, y4, color='orange')
        title = f'{數據名稱}周期圖\n'
        title += f"周期為{1/f:.2f}{發布周期}，平均{y2h[0]:.2f}元，上下振盪{peak:.2f}元"
        p1.set_title(title)
        if 數據名稱:
            png = f'{數據名稱}周期圖.png'
            plt.savefig(網站本地目錄 / 'images' / png)
            plt.close()
        if 圖示:
            plt.show()

    # 數據時長未大於周期1.5倍者，len/(1/f) = len*f
    if len(samples) * f  < 1.5: return 0
    return 1/f

def 正弦離散轉換():
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    plt.rcParams['axes.unicode_minus'] = False

    x1 = np.linspace(0, 1, 30)   
    y1 = 0.7 + np.cos(3*2*np.pi*x1+7)
    # plt.scatter(x, y)

    fft = np.fft.fft(y1)
    y = np.abs(fft) / (30/2)
    p = np.angle(fft)
    print(p)
    y[0] = y[0]/2 # 頻率0表直流分量，即垂宜位移，正負0各疊加一次，須再除以2還原。
    # x = np.linspace(0, 30-1, 30) # f_s = 30Hz, 頻率間隔 = 樣頻/樣數 = 30/30 = 1 Hz
    x = np.fft.fftfreq(30, 1/30)
    argmax = y.argmax()
    print(x[argmax])
    d = y[0]
    a = y[argmax]
    f = x[argmax]
    p = p[argmax]
    print(f'{d} + np.cos({f}*2*pi*x1+{p})')
    # plt.scatter(x, y)
    # plt.xticks(x, rotation=90)
    y2 = d + np.cos(f*2*np.pi*x1+p)
    plt.scatter(x1, y1)
    plt.scatter(x1, y2)
    plt.show()

def 最近缺失序列(序列:pd.Series):
    '找出最大序列索引缺項，即不連續缺口，並回傳索引值及序位'
    s = 序列.sort_index()
    full_index = pd.Index(range(s.index[0], s.index[-1]))
    # 找出缺項
    missing_index = full_index.difference(s.index)
    if not missing_index.empty:
        return (missing_index[-1], s.index.max()-missing_index[-1])
    else:
        return (None, 0)

def 序列缺項補零(序列:pd.Series):
    '序列索引缺項，即不連續缺口補零'
    s = 序列.sort_index()
    full_index = pd.Index(range(s.index[0], s.index[-1]))
    # 找出缺項
    missing_index = full_index.difference(s.index)
    # 將缺項插入序列並賦值為 0
    for miss in missing_index:
        s.loc[miss] = 0
    # 按索引順序重排
    return s.sort_index()

def 繪季節解析圖(時序):
    from statsmodels.tsa.seasonal import seasonal_decompose
    ts = 時序 
    r = seasonal_decompose(ts, period=12)
    r.plot()
    return r

class 無法於一階差分內穩定(Exception):pass
def 取穩定階數(時序):
    '回傳是否穩定及穩定差分階數'
    from 股票分析.股票基本資料分析 import 查股票代號
    from statsmodels.tsa.stattools import adfuller
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

if __name__ == '__main__':
    pass
    from 股票分析.股票基本資料分析 import 查股票代號
    from 股票分析.股利分析 import 年度股利分派表
    from zhongwen.date import 今日, 上年初
    import pandas as pd
    股票代號 = 查股票代號('台積電') # 潤弘及志超標準景氣循環股
    s = 年度股利分派表().loc[股票代號]
    if 今日().month < 4: # 年報尚未公布，故上年度股利可能未發放
        s = s[s.index < pd.to_datetime(上年初())]
    else:
        s = s[s.index < pd.to_datetime(今日())] # 歸屬今年度股利可能尚未完全發放，故排除。
    # t = 數據周期(s, 圖示=True)
    # breakpoint()
    a, b = 趨勢分析(s.配息, 圖示=True, 數據名稱='配息')
    print(a, b)
