'檔案處理'
from pathlib import Path
from urllib import request
from urllib.parse import urlparse
from diskcache import Cache
from functools import lru_cache
cache = Cache(Path.home() / 'cache' / 'zhongwen.file')

class FileLocation:
    '萃取文字內之路徑資訊'
    模式集 ={"python":r'File "(?P<path>.+.py)", line (?P<line>\d+).*'
            ,"jest":r'\((?P<path>.+\.js):(?P<line>\d+):(?P<pos>\d+)\)'
            ,"path":r'(?P<path>[^"\']+\.(js|py))'
            }
    def __init__(self, 訊息):
        for k in self.模式集:
            模式=self.模式集[k]
            import re 
            if m:=re.search(模式, 訊息):
                try:
                    self.路徑 = m['path']
                    self.列 = int(m['line'])
                    self.行 = int(m['pos'])
                    break
                except IndexError: pass
        if not hasattr(self, '路徑'): raise ValueError(f'訊息："{訊息}"不包含路徑資訊！')
        if not hasattr(self, '列'): self.列 = 0
        if not hasattr(self, '行'): self.行 = 0

def 最新檔(目錄, 檔案樣式="*"):
    import os
    fs = [f for f in 目錄.glob(檔案樣式)]
    try:
        return max(fs, key=os.path.getmtime)
    except:
        raise FileNotFoundError(目錄)

@lru_cache
def chrome():
    from webdriver_manager.chrome import ChromeDriverManager
    path = ChromeDriverManager().install()
    from selenium import webdriver
    return webdriver.Chrome()

# @cache.memoize(expire=100, tag='抓取')
def 抓取(url, 抓取方式='requests', 除錯=False, headers=None, use_requests=None, 參數={}) -> str:
    '''抓取網頁回傳原始碼。
抓取方式：'requests' 係指定使用 requests.get；'post' 係 requests.post；'selenium' 係 selenium 模組。
'''
    if use_requests: 
        from warnings import warn
        warn(f'參數【use_request】將廢棄且已無作用，已預設使用 requests 模組。', DeprecationWarning, stacklevel=2)
    import requests
    import logging
    if 抓取方式 == 'selenium':
        c = chrome()
        c.get(url)
        return c.page_source
    if not headers:
        from faker import Faker
        fake = Faker()
        headers = {'user-agent': fake.user_agent()
                  ,"accept-language": "zh-TW,zh;q=0.9,en;q=0.8,zh-CN;q=0.7"
                  }
        if 抓取方式=='post':
            headers["content-type"] = "application/x-www-form-urlencoded"
    if 抓取方式=='post':
        logging.debug(參數)
        r = requests.post(url, headers=headers, data=參數)
    else:
        r = requests.get(url, headers=headers)

    除錯訊息 = (f'回復內容為「{r!r}」：\n'
                f'{r.text!r}'
               )
    logging.debug(除錯訊息)

    return r.text

def 下載(url, 儲存路徑=None, 儲存目錄=None, 覆寫=False, selenium=False, 等待下載時間=20):
    '''下載 URL 內容至指定檔案，並且回傳檔案路徑。
如運用併發 selenium 子程序下載，且於子程序下載完成前提早結束返回，
則會中斷下載，須指定等待下載時間。
'''
    p = 儲存路徑
    downloads = 儲存目錄
    重載 = 覆寫

    if not downloads:
        downloads = Path.home() / 'Downloads'
        downloads.mkdir(exist_ok=True)
    fn = urlparse(url).path.split('/')[-1]
    if not p:
        p = downloads / fn

    if not 覆寫 and p.exists(): 
        print(f'警告：[{url}]已下載至[{p}]！')
        return p

    if p.exists():
        p.unlink()

    if selenium:
        c = chrome()
        c.get(url)
        from time import sleep
        sleep(等待下載時間) # 等待 chrome 下載完成
        print(f'下載[{url}]至[{p}]成功！')
    else:
        from urllib.request import urlopen
        with urlopen(url) as r, p.open('wb') as f:
            f.write(r.read())
            print(f'下載[{url}]至[{p}]成功！')
    return p

def 解壓(壓縮檔, 目錄):
    if 壓縮檔.suffix == '.7z':
        import py7zr
        壓縮檔 = py7zr.SevenZipFile(壓縮檔, mode='r')
    else:
        import zipfile
        try:
            壓縮檔 = zipfile.ZipFile(壓縮檔)
        except zipfile.BadZipFile:
            raise IOError(r'{壓縮檔}非ZipFile格式')
    壓縮檔.extractall(目錄)
    print(f'解壓[{壓縮檔}]成功！')
