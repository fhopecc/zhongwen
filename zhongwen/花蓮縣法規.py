'花蓮縣政府主管法規資料'
from zhongwen.pandas_tools import 可顯示
from pathlib import Path
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / 'hllaw')
網址 = 'https://glrs.hl.gov.tw/glrsout/'


def 開啟網頁():
    os.system(f'start {網址}')

async def 抓取(url):
    import logging
    import aiohttp
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError:
            logging.info(f'抓取{url}逾時，停止10秒重試')
            import asyncio
            asyncio.sleep(10)
            return await 抓取(url)
 
def 解析法規(內容):
    from bs4 import BeautifulSoup as bs
    import re
    text = 內容
    t = bs(text, 'lxml')
    trs = t.select_one('#content > div.text-con > table').find_all('tr')
    if not trs:
        raise RuntimeError(f'解析法規資訊失敗：{text!r}')
    ths = [tr.th.text.strip().replace('：', '') for tr in trs]
    tds = [tr.td.text.strip() for tr in trs]
    fs = {k:v for k, v in zip(ths, tds)}
    try:
        content = t.select_one('#ctl00_cp_content_divLawContent08').text
        fs['法規內容'] = re.sub(r'\s', '', content.strip())
    except AttributeError:
        fs['法規內容'] = None
    return fs

@可顯示
@cache.memoize(expire=30*24*60*60, tag='爬取法規')
def 爬取法規():
    from zhongwen.file import 抓取
    df = 法規連結()
    dfs = []
    for i, r in df.iterrows():
        url = f'https://glrs.hl.gov.tw/glrsout/{r["網址"]}'
        text = 抓取(url)
        l = 解析法規(text)
        dfs.append(l)
    import pandas as pd
    df = pd.DataFrame(dfs)
    return df

@可顯示
def 法規():
    return 法規條文()

def 現行法規():
    '非廢止法規'
    from zhongwen.date import 取日期
    df = 法規().query('not 法規名稱.str.contains("廢")')
    df['修正日期'] = df.修正日期.fillna(df.公發布日)
    df['公發布日'] = df.公發布日.map(取日期)
    df['修正日期'] = df.修正日期.map(取日期)
    return df

async def 取連結(page_no):
    from bs4 import BeautifulSoup as bs
    import pandas as pd
    url = f'https://glrs.hl.gov.tw/glrsout/?page={page_no}'
    text = await 抓取(url)
    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)
    return df

async def 爬取法規連結():
    from bs4 import BeautifulSoup as bs
    from io import StringIO
    import asyncio
    import logging
    import re
    import pandas as pd
    url = 'https://glrs.hl.gov.tw/glrsout/'
    text = await 抓取(url)
    logging.debug(f'爬取法規連結：{text}')
    pat = r'(\d+)<div class="pageno hidden-xs"'
    if m:=re.search(pat, text):
        page_num = int(m[1])
    else:
        raise RuntimeError('法規主頁無頁數資訊。')
    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)
    dfs = await asyncio.gather(*[取連結(page_no) for page_no in range(2, page_num+1)])
    df = pd.concat([df, *dfs])
    return df

@cache.memoize(tag='法規連結', expire=30*24*60*60)
def 法規連結():
    import asyncio
    df = asyncio.run(爬取法規連結())
    return df

def 取法規目錄頁數(html):
    pat = r'(\d+)<div class="pageno hidden-xs"'
    text = html
    if m:=re.search(pat, text):
        return int(m[1])
    else:
        raise RuntimeError('法規主頁無頁數資訊。')

def 取法規頁連結(html):
    text = html
    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)
    return df

from lark import Lark, Transformer
def 法規分條(法規內容):
    p = Lark.open(Path(__file__).with_suffix('.lark'))
    t = p.parse(法規內容)
    t = 法規分條剖析樹().transform(t).children
    return t

class 法規分條剖析樹(Transformer):
    def LAW_FIRST_PARA(self, tok):
        pat = r"第([\d壹貳參肆伍陸柒捌玖拾一二三四五六七八九十]+)條(.*)"
        import re
        from zhongwen.number import 轉數值
        if m := re.match(pat, tok.value):
            num = 轉數值(m[1])
            p = m[2]
            return (num, p)

    def LAW2_FIRST_PARA(self, tok):
        pat = r"([一二三四五六七八九十]+)、(.*)"
        import re
        from zhongwen.number import 轉數值
        if m := re.match(pat, tok.value):
            num = 轉數值(m[1])
            p = m[2]
            return (num, p)

    def LAW3_FIRST_PARA(self, tok):
        pat = r"([壹貳參肆伍陸柒捌玖拾]+)、(.*)"
        import re
        from zhongwen.number import 轉數值
        if m := re.match(pat, tok.value):
            num = 轉數值(m[1])
            p = m[2]
            return (num, p)

    def PARA(self, tok):
        return tok.value

    def law(self, toks):   
        f, *paras = toks
        return (f[0], ''.join([f[1], *paras]))

    def law2(self, toks):   
        f, *paras = toks
        return (f[0], ''.join([f[1], *paras]))

    def law3(self, toks):   
        f, *paras = toks
        return (f[0], ''.join([f[1], *paras]))

    def law4(self, toks):
        return (1, toks[0].value)

@可顯示
@cache.memoize(expire=30*24*60*60, tag='法規條文')
def 法規條文(排除廢止者=True):
    import logging
    df = 爬取法規()
    from zhongwen.date import 取日期
    df.rename(columns={'廢止/停止適用日期':'廢止停止適用日期'}, inplace=True)
    df['公發布日'] = df.公發布日.map(取日期)
    df['修正日期'] = df.修正日期.map(取日期)
    df['廢止日期'] = df.廢止日期.map(取日期)
    df['廢止停止適用日期'] = df.廢止停止適用日期.map(取日期)
    if 排除廢止者:
        df = df.query('廢止停止適用日期.isnull()')
    def _法規分條(l):
        try:
            return 法規分條(l)
        except Exception as e:
            logging.info(f'法規分條錯誤：{e}')
            return l
    df['法規分條'] = df.法規內容.map(_法規分條)
    df = df.explode('法規分條')
    def 取條號(t):
        try: return t[0]
        except: return ''
    def 取條文內容(t):
        try: return t[1]
        except: return ''
    df['條號'] = df.法規分條.map(取條號)
    df['條文內容'] = df.法規分條.map(取條文內容)
    df['修正日期'] = df.修正日期.fillna(df.廢止停止適用日期).fillna(df.公發布日)
    df.rename(columns={'修正日期':'異動日期'}, inplace=True)
    return df[['法規名稱', '異動日期', '條號', '條文內容']]

if __name__ == '__main__':
    pass
    # import logging
    # logging.getLogger().setLevel(logging.INFO)
    # cache.evict('法規條文')
    法規條文(顯示=True)
