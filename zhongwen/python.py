from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 取錯誤位置清單(errmsg):
    """
    解析 Python Traceback 字串，並轉換為 Vim Quickfix 列表格式。
    Quickfix 條目格式: {'filename': path, 'lnum': lineno, 'text': message}
    """
    import re
    import json
    import sys
    quickfix_entries = []
    if isinstance(errmsg, str):
        lines = errmsg.split('\n')
    else:
        lines = errmsg
    # 正規表達式：匹配堆棧條目 (File "path", line num, in func)
    # 注意：在 Windows 路徑中，Python Traceback 仍使用 '\'，但需要轉義
    frame_pattern = re.compile(r'^\s*File\s+"(.+)",\s+line\s+(\d+)(.*)')
    
    current_frame = None
    
    for line in lines:
        line = line.strip()

        # 1. 匹配堆棧條目（File 行）
        match = frame_pattern.match(line)
        
        if match:
            # 找到新的堆棧條目
            if current_frame:
                # 處理上一個條目，加入 Quickfix 列表
                quickfix_entries.append(current_frame)

            # 初始化新的堆棧條目
            path, lineno, funcname = match.groups()
            current_frame = {
                # 替換 Windows 的 '\' 為 Quickfix 慣用的 '/'
                'filename': path.replace('\\', '/'), 
                'lnum': int(lineno),
                'text': f"Frame: in {funcname}", # 預設訊息
            }
            continue

        # 2. 處理錯誤訊息及上下文
        if current_frame:
            # 找到 NameError 或其他錯誤資訊行
            if re.match(r'^\w+Error:', line):
                # 這是錯誤類型和訊息 (e.g., NameError: name 'comp' is not defined)
                error_message = line
                current_frame['text'] = error_message
                
                # 這是堆棧追蹤的終點，處理完畢後將其加入並重置
                quickfix_entries.append(current_frame)
                current_frame = None 
                
            # 處理上下文/指示符行 (例如: self.assertEqual(w, comp) 或 ^^^^)
            elif not line.startswith('---'):
                if line:
                    # 將上下文訊息附加到 'text' 欄位
                    current_frame['text'] += f" | Context: {line}"

    # 3. 處理頂層 ERROR 訊息 (例如: ERROR: test取最近詞首...)
    if not quickfix_entries and lines:
        # 如果沒有堆棧條目（例如解析失敗或頂層錯誤），將其作為單獨的訊息
        header_text = lines[0].strip()
        quickfix_entries.append({
            'filename': 'Test Log',
            'lnum': 0, # 使用 0 表示沒有確切行號
            'text': header_text,
        })
    elif quickfix_entries and lines:
        # 如果有堆棧條目，將頂層 ERROR 訊息加到第一個條目的前綴
        error_header_match = re.match(r'ERROR:\s+(.+?)\s+\((.+?)\)', lines[0].strip())
        if error_header_match:
             quickfix_entries[0]['text'] = f"{error_header_match.group(0)} | {quickfix_entries[0]['text']}"

    return quickfix_entries

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
        msg = r'''Reading from channel output...
Reading from channel error...
  File "d:\github\vimchinese\plugin\python.vim", line 5
    def ExecutePython()
                       ^
SyntaxError: expected ':'
'''
        qf = 取錯誤位置清單(msg)
        # qf = 取錯誤位置清單(__file__)
        print(qf)
    else:
        pass
