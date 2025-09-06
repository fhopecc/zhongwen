from pathlib import Path
from diskcache import Cache
from zhongwen.程式 import 通知執行時間
import logging

logger = logging.getLogger(Path(__file__).stem)

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 同步目錄(源, 終):
    '從源目錄備至終目錄'
    import shutil
    import os
    source_dir, dest_dir = 源, 終
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        dest_root = os.path.join(dest_dir, relative_path)
        if not os.path.exists(dest_root):
            os.makedirs(dest_root, exist_ok=True)
        # 同步文件
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            if not os.path.exists(dest_file) or \
               (os.path.getmtime(src_file) > os.path.getmtime(dest_file)):
                try:
                    shutil.copy2(src_file, dest_file)
                except PermissionError as e:
                    logger.error(e)

def 同步檔案(目錄甲, 目錄乙, 檔):
    """同步单个文件，基于最后修改时间"""
    from datetime import datetime
    import shutil
    import os
    source, target, filename = 目錄甲, 目錄乙, 檔
    source_path = os.path.join(source, filename)
    target_path = os.path.join(target, filename)
    
    # 如果源文件不存在而目标文件存在
    if not os.path.exists(source_path) and os.path.exists(target_path):
        shutil.copy2(target_path, source_path)
        print(f"从目标复制到源: {filename}")
        return
    
    # 如果目标文件不存在而源文件存在
    if os.path.exists(source_path) and not os.path.exists(target_path):
        shutil.copy2(source_path, target_path)
        print(f"从源复制到目标: {filename}")
        return
    
    # 如果两边都存在文件
    if os.path.exists(source_path) and os.path.exists(target_path):
        source_mtime = os.path.getmtime(source_path)
        target_mtime = os.path.getmtime(target_path)
        
        if source_mtime > target_mtime:
            shutil.copy2(source_path, target_path)
            print(f"更新目标文件: {filename} (源文件较新)")
        elif target_mtime > source_mtime:
            shutil.copy2(target_path, source_path)
            print(f"更新源文件: {filename} (目标文件较新)")
        else:
            print(f"文件已同步: {filename}")


@cache.memoize(expire=100, tag='抓取')
def 抓取(url:str
        ,抓取方式='get'
        ,headers=None
        ,回傳資料形態='str'
        ,參數=None
        ,除錯=False
        ,資料=None
        ,會話識別網址=None
        ,encoding="utf-8"
        ,等待秒數=5
        ,return_json=False
        ,return_content=False
        ,return_bytes=False
        ,use_requests=None
        ):
    '''「抓取」網頁內容，傳回字串，惟鍵結以 .xls 或 .xlsx 結尾，視同 Excel 檔，傳回位元組。
另再就抓取網頁內容之鏈結再進行抓取者，稱「爬取」。
會話識別網址：針對以會話識別防止爬蟲之網站，可指定本網址以連結取得會話識別後賡續爬取；如指定「網站網址」字串即網址中網站網址部分。
抓取方式：'get' 指定使用 requests.get；'post' 係 requests.post；'selenium' 係 selenium 模組。
回傳資料形態: 'str' 傳回字串、'json' 傳回 JSON 物件、'bytes' 傳回位元組及'StringIO' 傳回io。
'''
    from urllib.parse import urlparse
    from warnings import warn
    from faker import Faker
    from io import StringIO
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

    if 資料:
        warn(f'為強化命名，【資料】參數項將廢棄，請以【參數】替代。'
            ,DeprecationWarning, stacklevel=2)
        參數=資料

    if return_bytes:
        warn(f'【return_bytes】參數項將廢棄，請將【回傳資料形態】參數設定【bytes】值替代。'
            ,DeprecationWarning, stacklevel=2)
        回傳資料形態 = 'bytes'

    if return_content:
        warn(f'【return_content】參數項將廢棄，請將【回傳資料形態】參數設定【bytes】值替代。'
            ,DeprecationWarning, stacklevel=2)
        回傳資料形態 = 'bytes'

    if return_json:
        warn(f'【return_json】參數項將廢棄，請將【回傳資料形態】參數設定【json】值替代。'
            ,DeprecationWarning, stacklevel=2)
        回傳資料形態 = 'json'

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
    r = requests.session()
    if 會話識別網址=='網站網址':
        p = urlparse(url)
        會話識別網址 = f"{p.scheme}://{p.netloc}"

    if 會話識別網址:
        r = requests.get(會話識別網址, headers=headers, verify=False)

    if 抓取方式=='post':
        headers["content-type"] = "application/x-www-form-urlencoded"
    if 回傳資料形態=='json':
        headers["content-type"] = "application/json"

    if 'post' in 抓取方式:
        logging.debug(f'參數：{資料!r}')
        try:
            r = requests.post(url, headers=headers, data=參數)
        except requests.exceptions.SSLError:
            r = requests.post(url, headers=headers, data=參數, verify=False)
    else:
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.SSLError:
            r = requests.get(url, headers=headers, verify=False)


    r.encoding = encoding
    r.raise_for_status()  # 確保請求成功

    除錯訊息 = (f'回復內容為「{r!r}」：\n'
                f'{r.text!r}'
               )
    logging.debug(除錯訊息)

    if 回傳資料形態=='json':
        return r.json()
    elif 回傳資料形態=='bytes':
        return r.content
    elif 回傳資料形態=='StringIO':
        return StringIO(r.text)
    else:
        return r.text

def 下載(url, 儲存路徑=None, 儲存目錄=None, 覆寫=False):
    '''下載 URL 內容至指定檔案，並且回傳檔案路徑。'''
    from urllib.parse import urlparse
    from requests.exceptions import SSLError
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
    try:
        response = requests.get(url)
    except requests.exceptions.SSLError as e:
        import certifi
        try:
            response = requests.get(url, verify=certifi.where())
        except requests.exceptions.SSLError as e:
            response = requests.get(url, verify=False)
    
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


