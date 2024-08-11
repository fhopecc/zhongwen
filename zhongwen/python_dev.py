'Python 開發工具'
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
    
    測試檔前綴 = '測試' if 是否為中文檔名(f.name) else 'test_' 

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
    r = 光標物件()
    if r:
        m = r.docstring()
        m = m.split("\n")
        import re
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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy2pypi"
                       ,help="布署至PyPI，執行目錄下應有 pyproject.toml 檔。"
                       ,action='store_true')
    parser.add_argument("--add2pythonpath"
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
