'花蓮縣政府主管法規資料'
from bs4 import BeautifulSoup as bs
import pandas as pd
import os
from pathlib import Path
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / 'hllaw')

@cache.memoize(tag='爬取法規連結')
def 爬取法規連結():
    from zhongwen.file import 抓取
    from io import StringIO
    url = 'https://glrs.hl.gov.tw'
    text = 抓取(url)
    pat = '(\d+)<div class="pageno hidden-xs"'
    # print(text)
    # breakpoint()
    if m:=re.search(pat, text):
        page_num = int(m[1])
    else:
        raise RuntimeError('法規主頁無頁數資訊。')

    t = bs(text, 'lxml')
    trs = t.select('#all > table > tbody > tr')
    links = [tr.select('a')[0] for tr in trs]
    links = [{'名稱':link.text, '網址':link['href']} for link in links]
    df = pd.DataFrame(links)

    def 取連結(page_no) -> pd.DataFrame:
        url = f'https://glrs.hl.gov.tw?page={page_no}'
        text = 抓取(url)
        t = bs(text, 'lxml')
        trs = t.select('#all > table > tbody > tr')
        links = [tr.select('a')[0] for tr in trs]
        links = [{'名稱':link.text, '網址':link['href']} for link in links]
        df = pd.DataFrame(links)
        return df

    df = pd.concat([df, *[取連結(page_no) for page_no in range(2, page_num+1)]])
    # df = pd.read_html(StringIO(page))[0]
    return df

def dataframe():
    '''回傳花蓮縣政府法規資料集'''
    return pd.read_feather(r'data\花蓮縣政府主管法規.f')

def system_contains(s):
    '''法規體系包含指定字串 s。'''
    l = dataframe()
    return l[l.法規體系.str.contains(s)]

def contains(s):
    '''法規內容包含指定字串 s。'''
    return dataframe().query('法規.str.contains(@s, na=False)')

#分析法規頁
import pandas as pd
import requests
import re

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    #if isinstance(element, Comment):
    #    return False
    return True

def text_from_children(c):
    texts = c.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    # return u\" \".join(t.strip().replace('\\n'
    #                                   , '').replace('\\xa0', '').replace('\\r', '').replace('  ', ''
    #                                   ).replace(' ', ''
    #                                   ).replace('\\u3000', '') for t in visible_texts)

# url = 'http://glrs.hl.gov.tw/glrsout/LawContent.aspx?id=GL000950'
# p = bs(requests.get(url).text, 'lxml')
# c = p.select('#ctl00_cp_content_divContent')
# text_from_children(c[0])
# tds = list(map(lambda f: f.text.strip(), p.select('#content > div.text-con > table > * > td')))
# ths = list(map(lambda f: f.text.strip().replace('：', ''), p.select('#content > div.text-con > table > * > th')))
# v = dict(zip(ths, tds))
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--var", help="設定環境")
    args = parser.parse_args()
    if args.var:
        pass
    else:
        pass

    df = 爬取法規連結()

    df = df.iloc[:100]
    html = Path.home() / 'TEMP' / 'output.html'
    df.to_html(html)
    os.system(f'start {html}')
