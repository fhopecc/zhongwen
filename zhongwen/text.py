def 是否為中文字元(char:str):
    return '\u4e00' <= char <= '\u9fa5'

def 是否為平假名(c:str):
    return "\u3041" <= c <= "\u3096"

def 是否為片假名(c:str):
    return "\u30A1" <= c <= "\u30F6"

def 中文列舉表示(串列):
    '[a,b,c] -> a、b及c'
    heads = 串列[:-1]
    tail = 串列[-1]
    return '、'.join(heads) + f'及{tail}'

def 字元切換(string:str):
    '''輸入為大小寫字母，舉如拉丁字母，進行大小寫切換、
中文字母進行簡繁切換、日文字母平片假名切換(Todo)。
'''
    if string == '': return string
    def switch_case(c:str):
        if 是否為中文字元(c):
            from opencc import OpenCC
            r = OpenCC('s2t').convert(c)
            if r == c:
                return OpenCC('t2s').convert(c)
            return r

        if 是否為平假名(c):
            return chr(ord(c)-0x3041+0x30A1)

        if 是否為片假名(c):
            return chr(ord(c)-0x30A1+0x3041)

        if c.islower():
            return c.upper()
        else:
            return c.lower()

    if len(string) == 1: return switch_case(string)

    return ''.join(map(switch_case, string))


def 下載倉頡碼對照表():
    from .file import 下載
    f = 下載('https://github.com/Jackchows/Cangjie5/raw/master/Cangjie5_TC.txt')
    return f

from diskcache import FanoutCache
from pathlib import Path
wdir = Path(__file__).parent
cache = FanoutCache(wdir / 'cache')
@cache.memoize()
def 倉頡對照表():
    print('abc')
    from pandas import read_csv
    f = 下載倉頡碼對照表()
    df = read_csv(f, encoding='latin1'
                 ,skiprows=12
                 ,sep='\t'
                 ,names=['漢字','倉頡碼','標註']
                 )
    def convert(latin1:str):
        try:
            return latin1.encode('latin1').decode('utf8', errors='replace') 
        except AttributeError:
            return latin1
    df['漢字'] = df.漢字.map(convert)
    d = {}
    for index, row in df.iterrows():
        if not row['漢字'] in d:
            d[row['漢字']] = row['倉頡碼']
    return d

對照表 = 倉頡對照表()
對照表 = 倉頡對照表()
對照表 = 倉頡對照表()

def 倉頡首碼(char):
    try:
        return 對照表[char][0]
    except KeyError:
        return char

def 首碼搜尋表示式(char, text):
    cs = set()
    for i, c in enumerate(text):
        if c == char or 倉頡首碼(c) == char:
            cs.add(c)
    return f'[{"".join(cs)}]'


