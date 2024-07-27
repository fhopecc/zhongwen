from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 解鎖(pdfs, 覆蓋原檔=False):
    import PyPDF2
    from collections.abc import Iterable 
    from pathlib import Path
    if not isinstance(pdfs, Iterable):
        pdfs = [pdfs]
    for pdf in pdfs:
        with open(pdf, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])
            desecured_pdf:Path = pdf.with_stem(pdf.stem + '_desecured')
            with open(desecured_pdf, 'wb') as output_file:
                writer.write(output_file)
            if 覆蓋原檔:
                desecured_pdf.replace(pdf)

def word2pdf(words, output_dir=None):
    from collections.abc import Iterable 
    from pathlib import Path
    import win32com.client
    if isinstance(words, str) or not isinstance(words, Iterable):
        words = [word]
    if not output_dir:
        output_dir = Path(__file__).parent
    word = win32com.client.Dispatch('Word.Application')
    for w in words:
        doc = word.Documents.Open(str(w))
        doc.SaveAs(str(output_dir / w.with_suffix('.pdf').name), FileFormat=17)
        doc.Close()
    word.Quit()

def 合併(pdfs, 合併檔名='merged.pdf'):
    from PyPDF2 import PdfWriter
    from pathlib import Path
    merger = PdfWriter()
    filedir = None
    for pdf in pdfs:
        if not filedir:
            filedir = Path(pdf).parent
        try:
            merger.append(pdf)
        except Exception as e:
           breakpoint() 
           pass
    output = filedir / 合併檔名
    merger.write(output)
    merger.close()

def 旋轉(源檔, 角度=180, 旋轉頁=None, 目標檔=None):
    import PyPDF2
    from pathlib import Path
    if not 目標檔: 
        目標檔 = 源檔.with_stem(源檔.stem+"旋轉後")
    with open(源檔, 'rb') as pdf_in, open(目標檔, 'wb') as pdf_out:
        pdf_reader = PyPDF2.PdfReader(pdf_in)
        pdf_writer = PyPDF2.PdfWriter()
        for pagenum in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[pagenum]
            if pagenum in 旋轉頁:
                page.rotate(角度)
            pdf_writer.add_page(page)
        pdf_writer.write(pdf_out)

def 去空白頁(源檔, 轉換檔=None):
    if not 轉換檔: 
        轉換檔 = 源檔.with_stem(源檔.stem+"去空白頁")
    input_file = 源檔 
    output_file = 轉換檔

    import fitz
    doc = fitz.open(input_file)

    非空白頁碼清單 = []
    import numpy as np 
    from PIL import Image
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap()
        
        # 将Pixmap对象转换为PIL的Image对象
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 将图像转换为灰度图像
        gray_image = image.convert("L")

        # 将灰度图像转换为NumPy数组
        np_image = np.array(gray_image)
        
        # 计算像素值的均值
        mean_value = np.mean(np_image)
        
        # 设置阈值来判断页面是否为空白
        threshold = 200  # 可根据需要进行调整

        if mean_value < threshold: 
            非空白頁碼清單.append(page_number)
    doc.select(非空白頁碼清單)
    doc.save(output_file)

def 刪除頁面(input_path, pages, output_path=None):
    from PyPDF2 import PdfWriter, PdfReader
    from pathlib import Path
    input_path = Path(input_path)
    if not output_path:
        s = input_path.stem
        output_path = input_path.with_stem(f'{s}刪除後')
    with open(input_path, 'rb') as file:
        reader = PdfReader(file)
        writer = PdfWriter()

        total_pages = len(reader.pages)

        for page_number in range(total_pages):
            if page_number + 1 not in pages:
                writer.add_page(reader.pages[page_number])

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        print(f"{input_path}刪除頁面{', '.join(map(str, pages))}，結果另存於{output_path}。")

def 解鎖(pdfs):
    from collections.abc import Iterable 
    if not isinstance(pdfs, Iterable):
        pdfs = [pdfs]
    
    for pdf in pdfs:
        pdf

def 設定環境():
    from zhongwen.winman import 建立傳送到項目
    import sys
    cmd =  f'"{sys.executable}" -m fhopecc.pdf --merge_pdfs %*'
    建立傳送到項目('合併PDF', cmd)

if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action='store_true')
    parser.add_argument('--merge_pdfs', nargs='+', type=str, help='合併PDF')
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif pdfs := args.merge_pdfs:
        合併(pdfs)
