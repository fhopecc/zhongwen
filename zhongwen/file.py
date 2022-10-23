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
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-notifications")
    from os import environ
    driverpath = Path(environ['TEMP']) / 'chromedriver.exe'
    chrome = webdriver.Chrome(executable_path=str(driverpath)
                             ,options=options)
    return chrome

@cache.memoize(expire=100, tag='抓取')
def 抓取(url):
    '抓取網頁回傳原始碼。'
    c = chrome()
    c.get(url)
    return c.page_source

def 下載(url, p=None, downloads=None, force=True):
    '''下載 URL 的檔案至指定目錄 downloads，
並且回傳本地檔案的路徑。
'''
    if not downloads:
        downloads = Path.home() / 'Downloads'
    fn = urlparse(url).path.split('/')[-1]
    if not p:
        p  = downloads / fn
    if not force and p.exists(): 
        print(f'警告：已下載[{url}]至[{p}]！')
        return p
    downloads.mkdir(exist_ok=True)
    with request.urlopen(url) as r, p.open('wb') as f:
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
            raise Error(r'{壓縮檔}非ZipFile格式')
    壓縮檔.extractall(目錄)
    print(f'解壓[{壓縮檔}]成功！')
