from zhongwen.pandas_tools import read_docx, read_fwf, show_html
from zhongwen.pandas_tools import 可顯示

def read_mhtml(mhtml:str):
    from pathlib import Path
    import pandas as pd 
    import email
    
    # 解析 mhtml 文件
    msg = email.message_from_string(mhtml)
    html_content = ""

    # 遍歷 mhtml 文件的內容，提取 HTML 部分
    for part in msg.walk():
        if part.get_content_type() == "text/html":  # 確認是 HTML 部分
            html_content = part.get_payload(decode=True).decode('utf-8')
            break
    # 使用 pandas 讀取 HTML 表格
    return pd.read_html(html_content)

def 取表(字串:str):
    import re
    s = 字串
    pat = r'-[- ]+' # 形式如--- ----- ----
    欄 = None
    if m:=re.search(pat, s):
        欄 = 取欄(m[0])
    ls = s.splitlines() 
    return ls[0] 

def 取字塊(字串:str):
    s = 字串
    p = 0 # 表位置，即 position 簡寫。
    in_block = False
    b = '' # 表字塊，即 block 簡寫。
    bs = []
    start = -1
    end = -1
    for c in s:
        if not c.isspace():
            b += c
            if not in_block:
                start = p
                in_block = True
        else:
            if in_block:
                end = p
                bs.append((b, start, end))
                b = ''
                in_block = False
        p += 字寬(c)
    if in_block:
        end = p
        bs.append((b, start, end))
        b = ''
        in_block = False
    return bs

def 取欄(字串:str):
    import re
    s = 字串
    pat = r'-+'
    cs = []
    for m in re.finditer(pat, s):
        cs.append((m[0], m.start(), m.end()))
    return cs

def 字寬(字元):
    import re
    char = 字元
    return 2 if re.match(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', char) else 1
