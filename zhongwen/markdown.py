def 網頁表達(md, 預覽=True): 
    '''
    一、傳回表達 markdown 文件網頁字串。
    二、預設會以 chrome 預覽。
    '''
    from zhongwen.時 import 今日
    from pathlib import Path
    import subprocess
    import tempfile
    import time
    import os
    md = Path(md)
    try:
        command = ['pandoc'
                  ,'-f markdown+east_asian_line_breaks'
                  ,'--mathjax'
                  ,'--number-sections'
                  ,str(md)
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
        print("錯誤：找不到 'pandoc' 命令。請確認已安裝並設定環境變數。")
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

if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="指定處理的 markdown 檔")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
    elif f := args.file:
        網頁表達(f) 
