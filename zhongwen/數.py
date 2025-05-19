from zhongwen.number import 半型數字表, 全型數字表, 小寫數字表, 小寫位名表
from zhongwen.number import 大寫數字表, 大写数字表, 大寫位名表, 組名表, 组名表
from zhongwen.number import 最簡約數, 增減百分點, 百分比
from zhongwen.number import 中文數字
全數字表  = 半型數字表 + 全型數字表 + 小寫數字表 + 小寫位名表 + ','
全數字表 += 大寫數字表 + 大写数字表 + 大寫位名表 + 組名表 + 组名表

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
    return 最簡約數(n)

def 取增減百分比(百分比, 增減表達=['增加', '減少'], 項目名稱=''):
    增加, 減少 = 增減表達
    增減說明 = 增加 if 百分比 > 0 else ('減少' if 百分比 < 0 else '')
    增減說明 += f'{abs(百分比):.2%}'
    return f'{項目名稱}{增減說明}'

def 取中文數字(
    數: int | float | str,
    大寫: bool = False,
    簡體: bool = False,
    異體零: bool = False,
    兩: bool = False
) -> str:
    import re
    位名表 = 大寫位名表 if 大寫 else 小寫位名表
    _組名表 = 组名表 if 簡體 else 組名表
    數字表 = 大寫數字表 if 大寫 else 小寫數字表 
    數字表 = 大写数字表 if 大寫 and 簡體 else 數字表 
    數字表 = re.sub('二', '兩', 數字表) if 兩 else 數字表 
    點 =  '点' if 簡體 else '點' 
    
    n:str = str(數)
    i:str = n
    d = ""

    if "." in n:
        i, d= n.split(".", 1)
        d = d.rstrip("0")
    cn = ''
    i = list(reversed(i))

    def 轉中文數字(i):
        cn = ''
        for pos, digit in enumerate(i):
            位名 = ""
            if digit != '0' and pos > 0:
                位名 = 位名表[pos-1]
            cn = 數字表[int(digit)] + 位名 + cn
        return cn

    for pos, 一組阿拉伯數字 in enumerate([i[idx:idx + 4] for idx in range(0, len(i), 4)]):
        _cn = 轉中文數字(一組阿拉伯數字)
        if pos > 0: 
            _cn = _cn + _組名表[pos-1]
        cn = _cn + cn 
    #一萬零六百零零 -> 一萬零六百
    cn = re.sub('零+$', '', cn)
    #一十六 -> 十六
    cn = re.sub('^一十', '十', cn)
    #一千六百 -> 一千六
    cn = re.sub(f'(千[{數字表}])百$', r'\1', cn)
    #一百一十 -> 一百一
    cn = re.sub(f'(百[{數字表}])十$', r'\1', cn)
    if d != "":
        cn += 點 + d.translate(str.maketrans('0123456789', 數字表))
    return cn    

def 取中文数字(数):
    return 取中文數字(数, 簡體=True)

def 取大寫中文數字(數):
    return 取中文數字(數, 大寫=True)

def 取大写中文数字(数):
    return 取中文數字(数, 大寫=True, 簡體=True)
