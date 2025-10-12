from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 取錯誤位置清單(errmsg):
    import re
    if isinstance(errmsg, list):
        errmsg = '\n'.join(errmsg)
    # 解析項目：1.檔名；2.行號；3.訊息。
    traceback_pattern = re.compile(r'^\s*File\s+"(.*?)",\s*line\s*(\d+)(.*)$')
    qf_list = []
    output_lines = errmsg.splitlines()

    # 用來儲存最後一行錯誤類型和訊息 (e.g. IndexError: list index out of range)
    final_error_message = "未知錯誤"

    # 1. 第一次迭代：找出所有的堆疊追蹤行
    for line in output_lines:
        match = traceback_pattern.search(line)
        if match:
            # 這是堆疊中的一個呼叫層
            file_path = match.group(1)
            line_num = int(match.group(2))
            text = match.group(3).strip()

            # 構建 QuickFix 項目
            qf_item = {
                'filename': file_path,
                'lnum': line_num,
                'text': text,
                'type': 'E'
            }
            qf_list.append(qf_item)
        elif qf_list and not line.strip().startswith('Traceback'):
            # 捕捉堆疊追蹤的最後一行 (實際的錯誤訊息)
            # 假設它是跟在堆疊行之後，且不以 'Traceback' 開頭
            if not re.match(r'^\s*$', line): # 忽略空白行
                final_error_message = line.strip()
    # 2. 如果成功解析了堆疊，將最終錯誤訊息加入到列表的第一個項目
    # 讓 QuickFix 視窗中的訊息更豐富
    if qf_list:
        # 將最底層（最近發生）的錯誤訊息，作為 QuickFix 列表中的第一條記錄
        qf_list[-1]['text'] = f"{final_error_message} (in {qf_list[-1]['text']})"
    return qf_list

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
            cmd =  rf'del dist\* && py -m build && twine upload dist\* && '
            cmd += rf'python -m pip install {n} -U && '
            cmd += rf'python -m pip install {n} -U'
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
    parser.add_argument("--test"
                       ,help="設定 git 環境。"
                       ,action='store_true')

    args = parser.parse_args()
    if args.deploy2pypi:
        布署()
    elif args.add2pythonpath:
        當前目錄加入模組查找路徑()
    elif args.setgit:
        setgit()
    elif args.test:
        # qf = 執行並取錯誤位置清單(r'd:\github\vimchinese\plugin\python.vim')
        qf = 執行並取錯誤位置清單(__file__)
        print(qf)
    else:
        pass
