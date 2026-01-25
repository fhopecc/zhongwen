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

def org2docx(org):
    from zhongwen.數 import 取中文數字, 取大寫中文數字
    from docx import Document
    from pathlib import Path
    import re
    import os
    org = Path(org)
    docx = Path(__file__).parent / org.with_suffix('.docx')
    temp = r'c:\GitHub\zhongwen\zhongwen\resource\審核報告範本.docx'
    # cmd = f'pandoc -f markdown+east_asian_line_breaks -t docx '
    cmd = f'pandoc -t docx '
    cmd += f'--reference-doc="{temp}" --number-sections '
    cmd += f'-o "{docx}" {org}'
    os.system(cmd)
    document = Document(str(docx))

    def 取中文階層編號(編號, 階層):
        # if 階層==0:
            # return ''
        if 階層==0:
            return f'{取大寫中文數字(編號)}、'
        elif 階層==1: 
            return f'{取中文數字(編號)}、'
        elif 階層==2: 
            return f'({取中文數字(編號)})'
        elif 階層==3: 
            return f'{編號}.'
        elif 階層==4: 
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
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="指定處理的 org 檔")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
    elif f := args.file:
        取超文本(f)
