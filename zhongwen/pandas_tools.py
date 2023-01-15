'Pandas 輔助工具'
from pathlib import Path
import pandas as pd
import re
import os

def 強調關鍵字(df, 欄位=[], 關鍵字=[]):
    for c in 欄位:
        for k in 關鍵字:
            df[c] = df[c].str.replace(k, f'<b style="background:pink">{k}</b>')
    return df

def 資料型態標準化(df):
    '依資料框欄位名稱自動將資料框之資料型態標準化'
    from zhongwen.date import 取日期
    from zhongwen.number import 轉數值
    for c in df.columns:
        p = f'.*日期'
        if re.match(p, c):
            df[c] = df[c].map(取日期)
        p = f'.*金額'
        if re.match(p, c):
            df[c] = df[c].map(轉數值)
    return df            

def 標準格式(整數欄位=None, 實數欄位=None, 百分比欄位=None, 最大值顯著欄位=None, 隱藏欄位=None
            ,日期欄位=None
            ,採用民國日期格式=False
            ):
    def formatter(style):
        td_align_right = {'selector': 'td', 'props': 'text-align: right'}
        td_align_left = [{'selector': 'td', 'props': 'text-align: left;font-weight:bold'}]
        if 整數欄位:
            style.format('{:,.0f}', subset=整數欄位)
            # style.set_table_styles({"concept":td_align_right}, overwrite=False, axis=0)
        if 百分比欄位:
            style.format('{:,.2%}', subset=百分比欄位)
            style.background_gradient(axis=0, cmap='RdYlGn'
                  ,subset=百分比欄位, vmin=0, vmax=1)
        if 實數欄位:
            style.format('{:,.2f}', subset=實數欄位)
        if 日期欄位:
            style.format('{:%Y%m%d}', subset=日期欄位)
            if 採用民國日期格式:
                from zhongwen.date import 民國日期
                style.format(民國日期, subset=日期欄位)
        if 最大值顯著欄位:
            style.highlight_max(最大值顯著欄位)
            style.background_gradient(axis=0, cmap='RdYlGn'
                  ,subset=最大值顯著欄位)
        if 隱藏欄位:
            style.hide(隱藏欄位, axis=1) # hide index
        tr_hover = {
            'selector': 'tr:hover',
            'props':[('background-color', '#ffffb3'), ('border-style', 'dotted')]
        }
        style.set_table_styles([tr_hover], overwrite=False)
        return style
    return formatter

def show_html(df:pd.DataFrame, 自動格式=False
             ,整數欄位=None, 實數欄位=None, 百分比欄位=None
             ,日期欄位=None
             ,最大值顯著欄位=None, 隱藏欄位=None, 顯示筆數=100
             ,採用民國日期格式=False):
    if 顯示筆數:
        df = df[:顯示筆數]
    html = Path.home() / 'TEMP' / 'output.html'
    if 自動格式:
        columns = df.columns
        for c in df.columns:
            pat = '.*金額|支出|存入'
            if re.match(pat, c):
                try:
                    整數欄位.append(c)
                except AttributeError:
                    整數欄位 = [c]
            pat = '.*日期.*'
            if re.match(pat, c):
                try:
                    日期欄位.append(c)
                except AttributeError:
                    日期欄位 = [c]
        df.style.pipe(標準格式(整數欄位, 實數欄位, 百分比欄位
                              ,最大值顯著欄位, 隱藏欄位
                              ,日期欄位, 採用民國日期格式=採用民國日期格式)).to_html(html)
    else: df.to_html(html)
    os.system(f'start {html}')

def read_csv(*args, **kwargs):
    '編碼錯誤預設使用 replace。'
    from pathlib import Path
    fn = args[0]
    if isinstance(fn, Path):
        fn = str(fn)
    with open(fn, encoding=kwargs['encoding'], errors='replace') as f:
        df = pd.read_csv(f, *args[1:], **kwargs)
        return df

def read_fwf(*args, **kwargs): 
    import pandas as pd
    mbyte_columns = kwargs['mbyte_columns']
    names = kwargs['names']
    encoding = kwargs['encoding']
    del kwargs['mbyte_columns']
    del kwargs['encoding']
    df = pd.read_fwf(args[0], header=None
                    ,converters={h:str for h in names}
                    ,encoding = 'cp437' # 利用cp437剛好用1位元編碼特性，表達ByteString
                    ,**kwargs
                    )
    def convert(cp437:str):
        try:
            return cp437.encode('cp437').decode(encoding, errors='replace') 
        except AttributeError:
            return cp437
    for c in mbyte_columns: 
        df[c] = df[c].map(convert)
    return df

def read_docx_tables(filename, tab_id=None, **kwargs):
    from warnings import warn
    warn("警告：【read_docx_tables】函數將廢棄，請改用【read_docx】函數！")
    return read_docx_tables(filename, tab_id, **kwargs)

def read_docx(filename, tab_id=None, **kwargs):
    """
    讀取 Word 文件(.docx)表格至 Pnadas DataFrame
    parse table(s) from a Word Document (.docx) into Pandas DataFrame(s)

    Parameters:
        filename:   file name of a Word Document

        tab_id:     parse a single table with the index: [tab_id] (counting from 0).
                    When [None] - return a list of DataFrames (parse all tables)

        kwargs:     arguments to pass to `pd.read_csv()` function

    Return: a single DataFrame if tab_id != None or a list of DataFrames otherwise
    """
    from docx import Document
    def read_docx_tab(tab, **kwargs):
        import io
        import csv
        vf = io.StringIO()
        writer = csv.writer(vf)
        for row in tab.rows:
            writer.writerow(cell.text for cell in row.cells)
        vf.seek(0)
        return pd.read_csv(vf, **kwargs)

    doc = Document(filename)
    if tab_id is None:
        return [read_docx_tab(tab, **kwargs) for tab in doc.tables]
    else:
        try:
            return read_docx_tab(doc.tables[tab_id], **kwargs)
        except IndexError:
            print('Error: specified [tab_id]: {}  does not exist.'.format(tab_id))
            raise
