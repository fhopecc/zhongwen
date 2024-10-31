'檔案處理'
from zhongwen.batch_data import 通知執行時間
from functools import lru_cache
from diskcache import Cache
from pathlib import Path
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
            ,"python_debugger":r'^> (?P<path>.+.py)\((?P<line>\d+)\)'
            ,"jest":r'\((?P<path>.+\.js):(?P<line>\d+):(?P<pos>\d+)\)'
            ,"path":r'(?P<path>[^"\']+\.(js|py))'
            }
    def __init__(self, 訊息):
        import re 
        # if '股票估值' in 訊息:breakpoint()
        for k in self.模式集:
            模式=self.模式集[k]
            if m:=re.search(模式, 訊息):
                try:
                    self.路徑 = m['path']
                    self.列 = int(m['line'])
                    self.行 = int(m['pos'])
                    break
                except IndexError: pass
                break
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
def 抓取(url:str
        ,抓取方式='get'
        ,headers=None
        ,參數={}
        ,return_json=False
        ,return_content=False
        ,return_bytes=False
        ,除錯=False
        ,use_requests=None
        ,資料={}
        ,encoding="utf-8"
        ,等待秒數=5
        ):
    '''「抓取」網頁內容，傳回字串，惟鍵結以 .xls 或 .xlsx 結尾，視同 Excel 檔，傳回位元組。
另再就抓取網頁內容之鏈結再進行抓取者，稱「爬取」。
抓取方式：'get' 指定使用 requests.get；'post' 係 requests.post；'selenium' 係 selenium 模組。
'''
    from warnings import warn
    from faker import Faker
    import requests
    import logging
    import time

    # 鍵結以 .xls 或 .xlsx 結尾，視同 Excel 檔，傳回位元組。
    if not return_content:
        for suffix in ['.xls', '.xlsx']:
            if url.endswith(suffix):
                return_content=True
                break

    if 抓取方式=='request':
        warn(f'為強化命名，抓取方式參數之【request】選項將廢棄，請以【get】 替代。'
            ,DeprecationWarning, stacklevel=2)
        抓取方式='get'

    if 參數:
        warn(f'為強化命名，【參數】參數項將廢棄，請以【資料】替代。'
            ,DeprecationWarning, stacklevel=2)
        資料=參數

    if return_bytes:
        warn(f'為強化命名，【return_bytes】參數項將廢棄，請以【return_content】替代。'
            ,DeprecationWarning, stacklevel=2)
        return_content = return_bytes 

    if use_requests: 
        warn(f'預設使用【requests】模組，【use_request】參數項已無作用並將廢棄。'
            ,DeprecationWarning, stacklevel=2)

    if 抓取方式 == 'selenium':
        c = chrome()
        c.get(url)
        time.sleep(等待秒數)
        if '使用支援JavaScript' in c.page_source:
            c.get(url)
            time.sleep(等待秒數)
        return c.page_source
    if not headers:
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
    if return_content:
        return r.content
    return r.text

def 下載(url, 儲存路徑=None, 儲存目錄=None, 覆寫=False):
    '''下載 URL 內容至指定檔案，並且回傳檔案路徑。'''
    from urllib.parse import urlparse
    import requests
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
        logger.warn(f'警告：[{url}]已下載至[{p}]！')
        return p

    if p.exists():
        p.unlink()
    response = requests.get(url)
    if response.status_code == 200:
        with open(p, 'wb') as file:
            file.write(response.content)
        logger.info(f'下載[{url}]至[{p}]成功！')
    else:
        raise RuntimeError(r"{url}下載失敗，原因如次：", response.status_code, response.reason)
    return p

@通知執行時間
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

def 轉文字檔(filepath):
    from pathlib import Path
    import os
    output_txt = Path(filepath).with_suffix('.txt')
    cmd = f'pandoc -t plain "{filepath}" -o "{output_txt}"'
    os.system(cmd)
    return output_txt

def 複製檔案文字至剪貼簿(filepath):
    '複製檔案文字至剪貼簿'
    from pathlib import Path
    import clipboard
    filepath = Path(filepath)
    if filepath.suffix == '.txt':
        with open(filepath, 'r', encoding='utf8') as f:
            clipboard.copy(f.read())
    elif filepath.suffix == '.pdf':
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        clipboard.copy(text)
    else:
        textfile = 轉文字檔(filepath)
        複製檔案文字至剪貼簿(textfile)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--copytext", help='複製檔案文字至剪貼簿')
    parser.add_argument("--file2text", help='轉文字檔')
                       
    args = parser.parse_args()
    if file := args.copytext:
        複製檔案文字至剪貼簿(file)
    elif file := args.file2text:
        轉文字檔(file)
