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
        內容 = result.stdout
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
    網頁表達('g:\我的雲端硬碟\股票分析\文件\凌陽創新.md')
