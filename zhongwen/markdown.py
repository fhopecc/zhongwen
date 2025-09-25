from pathlib import Path 
import os

def 網頁表達(檔名, 覆寫=True): 
    from zhongwen.時 import 今日
    from pathlib import Path
    import pypandoc
    import tempfile
    import time
    檔名 = Path(檔名)
    網頁區 = Path
    模板目錄 = Path(__file__).parent
    # env = Environment(loader=FileSystemLoader(模板目錄))
    # template = env.get_template('一般模版.html')
    內容 = pypandoc.convert_file(str(檔名), 'html'
                                ,format='markdown+east_asian_line_breaks'
                                ,extra_args=['--mathjax', '--number-sections']
                                ) 
    with tempfile.TemporaryDirectory() as tmpdirname:
        html = os.path.join(tmpdirname, "tempfile.html")
        content = Path(html).write_text(內容, encoding='utf8') 
        os.system(f'start {html}')
        time.sleep(10)
    return html

if __name__ == '__main__':
    from pathlib import Path
    # md = Path(r'D:\GitHub\fhopecc.github.io\notes\破解 WIFA WPA 密碼.html')
    網頁表達('g:\我的雲端硬碟\股票分析\文件\凌陽創新.md')
    # os.system(f'start "" "{md}"')
