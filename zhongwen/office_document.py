from lark import Lark, Tree, Token, Transformer, Visitor
from lark.visitors import Interpreter
from zhongwen.date import 取日期, 民國日期
from zhongwen.number import 中文數字, 大寫中文數字
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
import logging

logger = logging.getLogger(Path(__file__).stem)
wdir = Path(__file__).parent
TITLE = -1
PROPOSER = -2
EVENTS = -3

def move_table_before(table, paragraph):
    tbl, p = table._tbl, paragraph._p
    tbl.addnext(p)

def make_events_table(doc, title, events):
    table = doc.add_table(rows=2, cols=2, style="Table Grid")
    title_row = table.rows[0]
    a, b = title_row.cells[:2]
    a.merge(b)
    p = a.paragraphs[0]
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.left_indent = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t = p.add_run(title)
    t.font.bold = True

    heading_row = table.rows[1].cells

    c = heading_row[0]
    c.width = Inches(0.1)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.left_indent = Pt(0)
    t = p.add_run('日期')
    t.font.size = Pt(12)
    t.font.bold = True

    c = heading_row[1]
    c.width = Inches(12)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t = p.add_run('摘要')
    t.font.size = Pt(12)
    t.font.bold = True
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.left_indent = Pt(0)

    for event in events:
        add_event_row(table, event)
    p = doc.add_paragraph() 
    doc.add_page_break()
    move_table_before(table, p)

def add_event_row(table, event): 
    # print(event[0])
    date = 民國日期(取日期(event[0]))
    event = event[1]
    row = table.add_row().cells
    c = row[0]
    from docx.enum.text import WD_LINE_SPACING

    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    p.paragraph_format.line_spacing = Pt(23)
    t = p.add_run(date)
    t.font.size = Pt(12)

    c = row[1]
    p = c.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    p.paragraph_format.line_spacing = Pt(23)
    t = p.add_run(event)
    t.font.size = Pt(12)

class MakeDocxTree(Transformer):

    def DESC(self, args):
        return args.value

    def DATE(self, args):
        return 取日期(args)

from pathlib import Path
from docx.shared import Pt
def setup_style(docx):
    style = docx.styles['Heading 1']
    font = style.font
    font.name = 'Calibri' #'DFKai-SB' #標楷體
    font.size = Pt(16)
    font.bold = True
    #docx.styles['Heading 1'].font.Size = Pt(30)
    return docx

def read_docx(doc):
    '讀取word文件文字'
    doc = Document(doc)
    return "\n".join([p.text for p in doc.paragraphs])

def fread_docx(doc):
    from file import 最新符合檔 
    doc = 最新符合檔(Path("D:\\g"), f"**/*{doc}*.docx")
    return read_docx(doc)

def 轉換游標標號層次(層級):
    '游標處符合模式字串，否傳回None'
    import vim
    cb = vim.current.buffer
    l = vim.current.window.cursor[0] - 1
    line = cb[l]
    line = 設定標號層次(層級, line)
    cb[l] = line

def 游標模式替換(模式, 替換函式):
    '游標處符合模式字串，否傳回None'
    import vim
    cb = vim.current.buffer
    _a, l, c, _a, _a = map(lambda s: int(s)-1, vim.eval('getcursorcharpos()'))
    line = cb[l] 
    import re
    p = re.compile(模式)
    i = 0
    while m:=p.search(line, i):
        if m.start() <= c < m.end():
            替換 = 替換函式(m[0]) 
            cb[l] = line[:m.start()] + 替換 + line[m.end():]
            return [m.group(0), m.start(), m.end(), line, cb, l]
        i = m.end()+1
    raise ValueError(f'游標處無此模式，模式:{模式}，游標:{c}，行:{line}')

微軟辦公室軟體共用範本路徑 = [
        'AppData/Roaming/Microsoft/Templates/Normal.dotm' # Word
       ,'AppData/Roaming/Microsoft/Excel/XLSTART/fhopecc.xlsb' # Excel
       ]

def 設定環境():
    for t in 微軟辦公室軟體共用範本路徑:
        t = Path.home() / t
        s = Path(__file__).parent.parent / 'resource' / t.name
        try:
            copy(s, t)
        except FileNotFoundError:
            t.parent.mkdir(exist_ok=True)
            copy(s, t)

def 更新微軟辦公室軟體共用範本():
    from shutil import copy
    for s in 微軟辦公室軟體共用範本路徑:
        s = Path.home() / s
        t = Path(__file__).parent.parent / 'resource' / s.name
        copy(s, t)
    logger.info('更新微軟辦公室軟體共用範本完成！')

class MakeContentList(Transformer):
    '回傳[階層碼、段落文字]清單'

    def start(self, args):
        return [[TITLE, args[0].value], *args[1:]]

    def content(self, args):
        return args[0]

    def h1(self, args):   
        from zhongwen.number import 中文數字, 轉數值
        return [1, f"{大寫中文數字(轉數值(args[0].value))}、" + args[1].value]

    def h2(self, args):   
        from zhongwen.number import 中文數字, 轉數值
        return [2, f"({大寫中文數字(轉數值(args[0].value))})" + args[1].value]

    def h3(self, args):   
        from zhongwen.number import 中文數字, 轉數值
        return [3, f"{中文數字(轉數值(args[0].value))}、" + args[1].value]

    def h4(self, args):   
        from zhongwen.number import 中文數字, 轉數值
        return [4, f"({中文數字(轉數值(args[0].value))})" + args[1].value]

    def h5(self, args):   
        from zhongwen.number import 中文數字, 轉數值
        return [5, f"{轉數值(args[0].value)}." + args[1].value]

    def h6(self, args):   
        from zhongwen.number import 中文數字, 轉數值
        return [6, f"({轉數值(args[0].value)})" + args[1].value]

    def p(self, args):   
        return [0, args[0].value]
    
    def proposer(self, args):   
        return [PROPOSER, '提案人：' + args[0].value]
    
    def events(self, args):
        return [EVENTS, [args[0], args[1:]]]

    def event(self, args):
        date = 民國日期(args[0])
        event = args[1]
        return [date, event]

def parse(doc) -> Lark: 
    p = Lark.open(Path(__file__).parent / 'office_document.lark')
    t = p.parse(doc)
    t = MakeDocxTree().transform(t)
    return t

def todocx(doc):
    path = Path(doc)
    with open(doc, 'r', encoding='utf8') as f:
        doc = '\n'.join(f.readlines())
        docx = path.with_suffix('.docx')
        t = parse(doc)
        title = t.children[0]
        # print(t.pretty())
        t = MakeContentList().transform(t)
        doc = Document(r'd:\GitHub\zhongwen\zhongwen\template.docx')
        for l, p in t:
            if l > 0:
                doc.add_heading(p, level=l)
            else:
                if l == TITLE:
                    p0 = doc.paragraphs[0]
                    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p0.keep_together = True
                    # p0.keep_with_next = True
                    r = p0.add_run(p)
                    r.font.bold = True
                elif l == PROPOSER: 
                    p = doc.add_paragraph(p) 
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                elif l == EVENTS:
                    title = p[0]
                    events = p[1]
                    make_events_table(doc, title, events)
                else:
                    doc.add_paragraph(p)
        if '工作底稿' in title:
            doc.add_paragraph()
            doc.add_paragraph("撰稿：                        覆核：")
        doc.save(docx) 
        from os import system
        system(f'start {docx}')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", nargs='?')
    parser.add_argument("--setup", help="設定環境", action="store_true")
    parser.add_argument("--test", help="測試", action="store_true")
    parser.add_argument("--update_temp", help="更新微軟辦公室軟體共用範本", action="store_true")
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif args.update_temp:
        更新微軟辦公室軟體共用範本()
    elif args.test:
        import os
        file_path = Path(__file__)
        os.system(str(file_path.with_name(f'test_{file_path.name}')))
    elif args.docx:
        import clipboard
        from pathlib import Path
        text = read_docx(args.docx)
        clipboard.copy(text)
        print(text)
