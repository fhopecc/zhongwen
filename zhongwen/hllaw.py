'花蓮縣政府主管法規資料'
from bs4 import BeautifulSoup as bs
from zhongwen.file import 抓取
from pathlib import Path
from diskcache import Cache
import pandas as pd
import os
import re
cache = Cache(Path.home() / 'cache' / 'hllaw')

@cache.memoize(expire=90*24*60*60, tag='抓取法規')
def 抓取法規(網址):
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

@cache.memoize(expire=30*24*60*60, tag='法規')
def 法規():
    df = 爬取法規連結()
    df = pd.DataFrame([抓取法規(row['網址']) for i, row in df.iterrows()])
    return df

def 取連結(page_no) -> pd.DataFrame:
    url = f'https://glrs.hl.gov.tw/glrsout/?page={page_no}'
    text = 抓取(url)
    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)
    return df

@cache.memoize(expire=90*24*60*60, tag='爬取法規連結')
def 爬取法規連結():
    from io import StringIO
    url = 'https://glrs.hl.gov.tw'
    text = 抓取(url)
    pat = '(\d+)<div class="pageno hidden-xs"'
    if m:=re.search(pat, text):
        page_num = int(m[1])
    else:
        raise RuntimeError('法規主頁無頁數資訊。')

    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)

    df = pd.concat([df, *[取連結(page_no) for page_no in range(2, page_num+1)]])
    return df
