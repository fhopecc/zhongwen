def 取排程表達文字(dl):
    from zhongwen.時 import 取正式民國日期
    import pandas as pd
    tstr = ''
    if dl:
        tstr += 取正式民國日期(dl.start, 含星期=True)
        if dl.has_time():
            tstr += f'{dl.start:%H:%M}-{dl.end:%H:%M}'
    return tstr

def 取待辦事項(ds):
    '''
    一、取目錄下所有 org 之待辦事項。
    二、欄位：狀態、標題、期限
    三、按期限先後排序。
    '''
    from zhongwen.時 import 取正式民國日期, 取日期
    from tabulate import tabulate
    import pandas as pd
    import orgparse
    from collections.abc import Iterable 
    if isinstance(ds, str) or not isinstance(ds, Iterable):
        ds = [ds]
    
    表頭 = ['狀態', '標題', '期限', '排程']
    表身 = []
    for d in ds:
        for org in d.glob(r'**\*.org'):
            data = orgparse.load(org)    
            for node in data[1:]: # 遍歷所有點
                # 檢查是否為具 TODO 狀態之點)
                if node.todo:
                    # 提取資訊
                    status = node.todo          # 例如: TODO, DONE, STARTED
                    title = node.heading        # 標題內容
                    deadline = node.deadline
                    scheduled = node.scheduled
                    tags = node.tags            # 標籤集合 (set)
                    priority = node.priority    # 優先級 (A, B, C)
                    表身.append([status, title[:35], deadline, scheduled])  
    df = pd.DataFrame(表身, columns=表頭)
    df['key'] = df.期限.map(lambda d: 取日期(d.start, 無效值以今日填補=False)).fillna(
            df.排程.map(lambda d:取日期(d.start, 無效值以今日填補=False)))
    df = df.sort_values('key')
    del df['key']
    df['期限']= df.期限.map(取排程表達文字)
    df['排程']= df.排程.map(取排程表達文字)
    return df

def 顯示待辦事項(org):
    '顯示指定 org 之待辦事項'
    from tabulate import tabulate
    from zhongwen.時 import 取民國日期
    import orgparse

    表頭 = ['狀態', '標題', '期限']
    表身 = []

    data = orgparse.load(org)
    for node in data[1:]: # 遍歷所有點
        # 檢查是否為具 TODO 狀態之點)
        if node.todo:
            # 提取資訊
            status = node.todo          # 例如: TODO, DONE, STARTED
            title = node.heading        # 標題內容
            deadline = 取民國日期(node.deadline.start) if node.deadline else None
            tags = node.tags            # 標籤集合 (set)
            priority = node.priority    # 優先級 (A, B, C)

            # deadline_str = str(deadline.start) if deadline else "未設定"
            表身.append([status, title[:10], deadline])  
    print(tabulate(表身, 表頭))


def 取超文本(org, 預覽=True) -> str: 
    '''
    一、傳回表達指定 org 文件之超文本字串。
    二、預設以系統browser預覽。
    '''
    from zhongwen.時 import 今日
    from pathlib import Path
    import subprocess
    import tempfile
    import time
    import os
    org = Path(org)
    try:
        command = ['pandoc'
                  ,str(org)
        ]
        command = ' '.join(command)
        result = subprocess.run(command
                               ,capture_output=True
                               ,text=True
                               ,check=True
                               ,encoding='utf-8')
        內容 = f'''<html>
</head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7516968926110807" crossorigin="anonymous"></script>
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
{result.stdout}
</html>
'''
    except FileNotFoundError:
        print("找不到 'pandoc' 命令，請確認已安裝並設定環境變數！")
        return None
    except subprocess.CalledProcessError as e:
        print(f"執行 pandoc 時發生錯誤：{e}")
        return None

    if 預覽:
        with tempfile.TemporaryDirectory() as tmpdirname:
            html = os.path.join(tmpdirname, "tempfile.html")
            content = Path(html).write_text(內容, encoding='utf8') 
            os.system(f'start {html}')
            time.sleep(10)
    return 內容

def 取一階節點(org, 節點序號):
    '取指定一階節點'
    import re
    import sys
    with open(str(org), 'r', encoding='utf-8') as f:
        content = f.read()

    # 正規表示式解析：
    # ^\* +   : 行首必須是一顆星加空格（一階節點）
    # (.*?)   : 標題文字（非貪婪匹配）
    # (?=\n\* +|\Z) : 停止點：遇到下一行的一階節點，或是檔案結尾 (\Z)
    # flags=re.DOTALL : 讓點號 (.) 包含換行符
    pattern = re.compile(r'(^\* +.*?(?=\n\* +|\Z))', re.MULTILINE | re.DOTALL)
    
    nodes = pattern.findall(content)

    if 1 <= 節點序號 <= len(nodes):
        return nodes[節點序號 - 1]
    else:
        print(f"Error: 找不到第 {節點序號} 個節點 (總共有 {le節點序號(nodes)} 個)", file=sys.stderr)
        return None

def org2docx(org, 節點序號=0):
    '節點序號 0 指取全部節點。'
    from zhongwen.數 import 取中文數字, 取大寫中文數字
    from docx import Document
    from pathlib import Path
    import re
    import os
    org = Path(org)
    if 節點序號 > 0:
        原始檔 = org
        節點內容 = 取一階節點(org, 節點序號)
        org = org.with_stem(f'{org.stem}_{節點序號}')
        org.write_text(節點內容, encoding='utf8')
    docx = org.with_suffix('.docx')
    temp = Path(__file__).parent / r'resource\審核報告範本.docx'
    cmd = f'pandoc -f org+east_asian_line_breaks -t docx '
    cmd += f'--reference-doc="{temp}" --number-sections '
    cmd += f'-o "{docx}" {org}'
    os.system(cmd)
    document = Document(str(docx))

    def 取中文階層編號(編號, 階層):
        if 階層==0:
            return ''
        if 階層==1:
            return f'{取大寫中文數字(編號)}、'
        elif 階層==2: 
            return f'{取中文數字(編號)}、'
        elif 階層==3: 
            return f'({取中文數字(編號)})'
        elif 階層==4: 
            return f'{編號}.'
        elif 階層==5: 
            return f'({編號})'
        return 編號

    階層 = 0
    for paragraph in document.paragraphs:
        print(paragraph.style.name)
        if m:='Heading' in paragraph.style.name:
            runs = list(paragraph.runs)
            if len(runs) > 0 and (number_run:=runs[0]):
                text = number_run.text
                pat = r'^((\d+.)*(\d+))$'
                if m:=re.match(pat, text):
                    階層 = m[1].count('.')
                    編號 = 取中文階層編號(m[3], int(階層))
                    number_run.text = text.replace(m[1], 編號)
        if 'Normal' in paragraph.style.name or 'Body Text' in paragraph.style.name:
            if int(階層)>0:
                print(f'{階層} -> 內文{階層+1}')
                paragraph.style = f'內文{階層+1}'
    document.save(str(docx))
    os.system(f'start {docx}')

if __name__ == '__main__':
    from fhopecc.洄瀾打狗人札記 import 張貼
    from zhongwen.表 import 表示
    from pathlib import Path
    import socket
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="輸入路徑 f 之 org")
    parser.add_argument("-d", "--dirs", type=Path, nargs="+", help="輸入 dir 目錄內所有 org")
    parser.add_argument('-n', '--node', type=int, help='指定要處理之節點')
    parser.add_argument("-w", "--docx", action='store_true', help="匯出成 docx")
    parser.add_argument("-t", "--todo", action='store_true', help="列出待辦事項")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
    elif args.todo:
        if args.dirs:
            todos = 取待辦事項(args.dirs)
        else:
            todos = 取待辦事項(Path.cwd())
        # 表示(todos, 顯示索引=False)
        df, _ = 表示(todos, 顯示索引=False, 不顯示=True)
        if socket.gethostname() == 'LAPTOP-6J3H5COA':
            張貼('待辦事項', df.to_html())
    elif f := args.file:
        if args.docx:
            if args.node:
                org2docx(f, args.node)
            else:
                org2docx(f)
        else:
            取超文本(f)
