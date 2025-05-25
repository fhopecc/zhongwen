import re
小寫數字表 = "零一二三四五六七八九"
大寫數字表 = "零壹貳參肆伍陸柒捌玖"
大写数字表 = "零壹贰叁肆伍陆柒捌玖"
小寫位名表 = "十百千"
大寫位名表 = "拾佰仟"
組名表 = "萬億兆京垓秭穰溝澗正載"
组名表 = "万亿兆京垓秭穰沟涧正载"
半型數字表 = "0123456789"
全型數字表 = "０１２３４５６７８９"

# 取得數值
def 轉數值(n, 傳回格式=False) -> int|float:  
    import pandas as pd
    if isinstance(n, str):
        # 百分比
        pat = r'(-?[\d]+(\.\d+)?)[%％]'
        if m:=re.match(pat, n):
            return 轉數值(m[1])/100
        pat = f'^[{全型數字表}]+$'
        if re.match(pat, n):
            d = str.maketrans(全型數字表, 半型數字表)
            return int(n.translate(d))

        # 不具位名之中文數
        中文數字='○0０零壹貳參肆伍陸柒捌玖一二三四五六七八九'
        pat = f'^[{中文數字}]+$'
        if re.match(pat, n):
            d = str.maketrans(中文數字, '0000123456789123456789')
            return int(n.translate(d))

        # 具單位之數值表示，如3年則取出3。
        單位 = '年'
        pat = rf'(\d+)[{單位}]+'
        if m:=re.match(pat, n):
            return int(m[1])

        # 具位名之中文數
        pat = r'^[零壹貳參肆伍陸柒捌玖拾一二三四五六七八九十百千佰仟萬億兆]+$'
        if m:=re.match(pat, n):
            return 中文數字轉數值(m.group(0))
        try:
            n = re.sub(r'[ ,，]', '', n)
            pat = r'^\((\d+\.?\d+)\)$'
            if m:=re.match(pat, n):
                return -1*轉數值(m.group(1))
            pat = r'^-?\d+$'
            if m:=re.match(pat, n):
                return int(n)
            return float(n)
        except:
            return 0


    return n

def 全型數字(number):
    if isinstance(number, int) or (isinstance(number, str) and number.isdigit()):
        translation_table = str.maketrans(半型數字表, 全型數字表)
        if isinstance(number, int):
            number_str = str(number)
        else:
            number_str = number
        return number_str.translate(translation_table)
    else:
        raise ValueError("Input must be a non-negative integer or a string of digits.")

def 中文數字轉數值(n):
    數字:str=小寫數字表+大寫數字表+大写数字表
    位名:str=小寫位名表+大寫位名表
    組名:str=組名表+组名表
    v = 0
    r = 0
    for c in n:
        if c in 數字:
            v = 數字.index(c) % len(小寫數字表)
        if c in 位名:
            if v != 0:
                r += v*10**(位名.index(c) % len(小寫位名表) + 1)
                v = 0
            if r == 0: # 十一 -> 11 
                r += 1*10**(位名.index(c) % len(小寫位名表) + 1)
        if c in 組名:
            r += v
            r *= 10**(4*(組名.index(c) % len(組名表) + 1))
            v = 0
    if v!=0:
        r+=v
    return r
    

def 中文數字(
    n: int | float | str,
    大寫: bool = False,
    簡體: bool = False,
    異體零: bool = False,
    兩: bool = False
) -> str:
    位名表 = 大寫位名表 if 大寫 else 小寫位名表
    _組名表 = 组名表 if 簡體 else 組名表
    數字表 = 大寫數字表 if 大寫 else 小寫數字表 
    數字表 = 大写数字表 if 大寫 and 簡體 else 數字表 
    數字表 = re.sub('二', '兩', 數字表) if 兩 else 數字表 
    點 =  '点' if 簡體 else '點' 
    
    n:str = str(n)
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

def 中文数字(n):
    return 中文數字(n, 簡體=True)

def 大寫中文數字(n):
    return 中文數字(n, 大寫=True)

def 大写中文数字(n):
    return 中文數字(n, 大寫=True, 簡體=True)

def 增減(變動數, 增減用語=['增加', '減少']):
    return (增減用語[0] if 變動數 > 0 else 增減用語[1]) + f'{abs(變動數):,.0f}'

# def 衰長(變動數):
    # return ('成長' if 變動數 > 0 else '減少') + f'{abs(變動數):,.0f}'

def 增減數(變動數):
    return ('增加' if 變動數 > 0 else '減少') + f'{abs(變動數)*100:,.2f}'

def 增減百分點(變動數, 增減用語=['增加', '減少']):
    return (增減用語[0] if 變動數 > 0 else 增減用語[1]) + f'{abs(變動數)*100:,.2f}'

def 約數(n) -> str:
    '中文萬約數表達，未達萬以全數表達'
    n = 轉數值(n)
    n = abs(n)
    if(n<10**4): return f'{n:,.0f}'
    s=""
    #億位數字
    h=n//10**8
    r=n%10**8
    if h:s+=f"{h:,.0f}億"
    #取萬位數字
    h=r//10**4
    r=n%10**4
    if h:s+=f"{h:,.0f}萬"
    if r: s+= "餘" 
    return s

def 最簡約數(n) -> str:
    '僅表達最高位數字，舉如：17億500萬餘元表達為17億餘元。'
    on = 轉數值(n)
    n = abs(on)
    sign = on / n if n > 0 else 1
    if(n<10**4): return f'{n:,.0f}'
    s=""
    #億位數字
    h=n//10**8
    r=n%10**8
    if h:
        s+=f"{h*sign:,.0f}億"
        if r: s+= "餘" 
        return s
    #萬位數字
    h=r//10**4
    r=n%10**4
    if h:s+=f"{h*sign:,.0f}萬"
    if r: s+= "餘" 
    return s

def 增減約數(變動數):
    return ('增加' if 變動數 > 0 else '減少') + 約數(abs(變動數))

def 百分比(n):
  '表達至2位小數百分比，另以--表達缺失值'
  import pandas as pd
  if pd.isnull(n): return '--'
  return f'{abs(float(n))*100:,.2f}％'

def 增減百分比(r, 增減文字=["增加", "減少"]):
    import pandas as pd
    if pd.isnull(r): return ''
    if isinstance(r, str): return r
    n = abs(r)
    _增減文字 = 增減文字[0] if r>0 else  增減文字[1] 
    return f'{_增減文字}{n:.2%}'

def 利損百分比(r):
    '用於利損項目，如毛利或毛損'
    return 增減百分比(r, ['利', '損'])

def 消長百分比(r):
    '比較前時序之數值用消長'
    return 增減百分比(r, ['成長', '衰退'])

def 同比百分比(r):
    '數據較去年同期增減'
    return 增減百分比(r, ['年增', '年減'])

def 二位實數(f):
    import pandas as pd
    if pd.isnull(f): return '--'
    return f'{abs(float(f)):,.2f}'

class 標號:
    def __init__(self, 號碼, 階層):
       self.號碼 = 號碼
       self.階層 = 階層

    def __str__(self):
        # 標號階層：壹、(貳)三、(四)5.(6)
        if self.階層==1:
            return f'{大寫中文數字(self.號碼)}、'
        if self.階層==2:
            return f'({大寫中文數字(self.號碼)})'
        if self.階層==3:
            return f'{中文數字(self.號碼)}、'
        if self.階層==4:
            return f'({中文數字(self.號碼)})'
        if self.階層==5:
            return f'{self.號碼}.'
        if self.階層==6:
            return f'({self.號碼})'

    def __eq__(self, other):
        if isinstance(other, 標號):
            return self.號碼==other.號碼 and self.階層==other.階層

def 轉標號(text):
    pat = f'([{大寫數字表}{大寫位名表}{組名表}]+)、'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 1)
    pat = f'\\(([{大寫數字表}{大寫位名表}{組名表}]+)\\)'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 2)
    pat = f'([{小寫數字表}{小寫位名表}{組名表}]+)、'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 3)
    pat = f'\\(([{小寫數字表}{小寫位名表}{組名表}]+)\\)'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 4)
    pat = f'([\\d]+).'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 5)
    return text 
    pat = f'\\(([\\d+)\\)'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 5)
    return text 
 
def 連續正負次數(數列):
    import numpy as np
    a = np.sign(數列)
    s = 0
    for n in a:
        if s*n < 0: return s
        s+=n
    return s

def 最近連續正負次數(時序):
    from warnings import warn
    from zhongwen.時序分析 import 最近連續正負次數
    warn(f'【最近連續正負次數】已移到「時序分析」模組，請使用【from 時序分析 import 最近連續正負次數】。', DeprecationWarning, stacklevel=2)
    return 最近連續正負次數(時序)

def 連續正數(數列):
    import numpy as np
    n = np.array(數列)
    n = n > 0
    s = 0
    for v in n:
        s = v*(s+v) 
    return s

def 貸方科目收支金額轉借方金額(金額):
    return abs(min(0, 金額))

def 貸方科目收支金額轉貸方金額(金額):
    return abs(max(0, 金額))

def 除零例外則回覆非數常數(含除法函數):
    '非數常數即NaN，亦即IEEE754 之 Not a Number 浮點數值。'
    from functools import wraps
    @wraps(含除法函數)
    def 除零回覆非數常數(*args, **kargs):
        try:
            return 含除法函數(*args, **kargs)
        except (ZeroDivisionError, TypeError):
            return float('nan')
    return 除零回覆非數常數

def 發生例外則回覆非數常數(函數):
    '非數常數即NaN，亦即IEEE754 之 Not a Number 浮點數值。'
    from functools import wraps
    @wraps(函數)
    def 發生例外回覆非數常數(*args, **kargs):
        try:
            return 函數(*args, **kargs)
        except:
            return float('nan')
    return 發生例外回覆非數常數

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--int", help="整數")
    parser.add_argument("--about", help="約數")
    parser.add_argument("--float", help="小數")
    parser.add_argument("--percent", help="百分比")
    parser.add_argument("--test", help="測試", action='store_true')
    parser.add_argument("--increment", help="中文數遞增")
    parser.add_argument("--decrement", help="中文數遞減")
    parser.add_argument("--dec_level", help="中文標號遞減層級")
    args = parser.parse_args()
    if args.increment:
        n = 轉標號(args.increment)
        # breakpoint()
        print(標號(n.號碼+1, n.階層))
    elif args.decrement:
        print(中文數遞減(args.decrement))
    elif args.percent:
        print(百分比(轉數值(args.percent)))
    elif args.float:
        print(小數(轉數值(args.float)))
    elif args.about:
        print(約數(轉數值(args.about)))
    elif args.int:
        print(f'{轉數值(args.int):,}')
    elif args.dec_level:
        n, l = 標號(args.dec_level)
        print(中文標號(n, l-1))
    elif args.test:
        test()
