import re
小寫數字表 = "零一二三四五六七八九"
大寫數字表 = "零壹貳參肆伍陸柒捌玖"
大写数字表 = "零壹贰叁肆伍陆柒捌玖"
小寫位名表 = "十百千"
大寫位名表 = "拾佰仟"
組名表 = "萬億兆京垓秭穰溝澗正載"
组名表 = "万亿兆京垓秭穰沟涧正载"

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
    
def 轉數值(n, 傳回格式=False) -> int|float:  
    if isinstance(n, str):
        # 不具位名之中文數
        中文數字='○0０零壹貳參肆伍陸柒捌玖一二三四五六七八九'
        pat = f'^[{中文數字}]+$'
        if re.match(pat, n):
            d = str.maketrans(中文數字, '0000123456789123456789')
            return int(n.translate(d))

        # 具位名之中文數
        pat = r'^[零壹貳參肆伍陸柒捌玖拾一二三四五六七八九十百千萬億兆]+$'
        if m:=re.match(pat, n):
            from pycnnum import cn2num
            return cn2num(m.group(0))
        try:
            n = re.sub(r'[ ,，]', '', n)
            pat = r'^-?\d+$'
            if m:=re.match(pat, n):
                return int(n)
            return float(n)
        except:
            return 0
    return n

def 中文數字(
    n: int | float | str,
    大寫: bool = False,
    簡體: bool = False,
    異體零: bool = False,
    兩: bool = False
) -> str:
    # system = NumberingSystem(numbering_type)
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
        # breakpoint()
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

def 約數(n) -> str:
    '中文萬約數表達，未達萬以全數表達'
    n = 轉數值(n)
    n = abs(n)
    if(n<10**4): return 全數(n)
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

class 標號:
    def __init__(self, 號碼, 階層):
       self.號碼 = 號碼
       self.階層 = 階層

    def __str__(self):
        # 標號階層：壹、(貳)三、(四)5.(6)
        if self.階層==1:
            return f'{大寫中文數字(self.號碼)}、'
        if self.階層==4:
            return f'({中文數字(self.號碼)})'

    def __eq__(self, other):
        if isinstance(other, 標號):
            return self.號碼==other.號碼 and self.階層==other.階層

def 轉標號(text):
    pat = f'([{大寫數字表}]+)、'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 1)
    pat = f'([{小寫數字表}]+)、'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 3)
    pat = f'([\d]+).'
    if m:=re.match(pat, text):
        return 標號(轉數值(m[1]), 5)
    return text 
