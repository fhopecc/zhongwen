from zhongwen.number import 發生例外則回覆非數常數

@發生例外則回覆非數常數
def 連續消長次數(時序資料, 欄位):
    df = 時序資料
    數值 = df[欄位]
    差異 = 數值 - 數值.shift()
    消長 = 差異/差異.abs()
    變化 = 消長 != 消長.shift()
    df['分組']= 變化.cumsum()
    連續次數 = df.groupby('分組')['index'].rank(method='first')
    return (連續次數 * 消長).fillna(0).astype(int).iloc[-1]

@發生例外則回覆非數常數
def 最近連續非零正數次數(時序):
    import numpy as np
    a = np.sign(時序)
    s = 0
    for n in reversed(a):
        if np.isnan(n) or n <= 0: return s
        s+=n
    return s
