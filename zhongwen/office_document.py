from lark import Lark, Tree, Token, Transformer
from pathlib import Path
wdir = Path(__file__).parent

def 中文數值(中文數):
    n1tab = str.maketrans("零壹貳參肆伍陸柒捌玖", "0123456789")
    n2tab = str.maketrans("Ｏ一二三四五六七八九", "0123456789")
    return int(中文數.translate(n1tab).translate(n2tab))

def 中文數符(數, 大數=False):
    n1tab = str.maketrans("0123456789", "零壹貳參肆伍陸柒捌玖")
    n2tab = str.maketrans("0123456789", "Ｏ一二三四五六七八九")
    if 大數:
        return str(數).translate(n1tab)
    return str(數).translate(n2tab)

def 標號字串(標號, 層級):
    if 層級=='T1':
        return 中文數符(標號, True) + '、'
    if 層級=='T2':
        return f'({中文數符(標號, True)})'
    if 層級=='T3':
        return 中文數符(標號) + '、'
    if 層級=='T4':
        return f'({中文數符(標號)})'
    if 層級=='T5':
        return f'{標號}.'
    if 層級=='T6':
        return f'({標號})'

def 標題分析(標題):
    模式 = {'T1':r'([壹貳參肆伍陸柒捌玖拾])+、(.+)',
            'T2':r'\(([壹貳參肆伍陸柒捌玖拾])+\)(.+)',
            'T3':r'([一二三四五六七八九十])+、(.+)',
            'T4':r'\(([一二三四五六七八九十])+\)(.+)',
            'T5':r'(\d+)\.(.*)',
            'T6':r'\((\d+)\)(.*)'
           }[標題.type]
    if m := re.match(模式, 標題.value):
        標號數=int(中文數值(m[1]))
        內容=m[2]
    標題.value = (標號數, 內容)
    return 標題

def l():
    return Lark(
         r'''T: /.*(計畫|資料調閱單|工作底稿|審核通知|報告|審計會議提案|重要審核意見).*/
            T1: N1 "、" P
            T2: "(" N1 ")" P
            T3: N2 "、" P
            T4: "(" N2 ")" P
            T5: /\d+\..*/
            T6: /\(\d+\).*/
            P:  /[^壹貳參肆伍陸柒捌玖拾一二三四五六七八九十\d(\s].*/
            t: (T1 | T2 | T3 | T4 | T5 | T6) P*

            N1:/[壹貳參肆伍陸柒捌玖拾]+/
            N2:/[一二三四五六七八九十]+/

            start: T t*
            %import common.WS
            %ignore WS
         ''')
    
 #''', 
#         lexer_callbacks={
#             'T1':標題分析,
#             'T2':標題分析,
#             'T3':標題分析,
#             'T4':標題分析,
#             'T5':標題分析,
#             'T6':標題分析 
#         })'''

def 設定標號層次(層級, 標題):
    層級 = f'T{層級}'
    標題 = 標題分析(next(l().lex(標題)))
    標號 = 標題.value[0]
    題目 = 標題.value[1]
    return f'{標號字串(標號, 層級)}{題目}'

from docx import Document

def temppath():
    return wdir / 'template.docx'
import re

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
