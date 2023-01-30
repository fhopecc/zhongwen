import pandas as pd
import re

def 中央地方法規條文():
    from zhongwen import 中央法規
    from zhongwen import 花蓮縣法規
    df = pd.concat([中央法規.法規條文(), 花蓮縣法規.法規條文()])
    df['條號'] = df.條號.map(lambda n: f'{n}')
    return df

def 顯示關鍵字查詢法規結果(關鍵字):
    from zhongwen.pandas_tools import 強調關鍵字, show_html
    df = 中央地方法規條文()
    pat = '|'.join(關鍵字)
    df = df.query('法規名稱.str.contains(@pat, na=False) or 條文內容.str.contains(@pat, na=False)')
    df = 強調關鍵字(df, ['法規名稱', '條文內容'], 關鍵字)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index+1
    df.index.name = '編號'
    show_html(df, 無格式=False, 顯示筆數=300)

def 法條查詢(s):
    q = LawQuery(s)
    if not q.法規名稱 : return ''

    def 屬性條件(a):
        if a=='關鍵字': return '條文內容.str.contains(@q.關鍵字)'
        return f'{a}==@q.{a}'

    qstr = [屬性條件(a) for a in dir(q) if not a.startswith("__") and getattr(q, a)!=None]

    qstr = ' and '.join(qstr)
    return 中央地方法規條文().query(qstr)

def 法條展開(s):
    return '\n'.join([f'{l[0]}第{l[2]}條規定：「{l[3]}」' for l in 法條查詢(s).values])

def 法條說明(s):
    ls = 法條查詢(s)
    def 條文內容(l):
        return f'{l[0]}第{l[2]}條規定：「{l[3]}」'
    doc = ''.join([條文內容(l.tolist()) for l in ls.values])
    return doc

class LawQuery:
    def __init__(self, s):
        self.法規名稱=None
        self.條號=None
        self.關鍵字=None
        pat = r'(.*(法|條例|規則|標準|細則))第([-\d]+)[點條]'
        if m:=re.match(pat, s):
            self.法規名稱=m[1]
            self.條號 = m[3]
            return

        pat = r'(.*(法|條例|規則|標準|細則))([-\d]+)'
        if m:=re.match(pat, s):
            self.法規名稱=m[1]
            self.條號 = m[3]
            return

        pat = r'(.*(法|條例|規則|標準|細則))\[(.*)\]'
        if m:=re.match(pat, s):
            self.法規名稱 = m[1]
            self.關鍵字 = m[3]
            return

def 法規名稱字首樹():
    中央地方法規條文() 
    from marisa_trie import Trie
    return Trie(中央地方法規條文().法規名稱.to_list())

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
