from zhongwen.text import 刪空格, 轉樣式表字串
from diskcache import Cache
from pathlib import Path
import functools
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)
倉頡字根表 = str.maketrans("abcdefghijklmnopqrstuvwxy"
                          ,"日月金木水火土竹戈十大中一弓人心手口尸廿山女田難卜" )

def 設定環境():
    from zhongwen.windows import 建立傳送到項目
    import sys
    cmd = f'cmd.exe /c "{sys.executable} -m zhongwen.文 -o -c -f %* || pause"'
    建立傳送到項目('轉錄至文檔', cmd)

@functools.cache
@cache.memoize()
def 取臺灣字頻序號(字=None):
    '''
    一、查詢指定字之臺灣字頻序號，即依字頻遞減排序號。
    二、未指定字則傳回臺灣字頻序號表，係以字為鍵而序號為值之 dict 物件。
    三、未列入統計字則傳回最大序號加一即 5732。 
    四、資料來源取自國語辭典簡編本編輯資料字詞頻統計報告，
　　    統計所得之單字數為 5731 字，頻次總數為 1982882 次。
    五、網址：(https://language.moe.gov.tw/001/Upload/files/SITE_CONTENT/M0001/PIN/F11.HTML)
    '''
    from zhongwen.表 import 顯示
    from pathlib import Path
    import pandas as pd
    if 字:
        try:
            return 取臺灣字頻序號()[字]
        except KeyError:
            return 5732
    f = Path(__file__).parent / r'resource\BIAU1.TXT'
    df = pd.read_csv(f) 
    print(df.shape)
    df = df.query("字.str.len()==1") # 排除如[口白]無造字，以雙字元表達字型者
    return dict(zip(df.字, df.字頻序號))
 
@functools.cache
@cache.memoize()
def 倉頡檢字(倉頡碼=None):
    '''
    一、查詢指定倉頡碼之候選字，並依碼長、字頻序號及候選字序遞增排序。
    二、倉頡碼可用倉頡字根或其對應英文字母指定。
    三、候選字為字及倉頡字根碼，如：張弓尸一女、簡竹日弓日
    四、未指定倉頡碼則傳回前綴樹，前綴樹值係倉頡字根碼加字。
    '''
    from zhongwen.檔 import 下載
    from pandas import read_csv
    from marisa_trie import Trie
    from pathlib import Path
    if 倉頡碼:
        倉頡碼 = 倉頡碼.translate(倉頡字根表)
        t : Trie = 倉頡檢字()
        return sorted([c[-1] + c[:-1] for c in t.keys(倉頡碼) if len(c) > len(倉頡碼)]
                     ,key = lambda s:(len(s), 取臺灣字頻序號(s[0]), s))
    try:
        f = 下載('https://github.com/Jackchows/Cangjie5/raw/master/Cangjie5_TC.txt')
    except Exception as e:
        print(f'下載倉頡碼表發生錯誤如次：{e}，改用內建碼表。')
        f = Path(__file__).parent / 'resource\Cangjie5_TC.txt'
    df = read_csv(f, encoding='latin1'
                 ,skiprows=12
                 ,sep='\t'
                 ,names=['漢字','倉頡碼','標註']
                 )
    def convert(latin1:str):
        try:
            return latin1.encode('latin1').decode('utf8', errors='replace') 
        except AttributeError:
            return latin1
    df['漢字'] = df.漢字.map(convert)
    df['倉頡碼字'] = df.倉頡碼.map(lambda s: s.translate(倉頡字根表))+df.漢字
    return Trie(df.倉頡碼字.tolist())

def geturl(文):
    '找出文中的 url，如找不到傳回空白'
    import re
    url_pattern = re.compile(r'https?://[a-zA-Z0-9-.]+(?:/[^\s()<>]+|)')
    urls = url_pattern.findall(文)
    if urls:
        for url in urls:
            return url
    else:
        return ''

def 刪除空行(文):
    return "\n".join(line for line in 文.splitlines() if line.strip())

def 刪除中文字間空白(文):
    import re
    new_text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', 文)
    return new_text

def 臚列(項目):
    "['甲', '乙', '丙'] -> '甲、乙及丙'"
    項目 = [str(i) for i in 項目]
    if type(項目) == list:
        if len(項目) > 1:
            return f"{'、'.join(項目[:-1])}及{項目[-1]}" if len(項目) else ''
        return 項目[0]
    return 項目

def 刪除末尾句號(字串):
    from zhongwen.text import 去除字串末句號
    return 去除字串末句號(字串)

def 隨機中文(最大字串長度):
    import random 
    return ''.join(chr(random.randint(0x4E00, 0x9FA5)) 
              for _ in range(random.randint(1, 最大字串長度)))


def 臚列標題(文, 級別=3) -> str:
    """### 標題甲\n### 標題乙 -> 1.標題甲；2.標題乙
    """
    from zhongwen.數 import 取中文數字, 取數值
    import re
    級別 = 取數值(級別)
    pattern = re.compile(rf'^{"#" * 級別}\s+(.+)$')
    lines = 文.splitlines()
    
    results = []
    counter = 1
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            numbered = f"({取中文數字(counter)}){match.group(1)}"
            results.append(numbered)
            counter += 1
    
    return '；'.join(results)

def 合併(文檔集):
    merged_content = ""
    for filename in 文檔集:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content += f"###{filename}###\n{content}\n" 
            print(f"成功讀取檔案: {filename}")
        except FileNotFoundError:
            print(f"錯誤：找不到檔案 {filename}，已跳過。")
        except Exception as e:
            print(f"讀取檔案 {filename} 時發生錯誤: {e}")
    return merged_content

def 取完整路徑(檔案集):
    "處理檔案清單，並為沒有路徑的檔案加上當前目錄。"
    from pathlib import Path
    # 取得當前工作目錄的 Path 物件
    current_directory = Path.cwd()
    # 使用列表推導式來處理每個路徑
    full_paths = [
        # 建立一個 Path 物件
        Path(p) if Path(p).is_absolute() else current_directory / p
        for p in 檔案集
    ]
    return full_paths

def get_pandoc_text(source):
    import subprocess
    # 1. 使用 subprocess.run() 執行 Pandoc 指令
    # capture_output=True 會捕捉標準輸出
    # text=True 會將輸出解碼為文字，而不是二進位資料
    # encoding='utf-8' 確保以 UTF-8 編碼來處理輸出
    try:
        result = subprocess.run(
            ['pandoc', '-s', '-t', 'plain', f'{source}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return f"源檔：{source}\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        print(f"執行指令時發生錯誤：{e}")
        print(f"錯誤訊息：\n{e.stderr}")
    except FileNotFoundError:
        print("錯誤：Pandoc 未安裝或不在系統路徑中。")

def 轉錄文字(源檔集):
    from zhongwen.音 import 轉錄文字 as 音訊轉錄文字
    from zhongwen.office_document import get_doc_text
    from zhongwen.pdf import 取內文
    from pyperclip import paste
    import os
    源檔集 = 取完整路徑(源檔集)
    text = ''
    for s in 源檔集:
        if s.suffix == ".txt":
            text += s.read_text(encoding='utf8')
        elif s.suffix == ".docx":
            text += get_pandoc_text(s)
        elif s.suffix == ".doc":
            text += get_doc_text(s)
        elif s.suffix == ".pdf":
            text += 取內文(s)
        elif s.suffix == ".m4a":
            text += 音訊轉錄文字(s)
        else:
            text += "源檔：{s}尚無轉錄文字程式。"
        text += "\n\n"
    return text

def escape_vim_string(s:str):
    return s.replace('\\', '\\\\')

if __name__ == "__main__":
    from pyperclip import copy
    from pathlib import Path
    from zhongwen.數 import 取中文數字
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', help="設定環境", action='store_true')
    parser.add_argument('--output', '-o', help="轉錄文字儲存至檔案" ,action='store_true')
    parser.add_argument('--clipboard', '-c', help="轉錄文字複製至剪貼簿", action='store_true')
    parser.add_argument('--files', '-f', nargs='+', help='指定欲轉錄文字之源檔集')
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif sources := args.files:
        text = 轉錄文字(sources)
        if args.clipboard:
            copy(text)
        if args.output:
            s1 = Path(sources[0])
            if len(sources) > 1:
                輸出文檔 = Path(s1).with_stem(f'{s1.stem[:6]}等{取中文數字(len(sources))}個文檔').with_suffix('.txt')
            else:
                輸出文檔 = Path(s1).with_suffix('.txt')
            with open(str(輸出文檔), 'w', encoding='utf-8') as out_f:
                out_f.write(text)
        print(f"{' '.join(sources)} =~->> {輸出文檔}")

def 去標籤(字串):
    import re
    字串 = 字串.replace('\u200b', '')
    字串 = 字串.replace('\xff', '')
    return re.sub(r'<.*?>', '', 字串)

class 萌典尚無定義之字詞(Exception):pass
def 查萌典(字詞):
    '傳回定義清單'
    from .檔 import 抓取
    import requests
    import logging
    import json
    url = f'https://www.moedict.tw/{字詞}.json'
    try:
        d = 抓取(url, return_json=True)
        hs = d['heteronyms']
        def 取定義(異名):
            h = 異名
            try:
                m = h['bopomofo']
                m += '：'
            except KeyError:
                m = ''
            ds = h['definitions']
            m += ''.join([去標籤(d["def"]) for d in ds])
            return m
        return [取定義(h) for h in hs]
    except (json.JSONDecodeError, requests.exceptions.HTTPError):
        raise 萌典尚無定義之字詞(字詞) 
