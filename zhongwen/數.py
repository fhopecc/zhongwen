from zhongwen.number import 半型數字表, 全型數字表, 小寫數字表, 小寫位名表
from zhongwen.number import 大寫數字表, 大写数字表, 大寫位名表, 組名表, 组名表
from zhongwen.number import 最簡約數
全數字表  = 半型數字表 + 全型數字表 + 小寫數字表 + 小寫位名表
全數字表 += 大寫數字表 + 大写数字表 + 大寫位名表 + 組名表 + 组名表

def 取數值(n, 全取=False, 無法解析時產生例外=False):
    from zhongwen.number import 轉數值
    import numpy as np
    import re
    if n == '--': return np.nan

    pat = f'[{全數字表}]+[點.]?[{全數字表}]*[%]?'
    if not isinstance(n, str):
        return 轉數值(n)
    if ms:=re.findall(pat, n):
        ps = [轉數值(m) for m in ms]
   
    if 全取: return ps
    
    try:
        return ps[0]
    except UnboundLocalError:
        if 無法解析時產生例外:
            raise UnboundLocalError(f"'{n}'無法解析為數值字串！")

    return 轉數值(n)
