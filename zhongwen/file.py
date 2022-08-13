'檔案處理'
from pathlib import Path
from urllib import request
from urllib.parse import urlparse
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / 'zhongwen.file')

def 最新檔(目錄, 檔案樣式="*"):
    import os
    fs = [f for f in 目錄.glob(檔案樣式)]
    try:
        return max(fs, key=os.path.getmtime)
    except:
        raise FileNotFoundError(目錄)

@cache.memoize(expire=100, tag='抓取')
def 抓取(url):
    '抓取網頁回傳原始碼。'
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("--disable-notifications")
    chrome = webdriver.Chrome(executable_path='c:\\Python\\Python310\\chromedriver.exe'
                             ,chrome_options=options)
    chrome.get(url)
    return chrome

def 下載(url, p=None, downloads=None):
    '''下載 URL 的檔案至指定目錄 downloads，
並且回傳本地檔案的路徑。
'''
    if not downloads:
        downloads = Path.home() / 'Downloads'
    fn = urlparse(url).path.split('/')[-1]
    if not p:
        p  = downloads / fn
    if p.exists(): 
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