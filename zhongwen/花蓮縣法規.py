'花蓮縣政府主管法規資料'
from bs4 import BeautifulSoup as bs
from zhongwen.file import 抓取
from zhongwen.number import 轉數值
from pathlib import Path
from diskcache import Cache
import pandas as pd
import asyncio
import os
import re
cache = Cache(Path.home() / 'cache' / 'hllaw')

網址 = 'https://glrs.hl.gov.tw/glrsout/'

def 開啟網頁():
    os.system(f'start {網址}')

async def 抓取法規(網址):
    url = f'https://glrs.hl.gov.tw/glrsout/{網址}'
    text = 抓取(url)
    t = bs(text, 'lxml')
    tr = t.select_one('#content > div.text-con > table > tbody')
    ths = [th.text.strip().replace('：', '') for th in tr.select('th')]
    tds = [td.text.strip() for td in tr.select('td')]
    fs = {k:v for k, v in zip(ths, tds)}
    try:
        content = t.select_one('#ctl00_cp_content_divLawContent08').text
        fs['法規內容'] = re.sub(r'\s', '', content.strip())
    except AttributeError:
        fs['法規內容'] = None
    return fs

async def 爬取法規():
    df = await 爬取法規連結()
    dfs = await asyncio.gather(*[抓取法規(row['網址']) for i, row in df.iterrows()])
    df = pd.DataFrame(dfs)
    return df

@cache.memoize(expire=30*24*60*60, tag='法規')
def 法規():
    df = asyncio.run(爬取法規())
    return df

def 現行法規():
    '非廢止法規'
    from zhongwen.date import 取日期
    df = 法規().query('not 法規名稱.str.contains("廢")')
    df['修正日期'] = df.修正日期.fillna(df.公發布日)
    df['公發布日'] = df.公發布日.map(取日期)
    df['修正日期'] = df.修正日期.map(取日期)
    return df

async def 取連結(page_no) -> pd.DataFrame:
    url = f'https://glrs.hl.gov.tw/glrsout/?page={page_no}'
    text = 抓取(url)
    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)
    return df

async def 爬取法規連結():
    from io import StringIO
    url = 'https://glrs.hl.gov.tw'
    text = 抓取(url)
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

def 取法規目錄頁數(html):
    pat = r'(\d+)<div class="pageno hidden-xs"'
    text = html
    if m:=re.search(pat, text):
        return int(m[1])
    else:
        raise RuntimeError('法規主頁無頁數資訊。')

def 取法規頁連結(html) -> pd.DataFrame:
    text = html
    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)
    return df

from lark import Lark, Transformer
def 法規分條(法規內容):
    try:
        p = Lark.open(Path(__file__).with_suffix('.lark'))
        t = p.parse(法規內容)
        t = 法規分條剖析樹().transform(t).children
        return t
    except:
        return 法規內容 

class 法規分條剖析樹(Transformer):
    def LAW_FIRST_PARA(self, tok):
        pat = r"第([\d壹貳參肆伍陸柒捌玖拾一二三四五六七八九十]+)條(.*)"
        if m := re.match(pat, tok.value):
            num = 轉數值(m[1])
            p = m[2]
            return (num, p)

    def LAW2_FIRST_PARA(self, tok):
        pat = r"([一二三四五六七八九十]+)、(.*)"
        if m := re.match(pat, tok.value):
            num = 轉數值(m[1])
            p = m[2]
            return (num, p)

    def LAW3_FIRST_PARA(self, tok):
        pat = r"([壹貳參肆伍陸柒捌玖拾]+)、(.*)"
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

@cache.memoize(expire=30*24*60*60, tag='法規條文')
def 法規條文():
    df = 現行法規()
    df['法規分條'] = df.法規內容.map(法規分條)
    df = df.explode('法規分條')
    def 取條號(t):
        try:
            return t[0]
        except: return ''
    def 取條文內容(t):
        try:
            return t[1]
        except: return ''
    df['條號'] = df.法規分條.map(取條號)
    df['條文內容'] = df.法規分條.map(取條文內容)
    df.rename(columns={'修正日期':'異動日期'}, inplace=True)
    return df[['法規名稱', '異動日期', '條號', '條文內容']]

if __name__ == '__main__':
    c = 抓取(網址)
    print(取法規目錄頁數(c))
    print(取法規頁連結(c))
    # print(c)
