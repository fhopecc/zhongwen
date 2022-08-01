from .file import 下載

def 中文詞界(curpos, line):
    # import jiojio
    # jiojio.init()
    import hanlp
    han = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
    words = (han(line))
    return words

def 臚列(項目):
    "['甲', '乙', '丙'] => '甲、乙及丙'"
    return f"{'、'.join(項目[:-1])}及{項目[-1]}" if len(項目) else ''

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
    f = 下載('https://github.com/Jackchows/Cangjie5/raw/master/Cangjie5_TC.txt')
    return f

from diskcache import Cache
from pathlib import Path
cache = Cache(Path.home() / 'cache')
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
    # breakpoint()
    return text.translatedText

cache.clear()
@cache.memoize()
def 法規名稱字首樹():
    # falv = 下載('https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CF', 'FALV.zip')
    falv = Path(__file__).parent.parent / 'FalV' / 'FalV.xml'
    minling = Path(__file__).parent.parent / 'MingLing' / 'MingLing.xml'
    from xml.etree.cElementTree import parse
    d = parse(falv)
    d = [t.text for t in d.findall('*/法規名稱')]
    m = parse(minling)
    d += [t.text for t in m.findall('*/法規名稱') ]
    from marisa_trie import Trie
    return Trie(d)

def 法規自動完成建議(line):
    '第一個結果是找出的字首'
    for i in range(0, len(line)):
        prefix = line[i:]
        ls = 法規名稱字首樹().keys(prefix)
        if len(ls) > 0:
            # 名稱越短的法規越重要
            ls = sorted(ls, key=len)
            return [prefix, *ls]
    return []
