from zhongwen.text import 刪空格, 轉樣式表字串

def 設定環境():
    from zhongwen.winman import 建立傳送到項目
    import sys
    cmd = f'cmd.exe /c "{sys.executable} -m zhongwen.文 -o -c -f %* || pause"'
    建立傳送到項目('轉錄至文檔', cmd)

def geturl(文):
    '找出文中的 url，如找不到傳回空白'
    import re

    # 這個正規表達式能匹配大多數常見的 URL 格式
    # 它可以處理 http/https，以及網址結尾的各種符號
    # `[a-zA-Z0-9-.]` 處理域名中的字元
    # `[^\s()<>]+` 處理路徑中的字元，並排除括號
    url_pattern = re.compile(r'https?://[a-zA-Z0-9-.]+(?:/[^\s()<>]+|)')

    # 使用 findall 方法找出所有符合模式的 URL
    urls = url_pattern.findall(文)

    if urls:
        for url in urls:
            return url
    else:
        return ''

def 刪除空行(文):
    return "\n".join(line for line in 文.splitlines() if line.strip())

def 刪除中文字間空白(文):
    import re
    new_text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', 文)
    return new_text

def 臚列(項目):
    "['甲', '乙', '丙'] -> '甲、乙及丙'"
    項目 = [str(i) for i in 項目]
    if type(項目) == list:
        if len(項目) > 1:
            return f"{'、'.join(項目[:-1])}及{項目[-1]}" if len(項目) else ''
        return 項目[0]
    return 項目

def 刪除末尾句號(字串):
    from zhongwen.text import 去除字串末句號
    return 去除字串末句號(字串)

def 隨機中文(最大字串長度):
    import random 
    return ''.join(chr(random.randint(0x4E00, 0x9FA5)) 
              for _ in range(random.randint(1, 最大字串長度)))


def 臚列標題(文, 級別=3) -> str:
    """### 標題甲\n### 標題乙 -> 1.標題甲；2.標題乙
    """
    from zhongwen.數 import 取中文數字, 取數值
    import re
    級別 = 取數值(級別)
    pattern = re.compile(rf'^{"#" * 級別}\s+(.+)$')
    lines = 文.splitlines()
    
    results = []
    counter = 1
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            numbered = f"({取中文數字(counter)}){match.group(1)}"
            results.append(numbered)
            counter += 1
    
    return '；'.join(results)

def 合併(文檔集):
    merged_content = ""
    for filename in 文檔集:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content += f"###{filename}###\n{content}\n" 
            print(f"成功讀取檔案: {filename}")
        except FileNotFoundError:
            print(f"錯誤：找不到檔案 {filename}，已跳過。")
        except Exception as e:
            print(f"讀取檔案 {filename} 時發生錯誤: {e}")
    return merged_content

def 取完整路徑(檔案集):
    "處理檔案清單，並為沒有路徑的檔案加上當前目錄。"
    from pathlib import Path
    # 取得當前工作目錄的 Path 物件
    current_directory = Path.cwd()
    # 使用列表推導式來處理每個路徑
    full_paths = [
        # 建立一個 Path 物件
        Path(p) if Path(p).is_absolute() else current_directory / p
        for p in 檔案集
    ]
    return full_paths

def get_pandoc_text(source):
    import subprocess
    # 1. 使用 subprocess.run() 執行 Pandoc 指令
    # capture_output=True 會捕捉標準輸出
    # text=True 會將輸出解碼為文字，而不是二進位資料
    # encoding='utf-8' 確保以 UTF-8 編碼來處理輸出
    try:
        result = subprocess.run(
            ['pandoc', '-s', '-t', 'plain', f'{source}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return f"源檔：{source}\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        print(f"執行指令時發生錯誤：{e}")
        print(f"錯誤訊息：\n{e.stderr}")
    except FileNotFoundError:
        print("錯誤：Pandoc 未安裝或不在系統路徑中。")

def 轉錄文字(源檔集):
    from zhongwen.音 import 轉錄文字 as 音訊轉錄文字
    from zhongwen.office_document import get_doc_text
    from zhongwen.pdf import 取內文
    from pyperclip import paste
    import os
    源檔集 = 取完整路徑(源檔集)
    text = ''
    for s in 源檔集:
        if s.suffix == ".txt":
            text += s.read_text(encoding='utf8')
        elif s.suffix == ".docx":
            text += get_pandoc_text(s)
        elif s.suffix == ".doc":
            text += get_doc_text(s)
        elif s.suffix == ".pdf":
            text += 取內文(s)
        elif s.suffix == ".m4a":
            text += 音訊轉錄文字(s)
        else:
            text += "源檔：{s}尚無轉錄文字程式。"
        text += "\n\n"
    return text

if __name__ == "__main__":
    from pyperclip import copy
    from pathlib import Path
    from zhongwen.數 import 取中文數字
    import argparse
    parser = argparse.ArgumentParser()
    # parser.add_argument("file", help="Markdown 文件路径")
    # parser.add_argument("-l", "--level", type=int, default=3, 
    #                    help="标题级别 (1-6)，默认为3")
    # parser.add_argument("-s", "--separator", default="；",
    #                    help="输出分隔符，默认为中文分号")
    # parser.add_argument("-n", "--no-space", action="store_true",
    #                    help="序号后不加空格 (1.标题)")
    
    # args = parser.parse_args()
    
    # try:
    #     result = extract_and_number_headers(
    #         args.file,
    #         level=args.level,
    #         output_separator=args.separator
    #     )
        
    #     # 处理不加空格的情况
    #     if args.no_space:
    #         result = result.replace(". ", ".")
        
    #     print(result)
    # except Exception as e:
    #     print(f"错误: {e}")
    parser.add_argument('--setup', help="設定環境", action='store_true')
    parser.add_argument('--output', '-o', help="轉錄文字儲存至檔案" ,action='store_true')
    parser.add_argument('--clipboard', '-c', help="轉錄文字複製至剪貼簿", action='store_true')
    parser.add_argument('--files', '-f', nargs='+', help='指定欲轉錄文字之源檔集')
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif sources := args.files:
        text = 轉錄文字(sources)
        if args.clipboard:
            copy(text)
        if args.output:
            s1 = Path(sources[0])
            if len(sources) > 1:
                輸出文檔 = Path(s1).with_stem(f'{s1.stem[:6]}等{取中文數字(len(sources))}個文檔').with_suffix('.txt')
            else:
                輸出文檔 = Path(s1).with_suffix('.txt')
            with open(str(輸出文檔), 'w', encoding='utf-8') as out_f:
                out_f.write(text)
        print(f"{' '.join(sources)} =~->> {輸出文檔}")
