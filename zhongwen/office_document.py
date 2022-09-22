from lark import Lark, Tree, Token, Transformer, Visitor
from lark.visitors import Interpreter
from zhongwen.date import 取日期, 民國日期
from pathlib import Path
import re
wdir = Path(__file__).parent

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def move_table_before(table, paragraph):
    tbl, p = table._tbl, paragraph._p
    tbl.addnext(p)

class MakeDocx(Interpreter):
    def __init__(self, docx):
        self.doc = Document(Path(__file__).parent / 'template.docx')
        self.docx = docx

    def start(self, args):
        print('start')
        for _events in args.children:
            self.visit(_events)
        self.doc.save(self.docx)

    def events(self, args):
        # print(args)
        title = args.children[0] 
        _events = args.children[1:]
        table = self.doc.add_table(rows=2, cols=2, style="Table Grid")
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

        self.work_table = table
        for event in _events:
            self.visit(event)
        p = self.doc.add_paragraph() 
        move_table_before(table, p)

    def event(self, args): 
        date = 民國日期(args.children[0])
        event = args.children[1]
        row = self.work_table.add_row().cells

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
        return args

    def DATE(self, args):
        return 取日期(args)

def parse(doc) -> Lark: 
    p = Lark.open(Path(__file__).parent / 'office_document.lark')
    t = p.parse(doc)
    t = MakeDocxTree().transform(t)
    return t

def todocx(doc, docx):
    worksheet = Path(r'd:\g\111-2漁港建設專調\大事記.txt')
    with open(worksheet, 'r', encoding='utf8') as f:
        doc = '\n'.join(f.readlines())
        l = parse(doc, docx)
        from os import system
        system(f'start {docx}')
        MakeDocx(docx).visit(t)

def mkdocx(tree, doc, doctype):
    if isinstance(tree, Tree):
        #print(tree.data)
        for child in tree.children:
            mkdocx(child, doc, doctype)
    elif tree.type[0] == 'T':
        #print(tree.type)
        內容 = 標號字串(tree.value[0], tree.type) + tree.value[1]
        doc.add_heading(tree.value, 
                        level=int(tree.type[1]))
    else:    
        #print('para')
        doc.add_paragraph(tree.value)

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

def 增加簽核(doctype, doc):
    if doctype == '工作底稿':
        doc.add_paragraph('')
        doc.add_paragraph('')
        doc.add_paragraph('查核人員：                     領組：')
    if doctype == '資料調閱單':
        doc.add_paragraph('')
        doc.add_paragraph('')
        doc.add_paragraph('填寫人員：                     覆核：')

def todocx(txt, docx):
    if isinstance(txt, str):
        tree = l().parse(txt) 
        T = tree.children[0]
        if isinstance(T, Token):
            doc=Document(temppath())
            doctype='工作底稿'
            if T.value == '審核通知':
                doc.add_heading('審計部臺灣省花蓮縣審計室審核通知', level=1)
                doc.add_heading('機關名稱：花蓮縣政府', level=1)
                doc.add_heading('審核事項：110年度單位決算及財務收支', level=1)
                doc.add_heading('審核結果：', level=1)

            elif T.value == '工作底稿':
                doc.add_heading('審計部臺灣省花蓮縣審計室工作底稿', level=1)
            elif re.match('.*資料調閱單.*', T.value):
                p = doc.paragraphs[0]
                p.text = T.value
                p.style = doc.styles['Heading 1']
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                #doc.add_heading(T.value, level=1)
                doctype='資料調閱單'
            elif re.match('.*報告', T.value):
                doc.add_heading(T.value, level=1)
                doctype='報告'
            for child in tree.children[1:]:
                mkdocx(child, doc, doctype)
        增加簽核(doctype, doc)
        doc.save(docx)
    if isinstance(txt, Path):
        todocx(txt.read_text(encoding='utf-8-sig'), docx)

def read_docx(doc):
    '讀取word文件文字'
    doc = Document(doc)
    return "\n".join([p.text for p in doc.paragraphs])

def fread_docx(doc):
    from file import 最新符合檔 
    doc = 最新符合檔(Path("D:\\g"), f"**/*{doc}*.docx")
    return read_docx(doc)

#def 設定標號層次(層級, 標題):
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

def 設定環境():
    import winshell
    捷徑 = Path(winshell.sendto()) / f"複製文字.lnk"
    程式 = Path(__file__) 
    winshell.CreateShortcut(
        Path=str(捷徑),#右鍵sendto快捷方式
        Target=f'{程式}',
        Icon=(str(程式), 0),
        Description='複製文字')
    print(f'建立傳送到[複製文字]。')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", nargs='?')
    parser.add_argument("--setup", help="設定環境", action="store_true")
    parser.add_argument("--test", help="測試", action="store_true")
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif args.test:
        import os
        file_path = Path(__file__)
        os.system(str(file_path.with_name(f'test_{file_path.name}')))
    if args.docx:
        import clipboard
        from pathlib import Path
        text = read_docx(args.docx)
        clipboard.copy(text)
        print(text)
