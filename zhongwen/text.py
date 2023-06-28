'中文文字處理'
from diskcache import Cache
from pathlib import Path
cache = Cache(Path.home() / 'cache' / 'text')

def 去標籤(字串):
    import re
    字串 = 字串.replace('\u200b', '')
    字串 = 字串.replace('\xff', '')
    return re.sub(r'<.*?>', '', 字串)

def 中文詞界(curpos, line):
    import hanlp
    han = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
    words = (han(line))
    print(words)
    return words

def 臚列(項目):
    "['甲', '乙', '丙'] -> '甲、乙及丙'"
    if type(項目) == list:
        if len(項目) > 1:
            return f"{'、'.join(項目[:-1])}及{項目[-1]}" if len(項目) else ''
        return 項目[0]
    return 項目

def 是否為中文字元(char:str):
    return '\u4e00' <= char <= '\u9fa5'

def 是否為平假名(c:str):
    return "\u3041" <= c <= "\u3096"

def 是否為片假名(c:str):
    return "\u30A1" <= c <= "\u30F6"

全型表 = {i: i + 0xFEE0 for i in range(0x21, 0x7F)}
全型表[0x20] = 0x3000
半型表 = {v: k for k, v in 全型表.items()}

def 轉全型(s):
    return s.translate(全型表)

def 轉半型(s):
    return s.translate(半型表).replace('—', '-')

def 字元切換(string:str):
    '''輸入為大小寫字母，舉如拉丁字母，進行大小寫切換、
中文字母進行簡繁切換、日文字母平片假名切換、符號則為全半型轉換(Todo)。
'''
    if string == '': return string
    def switch_case(c:str):
        if c == '[': return '「'
        if c == ']': return '」'
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
    from zhongwen.file import 下載
    f = 下載('https://github.com/Jackchows/Cangjie5/raw/master/Cangjie5_TC.txt')
    return f

@cache.memoize()
def 倉頡對照表():
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

對照表 = 倉頡對照表() # 以模組變數將對照表緩存在記憶體
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

def 翻譯(word):
    from pygtrans import Translate
    client = Translate()
    # 翻译句子
    text = client.translate(word, 'zh-tw')
    return text.translatedText

def 校正異體字(字串:str):
    a = '車路類例宅金易勒精神行煉練復療溜樓例列量料飯旅冷靈禮福利老六數歷里不拉簾來說度便力錄連年爐讀益' 
    n = '車路類例宅金易勒精神行煉練復療溜樓例列量料飯旅冷靈禮福利老六數歷里不拉簾來說度便力錄連年爐讀益'
    t = str.maketrans(a, n)
    return 字串.translate(t)

def 刪空格(n):
    import re
    try: return re.sub(r'\s+', '', n)
    except TypeError: return n

class 萌典尚無定義之字詞(Exception):pass

def 查萌典(字詞):
    from .file import 抓取
    url = f'https://www.moedict.tw/{字詞}.json'
    j = 抓取(url)
    import json
    try:
        d = json.loads(j)
        hs = d['heteronyms']
        def 取定義(異名):
            h = 異名
            m = h['bopomofo']
            m += '：'
            ds = h['definitions']
            m += ''.join([去標籤(d["def"]) for d in ds])
            return m
        return '\n'.join([取定義(h) for h in hs])
    except json.JSONDecodeError:
        raise 萌典尚無定義之字詞(字詞) 
