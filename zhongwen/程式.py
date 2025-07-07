'程式開發工具'
from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

__函數執行時間表__ = []

def 通知執行時間(f):
    '''
    一、增加函數於執行完成於標準輸出執行耗費秒數功能，以讓使用者調效程式。
    二、以上並將函數及其執行時間寫入模組變數「函數執行時間表」，
        可在程式結束時，運用「列出函數執行時間表」將函數依執行時間由長至短列出。
    '''
    from functools import wraps
    from time import time
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        runtime = time()-ts
        __函數執行時間表__.append({"函數":f.__name__, "執行時間":runtime})
        logger.info(f'{f.__name__}費時{runtime:.2f}秒。')
        return result
    return wrap

def 列出函數執行時間表():
    from zhongwen.表 import 顯示
    import pandas as pd
    ts = pd.DataFrame(__函數執行時間表__)
    ts = ts.groupby('函數', as_index=False
                   ).執行時間.agg(平均執行時間='mean'
                                 ,執行次數='count'
                                 )
    ts['總執行時間'] = ts.平均執行時間 * ts.執行次數
    ts = ts.sort_values('總執行時間', ascending=False)
    ts = ts.reset_index(drop=True)
    ts.index = ts.index+1
    顯示(ts)

def 安裝程式(應用程式):
    from collections.abc import Iterable 
    import os
    if isinstance(應用程式, str) or not isinstance(應用程式, Iterable):
        應用程式 = [應用程式]
    for p in 應用程式:
        os.system(f'scoop install {p}')

def 專案根目錄(檔案:Path):
    p = 檔案
    while not(p.parent / 'pyproject.toml').exists():
        if p == p.parent:
            raise FileNotFoundError(f'【{檔案}】無專案目錄！')
        p = p.parent
    return p.parent

def 套件名稱(f):
    from toml import load
    t = load(f)
    return t['project']['name']

def 布署(檔案:Path=None):
    import os
    if 檔案:
       r = 專案根目錄(檔案)
       old_cwd = os.getcwd()
       os.chdir(str(r))
       布署()
       os.chdir(old_cwd)
    else:
        try:
            n = 套件名稱('pyproject.toml') 
            cmd =  f'del dist\* && py -m build && twine upload dist\* && '
            cmd += f'python -m pip install {n} -U && '
            cmd += f'python -m pip install {n} -U'
            os.system(cmd)
        except FileNotFoundError:
            logger.error(f'當前目錄 {os.getcwd()} 無 pyproject.toml 檔案！')

def 至():
    from zhongwen.file import FileLocation
    import vim
    line = vim.eval("getline('.')")
    錯誤位置 = FileLocation(line)
    vim.command(f"e +{錯誤位置.列} {錯誤位置.路徑}")

def find_testfile(f:Path, debug=True):
    '依據路徑推論測試檔位置'
    import re
    if not isinstance(f, Path): 
        f = Path(f)

    def 是否為中文檔名(檔名):
        from zhongwen.text import 是否為中文字元
        for c in 檔名:
            if 是否為中文字元(c): return True
        return False
    
    測試檔前綴 = '測' if 是否為中文檔名(f.name) else 'test_' 

    test = f
    pat = 測試檔前綴
    if m:=re.match(pat, test.name) and test.exists():
        return str(test) 

    test = f.parent.parent / 'tests' / f'{測試檔前綴}{f.name}'
    if test.exists(): return str(test) 

    test = f.parent / f'{測試檔前綴}{f.name}'
    if test.exists(): return str(test) 

    test = f.parent / 'tests' / f'{測試檔前綴}{f.name}'
    if test.exists(): return str(test) 

    test = f.parent.parent / f'{測試檔前綴}{f.name}'
    if test.exists(): return str(test) 
     
    test = f.parent / 'test.py'
    if test.exists(): return str(test) 

    test = f.parent.parent / f'{測試檔前綴}{f.parent.name}.py'
    if test.exists(): return str(test) 
    
    raise FileNotFoundError(f'{f.name}尚無測試檔！')

def 光標物件():
    '光標處Python物件'
    import vim, jedi
    f = vim.eval("expand('%')")
    c = '\n'.join(vim.current.buffer)
    script = jedi.Script(code=c, path=f)
    _a, l, c, _a, _a = map(lambda s: int(s), vim.eval('getcursorcharpos()'))
    try:
        return script.goto(l, c, follow_imports=True)[0]
    except IndexError: None

def 至定義():
    '至光標處Python物件之定義'
    import vim
    r = 光標物件()
    if r:
        p = r.module_path
        l = r.line
        c = r.column
        vim.command(f"e +{l} {p}")

def escape_vim_special_chars(text):
    import vim
    escaped_text = vim.eval('escape("' + text + '", "#")')
    return escaped_text

def 說明():
    import vim
    import re
    r = 光標物件()
    if r:
        m = r.docstring()
        m = m.split("\n")
        m = [_m.replace('"', '＂').replace("'", '＇') for _m in m]
        m = [f"'{_m}'" for _m in m]
        m = ','.join(m)
        m = f"[{m}]"
        # print(f"{m!r}")
        # m = escape_vim_special_chars(m)
        vim.command(f"call popup_atcursor({m}, {{}})")

def 當前目錄加入模組查找路徑():
    '因 Python 係命令提示字元之子行程，無法更改其環境變數，須重啟。'
    import os
    pythonpath = ";".join([str(Path(os.getcwd())), os.environ['PYTHONPATH']])
    os.system(f'setx PYTHONPATH {pythonpath}')

def setgit():
    import os
    cmd = 'git config --global core.quotepath off'
    os.system(cmd)

def 筆記本轉程式碼(ipynb):
    import nbformat

    ipynb = Path(ipynb)

    # 讀取 .ipynb 檔案
    with open(ipynb, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # 提取所有 code cells 的 Python 代碼
    code_cells = [cell['source'] for cell in notebook['cells'] if cell['cell_type'] == 'code']

    # 將代碼儲存到一個 .py 文件中
    with open(ipynb.with_suffix('.py'), 'w', encoding='utf-8') as f:
        for cell_code in code_cells:
            f.write(cell_code + '\n\n')


def 安裝套件(套件名稱):
    "安裝套件名稱指定之 Python 套件。"
    import subprocess
    import sys
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", 套件名稱],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"成功安裝 {套件名稱}！")
        print("標準輸出:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"安裝 {套件名稱} 失敗！")
        print("錯誤輸出:\n", e.stderr)
    except FileNotFoundError:
        print("錯誤: 找不到 'pip' 命令。請確認 Python 和 pip 已正確安裝並配置到 PATH。")
    except Exception as e:
        print(f"安裝 {套件名稱} 時發生未知錯誤: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deploy2pypi"
                       ,help="布署至PyPI，執行目錄下應有 pyproject.toml 檔。"
                       ,action='store_true')
    parser.add_argument("-a", "--add2pythonpath"
                       ,help="當前目錄加入模組查找路徑。"
                       ,action='store_true')
    parser.add_argument("--setgit"
                       ,help="設定 git 環境。"
                       ,action='store_true')
    args = parser.parse_args()
    if args.deploy2pypi:
        布署()
    elif args.add2pythonpath:
        當前目錄加入模組查找路徑()
    elif args.setgit:
        setgit()
    else:
        pass
