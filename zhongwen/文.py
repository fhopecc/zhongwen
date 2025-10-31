from zhongwen.text import 刪空格, 轉樣式表字串
from diskcache import Cache
from pathlib import Path
import functools

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

倉頡字根表 = str.maketrans("abcdefghijklmnopqrstuvwxy"
                          ,"日月金木水火土竹戈十大中一弓人心手口尸廿山女田難卜" )

@functools.cache
def 取停用詞():
    import pandas as pd
    return pd.read_csv(Path(__file__).parent / 'resource' / '停用詞.csv')

@functools.cache
def 取分隔詞模式(程式語言=None):
    if 程式語言=='vim':
        return python_re_to_vim_magic(取分隔詞模式())
    df = 取停用詞()
    pat = df.iloc[:, 0].values
    pat = '|'.join(pat)
    return rf"(?:[\uff00-\uffef\u3000-\u303f\s,.?;:/\\\"'|~!@#$%^&*()\[\]{{}}\=\+\-]|{pat})+"

@functools.cache
@cache.memoize('取倉頡碼')
def 取倉頡碼(字元=None):
    from zhongwen.檔 import 下載
    from pandas import read_csv

    if 字元:
        return 取倉頡碼().get(字元, [字元])
    try:
        f = 下載('https://github.com/Jackchows/Cangjie5/raw/master/Cangjie5_TC.txt')
    except Exception as e:
        print(f'下載倉頡碼表發生錯誤如次：{e}，改用內建碼表。')
        f = Path(__file__).parent / r'resource\Cangjie5_TC.txt'

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
    d = {}
    for index, row in df.iterrows():
        if not row['漢字'] in d:
            d[row['漢字']] = row['倉頡碼']
    return d

def 首碼搜尋表示式(char, text):
    cs = set()
    for i, c in enumerate(text):
        if c == char or 取倉頡碼(c)[0] == char:
            cs.add(c)
    return f'[{"".join(cs)}]'


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
        f = Path(__file__).parent / r'resource\Cangjie5_TC.txt'
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

def 取最近詞首(字串, 欄數):
    import re
    text = 字串
    column = 欄數
    if column <= 0 or column > len(text):
        return None
    sub_text = text[0:column]

    pattern = r'(\w+)\W*$'
    
    match = re.search(pattern, sub_text)

    if match:
        return match.group(1)
    
    if re.search(r'\w$', sub_text) and not re.search(r'\W', sub_text):
         return sub_text
         
    return None

@functools.cache
def 取強調詞字首樹(文):
    '強調詞係以「」、【】、[]等符號所夾註之詞'
    from marisa_trie import Trie
    import re
    pat = r'「(.+?)」|【(.+?)】|\[(.+?)\]'
    return Trie([''.join(r) for r in re.findall(pat, 文)])

def 取強調詞補全選項(文:str, 行, 欄):
    '行及欄是以1起始'
    import re
    t = 取強調詞字首樹(文)
    l = 文.splitlines()[行-1]
    prefix = l[:欄]
    while prefix:
        if t.has_keys_with_prefix(prefix):
            cs = [{'word':c[len(prefix):], 'abbr':c, 'kind':'強調詞'} for c in t.keys(prefix)]
            return cs
        prefix = prefix[1:]
    return []

@functools.cache
def 取文內簡稱字首樹(文):
    from marisa_trie import Trie
    import re
    pat = r'\(下稱(.+?)\)'
    return Trie(re.findall(pat, 文))

def 取簡稱補全選項(文:str, 行, 欄):
    '行及欄是以1起始'
    import re
    t = 取文內簡稱字首樹(文)
    l = 文.splitlines()[行-1]
    prefix = l[:欄]
    while prefix:
        if t.has_keys_with_prefix(prefix):
            cs = [{'word':c[len(prefix):], 'abbr':c, 'kind':'簡稱'} for c in t.keys(prefix)]
            return cs
        prefix = prefix[1:]
    return []

@functools.cache
def 取詞字首樹(文):
    '找出字串詞。'
    from marisa_trie import Trie
    import re
    return Trie([w for w in re.split(取分隔詞模式(), 文) if len(w)>0])

def 取詞補全選項(文:str, 行, 欄):
    '行及欄是以1起始'
    import re
    t = 取詞字首樹(文)
    l = 文.splitlines()[行-1]
    # prefixes = re.split(取分隔詞模式(), l[:欄])
    # if prefixes and (prefix:=prefixes[-1]) and t.has_keys_with_prefix(prefix):
    #     return [{'word':c[len(prefix):], 'abbr':c, 'kind':'詞'} for c in t.keys(prefix)]
    prefix = l[:欄]
    while prefix:
        if t.has_keys_with_prefix(prefix):
            cs = [{'word':c[len(prefix):], 'abbr':c, 'kind':'詞'} for c in t.keys(prefix)]
            return cs
        prefix = prefix[1:]
    return []

@functools.cache
def 取英文單字首樹(文):
    '找出字串中包含英文單字，單字包含底線。'
    from marisa_trie import Trie
    import re
    pat = r'\b[a-zA-Z_-]+\b'
    return Trie(re.findall(pat, 文))

def 取英文單字補全選項(文:str, 行, 欄):
    '行及欄是以1起始'
    import re
    t = 取英文單字首樹(文)
    l = 文.splitlines()[行-1]
    pat = r'\b[a-zA-Z_-]+\b'
    prefixes = re.findall(pat, l[:欄])
    if prefixes and (prefix:=prefixes[-1]) and t.has_keys_with_prefix(prefix):
        return [{'word':c[len(prefix):], 'abbr':c, 'kind':'英文單字'} for c in t.keys(prefix)]
    return []

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

def 是否為中文字元(char:str):
    return '\u4e00' <= char <= '\u9fa5'

def 是否為中文符號(char:str):
    import re
    chinese_punctuation_pattern = re.compile(r'[\u3000-\u303F\uFF00-\uFFEF\u2000-\u206F]')
    return bool(re.match(chinese_punctuation_pattern, char))

def 是否為平假名(c:str):
    return "\u3041" <= c <= "\u3096"

def 是否為片假名(c:str):
    return "\u30A1" <= c <= "\u30F6"

def 是否為字元(c:str):
    import string
    # 檢查字元是否為符號
    if c in string.punctuation or 是否為中文符號(c) or c.isspace():
        return False
    return True

全型表 = {i: i + 0xFEE0 for i in range(0x21, 0x7F)}
全型表[0x20] = 0x3000
半型表 = {v: k for k, v in 全型表.items()}

def 轉全型(s):
    return s.translate(全型表)

def 轉半型(s):
    return s.translate(半型表).replace('—', '-')

重碼字 ='車路類例宅金易勒精神行煉練復療溜樓例列量料飯旅冷靈禮福利老六數歷里不拉簾來說度便力錄連年爐讀益'
重碼字+='立異理狀'
正體字 ='車路類例宅金易勒精神行煉練復療溜樓例列量料飯旅冷靈禮福利老六數歷里不拉簾來說度便力錄連年爐讀益'
正體字+='立異理狀'

def 是否為重碼字(字串:str):
    return 字串[0] in 重碼字 

def 校正中文字(字串:str):
    t = str.maketrans(重碼字, 正體字)
    return 字串.translate(t)

def 字元切換(string:str):
    '''就大小寫字母，舉如拉丁字母，進行大小寫切換；重碼字母進行校正；中文字母進行簡繁切換；日文字母平片假名切換；符號則為全半型轉換(Todo)。
'''
    from opencc import OpenCC
    if string == '': return string
    def switch_case(c:str):
        if c == '[': return '「'
        if c == ']': return '」'

        if 是否為重碼字(c):
            return 校正中文字(c)

        if 是否為中文字元(c):
            # 簡繁切換
            r = OpenCC('s2t').convert(c)
            if r == c:
                return OpenCC('t2s').convert(c)
            return r
        if 是否為平假名(c):
            return chr(ord(c)-0x3041+0x30A1)
        if 是否為片假名(c):
            return chr(ord(c)-0x30A1+0x3041)
        if c.islower():
            return c.upper()
        else:
            return c.lower()

    if len(string) == 1: return switch_case(string)

    return ''.join(map(switch_case, string))

def 翻譯(word):
    from pygtrans import Translate
    client = Translate()
    # 翻译句子
    text = client.translate(word, 'zh-tw')
    return text.translatedText

def 安裝雅黑混合字型():
    import win32gui
    def callback(font, tm, fonttype, names):
        names.append(font.lfFaceName)
        return True
    fontnames = []
    hdc = win32gui.GetDC(None)
    win32gui.EnumFontFamilies(hdc, None, callback, fontnames)
    win32gui.ReleaseDC(hdc, None)
    字型已安裝 = "Microsoft YaHei Mono" in fontnames

    if 字型已安裝:
        print('雅黑混合字型已安裝！')
        return 
    from pathlib import Path
    font = Path(__file__).parent.parent / 'font' / 'MSYHMONO.ttf'
    cmd = f'''$FONTS = 0x14
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)
$objFolder.CopyHere("{font}")
'''
    import subprocess
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    if result.returncode !=0:
        raise WindowsError(f'執行 powershell 發生錯誤：{result}；指令{cmd}')
    print(f'安裝雅黑混合字型完成!')

def 設定環境():
    from zhongwen.windows import 建立傳送到項目
    import sys
    cmd = f'cmd.exe /c "{sys.executable} -m zhongwen.文 -o -c -f %* || pause"'
    建立傳送到項目('轉錄至文檔', cmd)

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

def python_re_to_vim_magic(py_pattern: str) -> str:
    """
    將 Python re (PCRE 風格) 的正規表示式轉換為 Vim (magic 風格)。

    Vim magic 模式需要轉義的特殊字符：() + ? | {} <>
    注意：此函數假設輸入的 Python 模式是有效的。

    Args:
        py_pattern: Python re 模組使用的正規表示式字串。

    Returns:
        適用於 Vim magic 模式的正規表示式字串。
    """
    import re
    vim_pattern = py_pattern.replace('(', r'\(')
    vim_pattern = vim_pattern.replace(')', r'\)')
    
    vim_pattern = vim_pattern.replace('+', r'\+')
    vim_pattern = vim_pattern.replace('?', r'\?')

    vim_pattern = vim_pattern.replace('|', r'\|')

    vim_pattern = vim_pattern.replace('{', r'\{')
    vim_pattern = vim_pattern.replace('}', r'\}')
    
    vim_pattern = vim_pattern.replace(r'\(?:', r'\%(')
    vim_pattern = vim_pattern.replace(r'\)', ')') # 臨時還原 \)
    vim_pattern = vim_pattern.replace(r'\%()', r'\%(\)') # 重新轉義
    
    vim_pattern = py_pattern
    
    def escape_vim_char(match):
        char = match.group(0)
        if char in '()|?+{}<>':
            return r'\%s' % char
        return char

    replacements = {
        '(': r'\(', ')': r'\)', 
        '+': r'\+', '?': r'\?', 
        '|': r'\|', 
        '{': r'\{', '}': r'\}',
        '\\': r'\\', # 確保反斜線本身被保留
    }

    for py_char, vim_char in replacements.items():
        # 注意：這是一個簡化處理，無法區分字元集 [] 內外
        # 在實際使用中，如果遇到問題，需要寫更複雜的狀態機或使用 regex 進行非捕獲判斷
        vim_pattern = vim_pattern.replace(py_char, vim_char)

    # 處理非捕獲群組 (?:...) -> \(\) (忽略非捕獲特性，轉為標準群組)
    vim_pattern = vim_pattern.replace(r'\(?:', r'\(')

    return vim_pattern.replace(r'\\', r'\\\\') # 確保反斜線在輸出時被正確表示
