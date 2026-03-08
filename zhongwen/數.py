from zhongwen.number import 半型數字表, 全型數字表, 小寫數字表, 小寫位名表
from zhongwen.number import 大寫數字表, 大写数字表, 大寫位名表, 組名表, 组名表
from zhongwen.number import 最簡約數, 增減百分點, 百分比
from zhongwen.number import 中文數字
全數字表  = 半型數字表 + 全型數字表 + 小寫數字表 + 小寫位名表 + ','
全數字表 += 大寫數字表 + 大写数字表 + 大寫位名表 + 組名表 + 组名表

def 求值(公式) -> float:
    '數學式求值'
    import re
    公式 = str(公式)
    processed_expr = re.sub(r'([\d.]+)[%％]', r'(\1/100)', 公式)
    try:
        result = eval(processed_expr)
        return result
    except Exception as e: pass
    return float('nan')

def 取數值(n, 全取=False, 無法解析時產生例外=False):
    from zhongwen.number import 轉數值
    import numpy as np
    import re
    if n == '--': return np.nan

    if not isinstance(n, str):
        return 轉數值(n)

    pat = f'\(?-?[{全數字表}]+[點.]?[{全數字表}]*[%]?\)?'
    if ms:=re.findall(pat, n):
        ps = [轉數值(m) for m in ms]
   
    if 全取: return ps
    
    try:
        return ps[0]
    except UnboundLocalError:
        if 無法解析時產生例外:
            raise UnboundLocalError(f"'{n}'無法解析為數值字串！")
    return 轉數值(n)

def 取最簡約數(n):
    return 最簡約數(取數值(n))

def 取增減百分比(百分比, 增減表達=['增加', '減少'], 項目名稱='', 無小數=False):
    增加, 減少 = 增減表達
    增減說明 = 增加 if 百分比 > 0 else ('減少' if 百分比 < 0 else '')
    if 無小數:
        增減說明 += f'{abs(百分比):.0%}'
    else:
        增減說明 += f'{abs(百分比):.2%}'
    return f'{項目名稱}{增減說明}'

def 取增減數(數值, 增減表達=['增加', '減少'], 項目名稱='', 無小數=True):
    增加, 減少 = 增減表達
    增減說明 = 增加 if 數值 > 0 else ('減少' if 數值 < 0 else '')
    if 無小數:
        增減說明 += f'{abs(數值):,.0f}'
    else:
        增減說明 += f'{abs(數值):,.2f}'
    return f'{項目名稱}{增減說明}'

def 取中文數字(
    數: int | float | str,
    大寫: bool = False,
    簡體: bool = False,
    異體零: bool = False,
    兩: bool = False
) -> str:
    from zhongwen.number import 中文數字 as _中文數字
    return _中文數字(數, 大寫=大寫, 簡體=簡體, 異體零=異體零, 兩=兩)

def 取中文数字(数):
    return 取中文數字(数, 簡體=True)

def 取大寫中文數字(數):
    return 取中文數字(數, 大寫=True)

def 取大写中文数字(数):
    return 取中文數字(数, 大寫=True, 簡體=True)

def 計算增減率(上期數, 本期數):
    import pandas as pd
    import numpy as np
    try:
        if 本期數 > 0 and 上期數 <=0:
            return np.inf
        elif 本期數 <= 0 and 上期數 > 0:
            return -np.inf
        return (本期數 - 上期數) / abs(上期數)
    except ZeroDivisionError:
        if 本期數>0:
            return np.inf
        else:
            return -np.inf
    except Exception as e:
        raise ValueError(f'上期數{上期數}及本期數{本期數}發生錯誤如次：{e}!')
