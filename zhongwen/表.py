from zhongwen.pandas_tools import read_docx, read_fwf, show_html
from zhongwen.pandas_tools import 可顯示, 重名加序
from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

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

def 顯示(df
        ,整數欄位=[], 實數欄位=[], 百分比欄位=[]
        ,日期欄位=[], 隱藏欄位=[]
        ,漸層欄位=[]
        ,百分比漸層欄位=[]
        ,顯示筆數=100, 採用民國日期格式=False, 標題=None
        ,傳回超文件內容=False
        ,無格式=False
        ,不顯示=False
        ):
    from pathlib import Path
    import pandas as pd
    import numpy as np
    import tempfile
    import time
    import os

    if isinstance(df, list):
        df = pd.Series(df).to_frame()
    elif isinstance(df, set):
        df = pd.Series(list(df)).to_frame()
    elif isinstance(df, np.ndarray):
        df = pd.Series(df).to_frame()
    elif isinstance(df, pd.Series):
        df = df.to_frame()
    elif isinstance(df, pd.DataFrame):
        df = df.dropna(axis='columns', how='all')
        if not df.index.is_unique:
            df = df.reset_index(drop=True)
    if df.empty:
        logger.error('空表')
        return 

    df.reset_index(drop=True, inplace=True)
    df.columns.name = '編號'
    df.index = df.index+1

    df.dropna(how='all')
    df.dropna(how='all', axis=1)

    if not 無格式:
        from zhongwen.pandas_tools import 標準格式
        df = df.head(顯示筆數)

        整數欄位 = set(整數欄位).union(df.select_dtypes(include=['int']).columns)
        百分比欄位 = set(百分比欄位)
        實數欄位 = set(實數欄位).union(df.select_dtypes(include=['float']).columns)
        實數欄位 -= 整數欄位
        實數欄位 -= 百分比欄位
        百分比漸層欄位 = set(百分比漸層欄位).union(set(百分比欄位))
        漸層欄位 = set(漸層欄位).union(整數欄位, 實數欄位)
        漸層欄位 -= 百分比漸層欄位
        日期欄位 = df.select_dtypes(include=['datetime']).columns
        期間欄位 = [c for c in df.columns if 'period' in df.dtypes[c].name]
        文字欄位 = df.select_dtypes(include=['object']).columns
        
        df = df.style.map(lambda _:'text-align:right')
        df = df.map_index(lambda _:'text-align:center', axis=1)
        df = df.format('{:,.0f}', subset=list(整數欄位), na_rep='')
        df = df.format(lambda v: f"{v*100:.0f}", subset=list(百分比欄位), na_rep='')
        df = df.format('{:,.2f}', subset=list(實數欄位), na_rep='')
        df = df.format('{:%Y%m%d}', subset=日期欄位, na_rep='')
        df = df.format(str, subset=期間欄位, na_rep='')
        df = df.format(str, subset=文字欄位, na_rep='')
        df = df.background_gradient(axis=0, cmap='RdYlGn', vmax=1, vmin=-1
                                   ,subset=list(百分比漸層欄位)
                                   )
        df = df.background_gradient(axis=0, cmap='RdYlGn', subset=list(漸層欄位))
        df = df.hide(隱藏欄位, axis=1) # hide index
 
        tr_hover = {
            'selector': 'tr:hover',
            'props':[('background-color', '#ffffb3'), ('border-style', 'dotted')]
        }
        df = df.set_table_styles([tr_hover], overwrite=False)

    if 不顯示:
        return df

    with tempfile.TemporaryDirectory() as tmpdirname:
        html = os.path.join(tmpdirname, "tempfile.html")
        df.to_html(html)
        os.system(f'start {html}')
        time.sleep(1)
