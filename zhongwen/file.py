'檔案處理'
from pathlib import Path
from urllib import request
from urllib.parse import urlparse
from diskcache import Cache
from functools import lru_cache
import logging
cache = Cache(Path.home() / 'cache' / 'zhongwen.file')
logger = logging.getLogger(Path(__file__).stem)

def 轉換(來源:Path, 目的格式):
    '格式以副檔名推論'
    from pydub import AudioSegment
    s = 來源
    來源格式 = s.suffix
    t = s.with_suffix(目的格式)
    if s.suffix == '.aac':
        i = AudioSegment.from_file(s, format=s.suffix.replace('.', ''))
        if 目的格式 == '.mp3':
            o = i.export(t, format=目的格式.replace('.', ''))
            return t 
    raise NotImplementedError(f'尚未實作將{來源}轉換成{目的格式}格式功能')

class FileLocation:
    '萃取文字內之路徑資訊'
    模式集 ={"python":r'File "(?P<path>.+.py)", line (?P<line>\d+).*'
            ,"python_warn":r'^(?P<path>.+.py):(?P<line>\d+):.*'
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
    # from webdriver_manager.chrome import ChromeDriverManager
    # path = ChromeDriverManager().install()
    from selenium import webdriver
    return webdriver.Chrome()

# @cache.memoize(expire=100, tag='抓取')
def 抓取(url
        ,抓取方式='get'
        ,headers=None
        ,參數={}
        ,return_json=False
        ,return_bytes=False
        ,除錯=False
        ,use_requests=None
        ,資料={}
        ,encoding="utf-8"
        ):
    '''抓取網頁回傳原始碼，就已抓取網頁內容鏈結再抓取則稱為「爬取」。
抓取方式：'get' 指定使用 requests.get；'post' 係 requests.post；'selenium' 係 selenium 模組。
'''
    from warnings import warn
    if 抓取方式=='request':
        warn(f'為命名正確，參數選項「requests」將廢棄並由「get」取代。'
            ,DeprecationWarning, stacklevel=2)
        抓取方式='get'
    if use_requests: 
        warn(f'參數【use_request】將廢棄且已無作用，已預設使用 requests 模組。'
            ,DeprecationWarning, stacklevel=2)
    if 參數:
        warn(f'為命名正確，參數「參數」將廢棄並由「資料」取代。'
            ,DeprecationWarning, stacklevel=2)
        資料=參數

    import requests
    import logging
    if 抓取方式 == 'selenium':
        c = chrome()
        c.get(url)
        import time
        time.sleep(3)
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
        logging.debug(f'「資料」內容：{資料!r}')
        r = requests.post(url, headers=headers, data=資料)
    else:
        r = requests.get(url, headers=headers)
    r.encoding = encoding
    r.raise_for_status()  # 確保請求成功

    除錯訊息 = (f'回復內容為「{r!r}」：\n'
                f'{r.text!r}'
               )
    logging.debug(除錯訊息)
    if return_json:
        return r.json()
    if return_bytes:
        return r.content
    return r.text

def 下載(url, 儲存路徑=None, 儲存目錄=None, 覆寫=False):
    '''下載 URL 內容至指定檔案，並且回傳檔案路徑。'''
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
    import requests
    response = requests.get(url)
    if response.status_code == 200:
        with open(p, 'wb') as file:
            file.write(response.content)
        logger.info(f'下載[{url}]至[{p}]成功！')
    else:
        raise RuntimeError(r"{url}下載失敗，原因如次：", response.status_code, response.reason)
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
            raise IOError(f'{壓縮檔}非ZipFile格式')
    壓縮檔.extractall(目錄)
    print(f'解壓[{壓縮檔}]成功！')


def 下載跳出對話視窗連結檔案(url, 目錄=None):
    import requests
    from urllib.parse import urlparse
    import os
    
    response = requests.head(url)
    if 'Content-Disposition' in response.headers:
        content_disposition = response.headers['Content-Disposition']
        filename = content_disposition.split('filename=')[1].strip('"')
    else:
        filename = os.path.basename(urlparse(url).path)
    filepath = Path.home() / 'TEMP' / filename
    response = requests.get(url)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    logger.info(f'文件已下載到：{filepath}')
    return filepath

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    url = "https://www.chinesecj.com/forum/forum.php?mod=attachment&aid=NTc1NXxiNDlhMjUzZXwxNzEwNTAyMzc5fDB8MTk1MzIw"
    下載跳出對話視窗連結檔案(url)
