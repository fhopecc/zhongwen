from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

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

def 取筆記本源碼(ipynb):
    '取 Jupyter Notebook 之源碼。'
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
