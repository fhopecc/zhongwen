'中文文字處理'
from diskcache import Cache
from pathlib import Path
from functools import lru_cache
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=ResourceWarning) 
cache = Cache(Path.home() / 'cache' / 'text')

@lru_cache
@cache.memoize()
def hantok():
    import hanlp
    return hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)

@lru_cache
def 分詞(字串):
    return {w for w in hantok()(字串) if len(w) > 1}

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
    項目 = list(項目)
    if type(項目) == list:
        if len(項目) > 1:
            return f"{'、'.join(項目[:-1])}及{項目[-1]}" if len(項目) else ''
        return 項目[0]
    return 項目

def 是否為中文字元(char:str):
    return '\u4e00' <= char <= '\u9fa5'

def 是否為中文符號(char:str):
    import re
    chinese_punctuation_pattern = re.compile(r'[\u3000-\u303F\uFF00-\uFFEF\u2000-\u206F]')
    return bool(re.match(chinese_punctuation_pattern, char))

def 是否為平假名(c:str):
    return "\u3041" <= c <= "\u3096"

def 是否為片假名(c:str):
    return "\u30A1" <= c <= "\u30F6"

def 是否為字元(c:str):
    import string
    # 檢查字元是否為符號
    if c in string.punctuation or 是否為中文符號(c) or c.isspace():
        return False
    return True

全型表 = {i: i + 0xFEE0 for i in range(0x21, 0x7F)}
全型表[0x20] = 0x3000
半型表 = {v: k for k, v in 全型表.items()}

def 轉全型(s):
    return s.translate(全型表)

def 轉半型(s):
    return s.translate(半型表).replace('—', '-')

def 字元切換(string:str):
    '''就大小寫字母，舉如拉丁字母，進行大小寫切換；重碼字母進行校正；中文字母進行簡繁切換；日文字母平片假名切換；符號則為全半型轉換(Todo)。
'''
    from opencc import OpenCC
    if string == '': return string
    def switch_case(c:str):
        if c == '[': return '「'
        if c == ']': return '」'

        if 是否為重碼字(c):
            return 校正中文字(c)

        if 是否為中文字元(c):
            # 簡繁切換
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

重碼字 ='車路類例宅金易勒精神行煉練復療溜樓例列量料飯旅冷靈禮福利老六數歷里不拉簾來說度便力錄連年爐讀益'
重碼字+='立異理狀'
正體字 ='車路類例宅金易勒精神行煉練復療溜樓例列量料飯旅冷靈禮福利老六數歷里不拉簾來說度便力錄連年爐讀益'
正體字+='立異理狀'

def 是否為重碼字(字串:str):
    return 字串[0] in 重碼字 

def 校正中文字(字串:str):
    t = str.maketrans(重碼字, 正體字)
    return 字串.translate(t)

def 刪空格(n):
    import re
    try: return re.sub(r'[\s　]+', '', n)
    except TypeError: return n

class 萌典尚無定義之字詞(Exception):pass

def 查萌典(字詞):
    from .file import 抓取
    import requests
    import logging
    import json
    url = f'https://www.moedict.tw/{字詞}.json'
    try:
        j = 抓取(url)
        d = json.loads(j)
        hs = d['heteronyms']
        def 取定義(異名):
            h = 異名
            try:
                m = h['bopomofo']
                m += '：'
            except KeyError:
                m = ''
            ds = h['definitions']
            m += ''.join([去標籤(d["def"]) for d in ds])
            return m
        return [取定義(h) for h in hs]
    except (json.JSONDecodeError, requests.exceptions.HTTPError):
        raise 萌典尚無定義之字詞(字詞) 

def 去除字串末句號(字串):
    import re
    return re.sub('。$', '', 字串)

def 公司正名(公司名稱):
    import re
    n = 公司名稱
    n = n.replace("(股)", "股份有限")
    n = re.sub(r'\(下稱.+\)$', '', n)
    return n

def 轉樣式表字串(字串):
    '以將Unicode字串以CSS跳脫字元方式轉成ASCII字串，'
    import re
    try:
        original_string = 字串
        unicode_escaped_string = original_string.encode('unicode_escape').decode()
        # print(unicode_escaped_string)
        pat = r'\\u(\w{4})'
        css_escaped_string = re.sub(pat, r'\\00\1', unicode_escaped_string)
        # print(css_escaped_string)
        return css_escaped_string
    except AttributeError:
        return 字串

def 符號轉半型(s, 輸出錯誤訊息=False):
    import logging
    try:
        return s.translate(str.maketrans('，；：％。、'
                                        ,',;:%.,')
                )
    except AttributeError as e:
        if 輸出錯誤訊息:
            logging.error(f'符號轉半型錯誤{e}')
        return s

def 移除非中文字(text):
    '移除非中文字及符號，可用於表頭標題的正規化。'
    import re
    chinese_pattern = re.compile(r'[^\u4e00-\u9fa5]')  # 匹配非中文字的正則表達式
    return chinese_pattern.sub('', text)

def 是否為空白字元(text):
    raise Exception('請用 str.isspace() 替代！')

def 交談(text):
    import requests 

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyDF7loLYLpl7V4XXJzP4uJsOy59vZSOZB4'
    data = '{"contents":[{"parts":[{"text":"'+text+'"}]}]}'
    # data = [{"parts":[{"text":f"{text}"}]}]
    # print(data)
    import json.encoder
    r = requests.post(url, data=data, headers=headers)
    
    return r.json()

環繞開啟符號 = "'\"([{「『（【"
環繞關閉符號 = "'\")]}」』）】"
環繞關閉符號對應 = str.maketrans(環繞開啟符號, 環繞關閉符號)

def 取環繞關閉符號(環繞開啟符號:str):
    return 環繞開啟符號.translate(環繞關閉符號對應)

def 取最近環繞符號(字串:str) -> str:
    最近環繞符號索引 = -1
    最近環繞符號位置 = -1
    for i, c in enumerate(環繞開啟符號):
        p = 字串.rfind(c)
        if p == -1:
            continue
        最近環繞符號位置 = max(最近環繞符號位置, p)
        if 最近環繞符號位置 == p:
            最近環繞符號索引 = i
    if 最近環繞符號位置 == -1:
        raise RuntimeError(f'以下字串尚無環繞符號：{字串}')
    return 環繞開啟符號[最近環繞符號索引] + 環繞關閉符號[最近環繞符號索引]

def 刪除環繞符號(字串:str, 環繞符號='(', 游標位置:int=0) -> str:
    import re
    l = 環繞符號
    r = 取環繞關閉符號(l)
    p = 游標位置
    pat = f"{l}[^{r}]?{r}"
    istart = 0
    iend = 0
    for m in re.finditer(pat, 字串):
        start = m.start()
        end = m.end()
        if start <= p <= end:
            if start > istart:
                istart = start
                iend = end
    if istart != iend:
        return 字串[:start] + 字串[start+1:end-1] + 字串[end:]
    return 字串

def 插入環繞符號(字串:str, 環繞符號='(', 列:int=0, 區間='w') -> str:
    '區間是vim的 motion 命令，如 w、$'
    import re
    match 區間:
        case 'w':
            s = 字串[列-1:]
            pat = r'[a-zA-Z\u4e00-\u9fff]+'
            if m:=re.match(pat, s):
                return f'{字串[:列-1]}{環繞符號}{m[0]}{取環繞關閉符號(環繞符號)}{s[m.end():]}' 

左引號 = "'\"([{「『（【"
右引號 = "'\")]}」』）】"
左引號表 = dict(zip(右引號, 左引號))

from dataclasses import dataclass
@dataclass
class 引用:
    內容:str
    始:int
    迄:int

def 取引用內容(字串:str, 游標位置:int=0):
    s = 字串
    slen = len(s)
    可能右引號 = 右引號
    pos = 游標位置
    rpos = pos
    while len(可能右引號) > 0:
        r = None
        while rpos < slen:
            if s[rpos] in 可能右引號:
                r = s[rpos]
                break
            rpos += 1
        if not r:
            return None
        l = 左引號表[r]
        left = s[:rpos+1]
        lpos = left.rfind(l)
        if pos < lpos:
            可能右引號 = 可能右引號.replace(r, "")
            continue
        return 引用(字串[lpos:rpos+1], lpos, rpos)
    return None

def 查找引號對(expression):
    stack = []
    matches = {}

    for i, char in enumerate(expression):
        if char in "([{":
            stack.append((char, i))
        elif char in ")]}":
            if not stack:
                raise ValueError(f"Unmatched closing {char} at index {i}")
            opening_char, opening_index = stack.pop()
            if (opening_char == '(' and char != ')') or \
               (opening_char == '[' and char != ']') or \
               (opening_char == '{' and char != '}'):
                raise ValueError(f"Unmatched {opening_char} at index {opening_index} with {char} at index {i}")
            matches[opening_index] = i
            matches[i] = opening_index

    if stack:
        remaining_opening = stack.pop()
        raise ValueError(f"Unmatched opening {remaining_opening[0]} at index {remaining_opening[1]}")

    return matches


