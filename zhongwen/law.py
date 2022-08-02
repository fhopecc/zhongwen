from .file import 下載, 解壓
from pathlib import Path
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / 'law')

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
