from zhongwen.pandas_tools import read_docx, read_fwf, show_html
from zhongwen.pandas_tools import 重名加序
from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 取數據輪廓(df):
    import pandas as pd
    import numpy as np
    import pathlib
    import argparse
    from datetime import datetime
    results = []
    def get_top_n(series, n=5):
            """計算前 N 名出現頻率最高的數值與次數"""
            # 排除空值後進行計數
            counts = series.value_counts().head(n)
            if counts.empty:
                return "-"
            # 格式化為 "值:次數" 的字串列表
            return r"<br/>".join([f"{str(val)[:10]}:{count}" for val, count in counts.items()])
    for col in df.columns:
        series = df[col]
        # 基礎資訊

        try:
            唯一值數 = series.nunique()
        except:
            唯一值數 = np.nan

        info = {
            "欄位名稱": col,
            "資料型別": str(series.dtype),
            "總筆數": len(df),
            "空值數": series.isnull().sum(),
            "唯一值數": 唯一值數,
            "前五高頻值(值:次數)": get_top_n(series, 5)
        }

        # 數值型分析 (Numeric)
        if pd.api.types.is_numeric_dtype(series):
            info.update({
                "最大值": series.max(),
                "最小值": series.min(),
                "平均值": round(series.mean(), 2),
                "中位數": series.median(),
                "總計": series.sum(),
                "正值數": (series > 0).sum(),
                "負值數": (series < 0).sum(),
                "零值數": (series == 0).sum()
            })
        
        # 日期型分析 (Datetime)
        elif pd.api.types.is_datetime64_any_dtype(series):
            info.update({
                "最早日期": series.min(),
                "最晚日期": series.max(),
                "週末交易數": series.dt.dayofweek.isin([5, 6]).sum()
            })

        # 字串型分析 (Object/String)
        else:
            str_series = series.astype(str)
            info.update({
                "最大長度": str_series.str.len().max(),
                "平均長度": round(str_series.str.len().mean(), 2)
            })
        
        results.append(info)
    return pd.DataFrame(results)

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
        ,編號欄位=[]
        ,整數欄位=[], 實數欄位=[], 百分比欄位=[]
        ,日期欄位=[], 隱藏欄位=[]
        ,漸層欄位=[]
        ,指定漸層上下限欄位=[]
        ,漸層上限=None
        ,漸層下限=None
        ,百分比漸層欄位=[]
        ,百分比漸層按值區間欄位=[]
        ,顯示筆數=100, 採用民國日期格式=False, 標題=None
        ,傳回超文件內容=False
        ,顯示索引=True
        ,無格式=False
        ,不顯示=False
        ):
    from warnings import warn
    warn(f'【顯示】將廢棄，請使用【表示】', DeprecationWarning, stacklevel=2) 
    return 表示(df
        ,編號欄位
        ,整數欄位, 實數欄位, 百分比欄位
        ,日期欄位, 隱藏欄位
        ,漸層欄位
        ,指定漸層上下限欄位
        ,漸層上限
        ,漸層下限
        ,百分比漸層欄位
        ,百分比漸層按值區間欄位
        ,顯示筆數, 採用民國日期格式, 標題
        ,傳回超文件內容
        ,顯示索引
        ,無格式
        ,不顯示) 

def 表示(df
        ,編號欄位=[]
        ,整數欄位=[], 實數欄位=[], 百分比欄位=[]
        ,日期欄位=[], 隱藏欄位=[]
        ,漸層欄位=[]
        ,指定漸層上下限欄位=[]
        ,漸層上限=None
        ,漸層下限=None
        ,百分比漸層欄位=[]
        ,百分比漸層按值區間欄位=[]
        ,顯示筆數=100, 採用民國日期格式=False, 標題=None
        ,傳回超文件內容=False
        ,顯示索引=True
        ,無格式=False
        ,不顯示=False
        ):
    '''
    一、字串視為超文件檔案直接顯示；序列、系列、集合、陣列及資料框以表格顯示。
    二、如設不顯示，傳回樣式及可顯示資料框，可顯示資料框用來設定工具提示。
    '''
    from pathlib import Path
    import pandas as pd
    import numpy as np
    import tempfile
    import time
    import os
    if isinstance(df, str):
        df = '<meta charset="UTF-8">\n' + df
        with tempfile.TemporaryDirectory() as tmpdirname:
            html = os.path.join(tmpdirname, "tempfile.html")
            with open(html, 'w', encoding='utf8') as f:
                f.write(df)
            os.system(f'start {html}')
            time.sleep(2)
        return 

    if isinstance(df, list):
        df = pd.Series(df).to_frame()
        顯示索引 = True
    elif isinstance(df, set):
        df = pd.Series(list(df)).to_frame()
        顯示索引 = True
    elif isinstance(df, np.ndarray):
        df = pd.Series(df).to_frame()
        顯示索引 = True
    elif isinstance(df, pd.Series):
        df = df.to_frame()
        顯示索引 = True
    elif isinstance(df, pd.DataFrame):
        df = df.dropna(axis='columns', how='all')
        if not df.index.is_unique:
            df = df.reset_index(drop=True)

    try:
        if df.empty:
            logger.error('空表')
            return 
    except AttributeError:
        logger.error(f'非資料框物件，係{type(df)}')
        return 

    if 顯示索引:
        df.reset_index(inplace=True)
    else:
        df.reset_index(drop=True, inplace=True)
    df.columns.name = '編號'
    df.index = df.index+1

    df.dropna(how='all')
    df.dropna(how='all', axis=1)

    df = df.head(顯示筆數)
    odf = df
    for c in 實數欄位+百分比欄位+整數欄位:
        df[c] = pd.to_numeric(df[c])
    if 無格式:
        可顯示資料框 = df.copy()
    else:
        try:
            df.columns = 重名加序(df.columns)
            整數欄位 = set(整數欄位).union(df.select_dtypes(include=['int']).columns)
            整數欄位 -= set(編號欄位)
            百分比欄位 = set(百分比欄位)
            實數欄位 = set(實數欄位).union(df.select_dtypes(include=['float']).columns)
            實數欄位 -= 整數欄位
            實數欄位 -= 百分比欄位
            百分比漸層按值區間欄位 = set(百分比漸層按值區間欄位)
            百分比漸層欄位 = set(百分比漸層欄位).union(set(百分比欄位))
            百分比漸層欄位 -= 百分比漸層按值區間欄位 
            漸層欄位 = set(漸層欄位).union(整數欄位, 實數欄位)
            漸層欄位 -= 百分比漸層欄位
            漸層欄位 = 漸層欄位.union(百分比漸層按值區間欄位)
            漸層欄位 -= set(指定漸層上下限欄位)
            日期欄位 = df.select_dtypes(include=['datetime']).columns
            期間欄位 = [c for c in df.columns if 'period' in df.dtypes[c].name]
            文字欄位 = df.select_dtypes(include=['object']).columns

            浮動提示 = df.copy()
            可顯示資料框 = df.copy()
            for c in df.columns: 浮動提示[c] = c
            if pd.__version__.startswith('2.'):
                df = df.style.map(lambda _:'text-align:right')
                df = df.map_index(lambda _:'text-align:center', axis=1)
            else:
                df = df.style.applymap(lambda _:'text-align:right')
                df = df.applymap_index(lambda _:'text-align:center', axis=1)
            df = df.format('{:.0f}', subset=list(編號欄位), na_rep='')
            df = df.format('{:,.0f}', subset=list(整數欄位), na_rep='')
            df = df.format(lambda v: f"{v*100:.0f}", subset=list(百分比欄位), na_rep='')
            df = df.format('{:,.2f}', subset=list(實數欄位), na_rep='')
            df = df.format('{:%Y%m%d}', subset=日期欄位, na_rep='')
            df = df.format(str, subset=期間欄位, na_rep='')
            df = df.format(str, subset=文字欄位, na_rep='')
            df = df.background_gradient(axis=0, cmap='RdYlGn', vmax=1, vmin=-1
                                       ,subset=list(百分比漸層欄位)
                                       )
            if 指定漸層上下限欄位 and 漸層上限 and 漸層下限:
                df = df.background_gradient(axis=0, cmap='RdYlGn', subset=list(指定漸層上下限欄位)
                                           ,vmax=漸層上限, vmin=漸層下限)
            df = df.background_gradient(axis=0, cmap='RdYlGn', subset=list(漸層欄位))
            df = df.hide(隱藏欄位, axis=1) # hide index
     
            tr_hover = {
                'selector': 'tr:hover',
                'props':[('background-color', '#ffffb3'), ('border-style', 'dotted')]
            }
            df = df.set_table_styles([tr_hover], overwrite=False)
            df = df.set_tooltips(浮動提示)
        except Exception as e:
            logger.error(e)
            # breakpoint()
            return 顯示(odf, 無格式=True)

    if 不顯示:
        return df, 可顯示資料框

    with tempfile.TemporaryDirectory() as tmpdirname:
        html = os.path.join(tmpdirname, "tempfile.html")
        html_content = df.to_html(classes='data-table', index=False)
        desc = 取數據輪廓(可顯示資料框)
        desc = 表示(desc.fillna(0), 顯示索引=False, 不顯示=True)[0]
        html_describe = desc.to_html(
                classes='describe-table'
               ,float_format=lambda x: f'{x:.2f}'
               )
        final_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                .data-table {{ border: 1px solid #ccc; margin-bottom: 40px; }}
                .describe-table {{ border: 1px solid #000; background-color: #f9f9f9; }}
                h2 {{ color: #333; }}
            </style>
        </head>
        <body>
            {html_content}
            
            <hr>
            
            <h2>資料型態</h2>
            {html_describe}
        </body>
        </html>
        """
        with open(html, mode='w', encoding='utf8') as f:
            f.write(final_html)
        os.system(f'start {html}')
        time.sleep(10)

def 檢核欄位資料型態是否為字串(表, 欄位名稱): 
    df = 表
    column_name = 欄位名稱
    return df[column_name].dtype == 'object' and df[column_name].map(type).eq(str).all()

def 重名加序(columns):
    seen = {}
    new_columns = []
    for col in columns:
        if col in seen:
            seen[col] += 1
            new_columns.append(f"{col}.{seen[col]}")
        else:
            seen[col] = 0
            new_columns.append(col)
    return new_columns

class 數據不足(Exception):

    def __init__(self, 名稱: str, 實際筆數: int, 至少筆數: int, 目的=''):
        self.名稱 = 名稱
        self.實際筆數 = 實際筆數
        self.至少筆數 = 至少筆數
        self.目的 = 目的
        super().__init__(self.__str__())

    def __str__(self):
        if len(self.目的) > 0:
            if self.實際筆數 > 0:
                return f"{self.名稱}僅有{self.實際筆數}筆，至少需要{self.至少筆數}筆，以{self.目的}！"
            else:
                return f"尚無{self.名稱}以{self.目的}！"

        if self.實際筆數 > 0:
            return f"{self.名稱}僅有{self.實際筆數}筆，至少需要{self.至少筆數}筆！"
        else:
            return f"尚無{self.名稱}！"

def 可顯示(查詢資料函數或顯示筆數=object(), 顯示筆數=100, 隱藏欄位=[], 整數欄位=[], 實數欄位=[]):
    '''
    一、裝飾查詢資料函數，指名參數設為【以表顯示=True】，即將查詢結果以 html 顯示。
    二、可用選項：顯示筆數、隱藏欄位、整數欄位、實數欄位。
    '''
    if callable(查詢資料函數或顯示筆數):
        return _可顯示(查詢資料函數或顯示筆數)
    else:
        def decorator(func):
            return _可顯示(func, 顯示筆數, 隱藏欄位, 整數欄位, 實數欄位)
        return decorator


def _可顯示(函數=object(), 顯示筆數=100, 隱藏欄位=[], 整數欄位=[], 實數欄位=[]):
    from functools import wraps
    import matplotlib.pyplot as plt
    @wraps(查詢資料函數)
    def wrapper(*args, 以表顯示=False, 圖示=False
               ,**kargs):
        可用選項 = ['顯示筆數', '隱藏欄位', '整數欄位', '實數欄位']
        for 選項 in 可用選項:
            if 選項值:=kargs.get(選項, None):
                del kargs[選項]
                if 選項=='顯示筆數': 
                    顯示筆數 = 選項值
                elif 選項=='隱藏欄位': 
                    隱藏欄位 = 選項值
                elif 選項=='整數欄位': 
                    整數欄位 = 選項值
                elif 選項=='實數欄位': 
                    實數欄位 = 選項值
        df = 查詢資料函數(*args, **kargs)
        if 以表顯示: 顯示(df, 顯示筆數=顯示筆數
                         ,隱藏欄位=隱藏欄位
                         ,整數欄位=整數欄位
                         ,實數欄位=實數欄位
                         ,顯示索引=True
                         )
        if 圖示: 
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
            df.plot()
            plt.show()
        return df
    return wrapper

def 取名稱帶同名圖片超文件碼(名稱, 圖檔子目錄, 圖寬='100%', 顯示名稱=None):
    if not 顯示名稱: 
        顯示名稱=名稱
    img_path = f"{圖檔子目錄}/{名稱}.png"
    html_content = (
        f"<div>{顯示名稱}<br>"
        f"<img src='{img_path}' alt='{顯示名稱} Image' width='{圖寬}'></div>"
    )
    return html_content
            

def _可顯示(查詢資料函數=object(), 顯示筆數=100, 隱藏欄位=[], 整數欄位=[], 實數欄位=[]):
    from functools import wraps
    import matplotlib.pyplot as plt
    @wraps(查詢資料函數)
    def wrapper(*args, 以表顯示=False, 圖示=False
               ,**kargs):
        nonlocal 顯示筆數, 隱藏欄位, 整數欄位, 實數欄位
        可用選項 = ['顯示筆數', '隱藏欄位', '整數欄位', '實數欄位']
        for 選項 in 可用選項:
            if 選項值:=kargs.get(選項, None):
                del kargs[選項]
                if 選項=='顯示筆數': 
                    顯示筆數 = 選項值
                elif 選項=='隱藏欄位': 
                    隱藏欄位 = 選項值
                elif 選項=='整數欄位': 
                    整數欄位 = 選項值
                elif 選項=='實數欄位': 
                    實數欄位 = 選項值
        df = 查詢資料函數(*args, **kargs)
        if 以表顯示: 顯示(df
                          ,顯示筆數=顯示筆數
                          ,隱藏欄位=隱藏欄位
                          ,整數欄位=整數欄位
                          ,實數欄位=實數欄位)
        if 圖示: 
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
            df.plot()
            plt.show()
        return df
    return wrapper

def 取名稱帶同名圖片超文件碼(名稱, 圖檔子目錄, 圖寬='100%', 顯示名稱=None):
    if not 顯示名稱: 
        顯示名稱=名稱
    img_path = f"{圖檔子目錄}/{名稱}.png"
    html_content = (
        f"<div>{顯示名稱}<br>"
        f"<img src='{img_path}' alt='{顯示名稱} Image' width='{圖寬}'></div>"
    )
    return html_content

def 多級欄位扁平化(df):
    df.columns = [f"{col[0]}_{col[1]}" if col[1] else f"{col[0]}" for col in df.columns]
    return df
