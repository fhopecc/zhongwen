from zhongwen.程式 import 通知執行時間
from pathlib import Path
from diskcache import Cache
import logging

logger = logging.getLogger(Path(__file__).stem)

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 取最新檔(檔案清單):
    from pathlib import Path
    import os
    檔案清單 = list(檔案清單)
    try:
        return max(檔案清單, key=os.path.getmtime)
    except:
        raise FileNotFoundError(檔案清單)

def 取檔名補全選項(文:str, 行, 欄, 工作目錄=None, debug=False):
    '行及欄是以1起始'
    from glob import glob
    l = 文.splitlines()[行-1]
    prefix = l[:欄]
    while prefix:
        if debug: print(prefix)
        if (p:=Path(prefix)).exists():
            cs = [c + ('\\' if Path(c).is_dir() and c[-1] != '\\' else '')
                  for c in glob(rf"{prefix}*")]
            cs = [{'word':c[len(prefix):], 'abbr':c
                  ,'kind': '目錄' if Path(c).is_dir() else '檔案'
                  } for c in cs]
            if len(cs)>0:
                cs = sorted(cs, key=lambda p: (p['kind'], p['abbr']))
                return cs
        elif 工作目錄 and (p:=Path(工作目錄)).exists():
            try:
                cs = [c.name + ('\\' if Path(c).is_dir() else '')
                      for c in p.glob(rf"{prefix}*")]
                cs = [{'word':c[len(prefix.split('\\')[-1]):], 'abbr':c
                      ,'kind': '目錄' if (p / c).is_dir() else '檔案'
                      } for c in cs]
                if len(cs)>0:
                    cs = sorted(cs, key=lambda p: (p['kind'], p['abbr']))
                    return cs
            except NotImplementedError:
                # 如在 Windows 系統且模式第2字元是:，如 "顯:日月"，
                # 因為 Windows 路徑係以磁碟機代號加:，前開模式會視為
                # 顯 磁碟機之絕對路徑，引發執行未實作非相對路徑模式錯誤，
                # 爰不作處理。
                pass
        prefix = prefix[1:]
    return []

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
    ''' 
一、抓取超連結內容字串。
二、抓取方式選項：get 使用 requests.get、post 使用 requests.post、selenium 使用 selenium 模組。
二、回傳資料形態選項如次：
    str      字串
    json     JSON 物件
    bytes    位元組
    StringIO StringIO。
三、超連結以 .xls 或 .xlsx 結尾之 Excel 檔則傳回位元組。
四、另再就抓取網頁內容之鏈結再進行抓取者，稱「爬取」。
五、會話識別網址：針對以會話識別防止爬蟲之網站，可指定本網址以連結取得會話識別後賡續爬取；如指定「網站網址」字串即網址中網站網址部分。
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
        # fake = Faker()
        # headers = {'user-agent': fake.user_agent()
                  # ,"accept-language": "zh-TW,zh;q=0.9,en;q=0.8,zh-CN;q=0.7"
                  # }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.tpex.org.tw/zh-tw/afterTrading/dailyQuotes.html',
            'X-Requested-With': 'XMLHttpRequest'
        }
    r = requests.session()
    if 會話識別網址=='網站網址':
        p = urlparse(url)
        會話識別網址 = f"{p.scheme}://{p.netloc}"

    if 會話識別網址:
        r = requests.get(會話識別網址, headers=headers, verify=False)
        # r = requests.get(會話識別網址, headers=headers)

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

def 下載(url, 儲存路徑=None, 儲存目錄=None, 覆寫=False) -> "pathlib.Path":
    '下載 URL 內容至指定檔案，並且回傳檔案路徑。'
    from pathlib import Path
    from urllib.parse import urlparse
    import requests

    p = 儲存路徑
    downloads = 儲存目錄

    # 1. 確保目錄與路徑處理正確
    if not downloads:
        downloads = Path.home() / 'Downloads'
        downloads.mkdir(exist_ok=True)
    else:
        downloads = Path(downloads) # 確保傳入的字串能轉為 Path 物件
        
    fn = urlparse(url).path.split('/')[-1] or "downloaded_file"
    if not p:
        p = downloads / fn
    else:
        p = Path(p)

    # 2. 檢查檔案是否存在
    if not 覆寫 and p.exists(): 
        logger.warning(f'警告：[{url}]已下載至[{p}]！')
        return p

    if p.exists():
        p.unlink()

    # 3. SSL 憑證彈性處理與串流(Stream)設定
    session_kwargs = {"stream": True, "timeout": 30} # 加入 timeout 防止連線卡死
    try:
        response = requests.get(url, **session_kwargs)
    except requests.exceptions.SSLError:
        import certifi
        try:
            response = requests.get(url, verify=certifi.where(), **session_kwargs)
        except requests.exceptions.SSLError:
            response = requests.get(url, verify=False, **session_kwargs)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"{url}下載失敗，係網路連線異常: {e}")

    # 4. 分段串流下載，解決 100MB zip 下載不完整的問題
    if response.status_code == 200:
        try:
            with open(p, 'wb') as file:
                # 每次只讀取 1MB 寫入硬碟，省記憶體且穩定
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk: 
                        file.write(chunk)
            logger.info(f'下載[{url}]至[{p}]成功！')
        except Exception as e:
            if p.exists(): p.unlink() # 若中途斷線或寫入失敗，刪除殘缺的檔案
            raise RuntimeError(f"檔案寫入失敗: {e}")
    else:
        raise RuntimeError(f"{url}下載失敗，原因：狀態碼 {response.status_code}, {response.reason}")
        
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
            raise IOError(f'{壓縮檔.filename}非ZipFile格式')
    壓縮檔.extractall(目錄)
    print(f'{壓縮檔.filename}解壓成功！')

模式集 ={"python":r'File "(?P<path>.+)", line (?P<line>\d+).*'
        ,"python_warn":r'^(?P<path>.+):(?P<line>\d+):.*'
        ,"python_debugger":r'^> (?P<path>.+)\((?P<line>\d+)\)'
        ,"path":r'(?P<path>[^"\']+\.(js|py))'
        }

def 取文檔位置(訊息):
    '萃取文字內之路徑資訊'
    import re 
    d = {'路徑':'', '列':0, '行':0}
    for k in 模式集:
        模式 = 模式集[k]
        if m:=re.search(模式, 訊息):
            try:
                d['路徑']= m['path']
                d['列'] = int(m['line'])
                d['行'] = int(m['pos'])
                break
            except IndexError:
                continue
    return d
