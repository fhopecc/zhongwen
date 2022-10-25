from pathlib import Path
from diskcache import Cache
from bs4 import BeautifulSoup as bs
import re
cache = Cache(Path.home() / 'cache' / Path(__file__).name)

@cache.memoize(expire=30*24*60*60)
def 抓取法規(url):
    import requests
    url = 'https://law.nfa.gov.tw/mobile/law.aspx?LSID=FL005010'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52'
    response = requests.get(url, headers={ 'user-agent': user_agent })
    law = bs(response.text, 'lxml')
    law = law.select_one("#contenter")
    law = law.text
    pat = r'([一二三四五六七八九十]+)\s+'
    law = re.sub(pat, r'\1、', law)
    pat = r'\)\s+'
    law = re.sub(pat, r')', law)
    pat = r'\s+|檢視歷史法規'
    law = re.sub(pat, r'', law)
    return law

def 法規類別():
    from zhongwen.file import 抓取
    html = 抓取('https://law.nfa.gov.tw/mobile/category.aspx?typecode=A001')
    print(html)
