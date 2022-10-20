from .file import 下載, 解壓
from pathlib import Path
from diskcache import Cache
import re
cache = Cache(Path.home() / 'cache' / 'law')

@cache.memoize()
def 中央法律():
    url = 'https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CF'
    z = Path.home() / 'TEMP' / 'falv.zip'
    下載(url, z)
    falv = Path.home() / 'TEMP' / 'law' / 'FalV.xml'
    解壓(z, falv.parent)
    from xml.etree.cElementTree import parse
    return parse(falv)

@cache.memoize()
def 中央命令():
    url = 'https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CM'
    z = Path.home() / 'TEMP' / 'mingling.zip'
    下載(url, z)
    minling = Path.home() / 'TEMP' / 'law' / 'MingLing.xml'
    解壓(z, minling.parent)
    from xml.etree.cElementTree import parse
    return parse(minling)

@cache.memoize()
def 法規名稱字首樹():
    url = 'https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CF'
    z = Path.home() / 'TEMP' / 'falv.zip'
    下載(url, z)
    falv = Path.home() / 'TEMP' / 'law' / 'FalV.xml'
    解壓(z, falv.parent)

    url = 'https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CM'
    z = Path.home() / 'TEMP' / 'mingling.zip'
    下載(url, z)
    minling = Path.home() / 'TEMP' / 'law' / 'MingLing.xml'
    解壓(z, minling.parent)
 
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

# cache.clear()
@cache.memoize()
def 法規條文表():
    from pandas import DataFrame, concat
    l = 中央法律()
    def 法條資料表(法規):
        def 條號數(s):
            pat = r'第[^\d]*([-\d]+)[^\d]*條'
            if m:=re.match(pat, s):
                return m[1]
            return s
        條號 = [條號數(n.find('條號').text) for n in 法規.findall('*/條文')]
        條文內容 = [n.find('條文內容').text for n in 法規.findall('*/條文')]
        df = DataFrame(data = {'條號':條號, '條文內容':條文內容})
        df['法規名稱'] = 法規.find('法規名稱').text
        return df[['法規名稱', '條號', '條文內容']]
    law = concat([法條資料表(法規) for 法規 in 中央法律().findall('法規')])
    mingling = concat([法條資料表(法規) for 法規 in 中央命令().findall('法規')]) 
    df = concat([law, mingling])
    return df

def 法條查詢(s):
    q = LawQuery(s)
    if not q.法規名稱 : return ''

    def 屬性條件(a):
        if a=='關鍵字': return '條文內容.str.contains(@q.關鍵字)'
        return f'{a}==@q.{a}'

    qstr = [屬性條件(a) for a in dir(q) if not a.startswith("__") and getattr(q, a)!=None]

    qstr = ' and '.join(qstr)
    return 法規條文表().query(qstr)

def 法條展開(s):
    l = 法條查詢(s).values[0]
    return f'{l[0]}第{l[1]}條規定：「{l[2]}」'

def 法條說明(s):
    ls = 法條查詢(s)
    def 條文內容(l):
        # breakpoint()
        return f'{l[0]}第{l[1]}條規定：「{l[2]}」'
    doc = '\n'.join([條文內容(l.tolist()) for l in ls.values])
    return doc
    # return str(ls)

class LawQuery:
    def __init__(self, s):
        self.法規名稱=None
        self.條號=None
        self.關鍵字=None
        pat = r'(.*(法|規則|標準))第([-\d]+)[點條]'
        if m:=re.match(pat, s):
            self.法規名稱=m[1]
            self.條號 = m[3]
            return

        pat = r'(.*(法|規則|標準))([-\d]+)'
        if m:=re.match(pat, s):
            self.法規名稱=m[1]
            self.條號 = m[3]
            return

        pat = r'(.*(法|規則|標準))\[(.*)\]'
        if m:=re.match(pat, s):
            self.法規名稱 = m[1]
            self.關鍵字 = m[3]
            return
     
if __name__ == '__main__':
    text = 法條說明('職業安全衛生法[合格]')
    print(text)
    # df = 法條('職業安全衛生法[合格]')
    # temp = Path.home() / 'TEMP'
    # html = temp / 'output.html'

    # df.to_html(html
              # ,formatters={'金額':lambda x: f'{x:,.0f}'})
    # import os
    # os.system(f'start {html}')
