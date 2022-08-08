'''花蓮縣政府主管法規資料'''

def 爬取法規():
    from pathlib import Path
    from zhongwen.file import 下載
    cached = Path.home() / 'temp' / 'hllaw'
    url = 'https://glrs.hl.gov.tw/glrsout/index.aspx'
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time
    options = Options()
    options.add_argument("--disable-notifications")
    chrome = webdriver.Chrome(executable_path='c:\\Python\\Python310\\chromedriver.exe'
                             ,chrome_options=options)
    chrome.get(url)
    h = chrome.page_source
    return False

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
from bs4 import BeautifulSoup as bs


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

