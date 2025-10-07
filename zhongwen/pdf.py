from pathlib import Path
from diskcache import Cache
from pathlib import Path
import logging

logger = logging.getLogger(Path(__file__).stem)

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 設定環境():
    r"""
    一、安裝套件 pdf2image，先至github下載 poppler-windows 預編檔，
        放到 poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin'
        指定之目錄。
    """
    from zhongwen.winman import 建立傳送到項目, 增加檔案右鍵選單功能
    from zhongwen.python import 安裝套件
    import sys
    
    logger.info('設定 pdf 功能')
    cmd =  f'"{sys.executable}" -m zhongwen.pdf --merge_pdfs %* && pause'
    建立傳送到項目('合併為PDF', cmd)

    cmd = f'cmd.exe /c "{sys.executable} -m zhongwen.pdf --arrange %1 || pause"'
    增加檔案右鍵選單功能('整理頁面', cmd, 'pdf')
    增加檔案右鍵選單功能('整理頁面', cmd, 'FoxitReader.Document')

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

def 合併(pdfs, 合併檔名='合併檔案.pdf'):
    from zhongwen.office_document import doc2docx, doc2pdf
    from PyPDF2 import PdfWriter
    from pathlib import Path
    from shutil import copy
    pdfs = sorted(pdfs)
    merger = PdfWriter()
    filedir = None
    docxdir = None
    pdfdir = None
    for src in pdfs:
        src = Path(src)
        if not filedir:
            filedir = Path(src).parent
        if not docxdir:
            docxdir = Path(src).parent / 'docxs'
            docxdir.mkdir(exist_ok=True)
        if not pdfdir:
            pdfdir = Path(src).parent / 'pdfs'
            pdfdir.mkdir(exist_ok=True)
        if src.suffix == '.doc':
            doc2docx(src, docxdir)
            docx = docxdir / src.with_suffix('.docx').name
            doc2pdf(docx, pdfdir)
            pdf = pdfdir / docx.with_suffix('.pdf').name
        if src.suffix == '.docx':
            doc2pdf(src, pdfdir)
            pdf = pdfdir / src.with_suffix('.pdf').name
        if src.suffix == '.pdf':
            pdf = src
        try:
            merger.append(pdf)
        except Exception as e:
            print(e)
            breakpoint() 
            pass
    output = filedir / 合併檔名
    merger.write(output)
    merger.close()

def 旋轉(源檔, 角度=180, 旋轉頁=None, 目標檔=None, 奇數頁旋轉角度=None, 偶數頁旋轉角度=None):
    '''
    一、起始頁數係0，惟為符合一般頁碼編碼方式，奇偶頁判斷係將起始頁數視為1。
    '''
    from zhongwen.數 import 取數值
    from pathlib import Path
    import PyPDF2
    源檔 = Path(源檔)
    if not 目標檔: 
        目標檔 = 源檔.with_stem(源檔.stem+"旋轉後")
    with open(源檔, 'rb') as pdf_in, open(目標檔, 'wb') as pdf_out:
        pdf_reader = PyPDF2.PdfReader(pdf_in)
        pdf_writer = PyPDF2.PdfWriter()
        for pagenum in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[pagenum]
            if 奇數頁旋轉角度 is not None or 偶數頁旋轉角度 is not None:
                if not 奇數頁旋轉角度: 
                    奇數頁旋轉角度 = 0
                if not 偶數頁旋轉角度: 
                    偶數頁旋轉角度 = 0
                if pagenum % 2 == 0:
                    page.rotate(奇數頁旋轉角度)
                else:
                    page.rotate(偶數頁旋轉角度)
            elif 旋轉頁 is None or pagenum in 剖析頁碼字串(旋轉頁):
                page.rotate(取數值(角度))
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

def to_excel(pdfs):
    from collections.abc import Iterable 
    from pathlib import Path
    import pandas as pd
    import pdfplumber
    if isinstance(pdfs, str) or not isinstance(pdfs, Iterable):
        pdfs = [pdfs]

    pdfs = [Path(pdf) for pdf in pdfs]

    for pdf in pdfs:
        with pdfplumber.open(pdf) as _pdf:
            all_data = []
            for page in _pdf.pages:
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])  # 使用表格第一行作為標題
                    all_data.append(df)
            final_df = pd.concat(all_data)
            xlsx = pdf.with_suffix('.xlsx')
            final_df.to_excel(xlsx, index=False)
            print(f'{pdf.name}->{xlsx.name}')

def 平分(文件路徑, 平分文件數=2, 平分文件大小=None):
    '''平分文件，預設分半，即將文件平分為2個文件；
    如指定平分文件數，即平分為該數個文件(尚未實現)；
    如指定平分文件大小，即依該大小平分文件(尚未實現)。
    '''
    import fitz

    pdf_path = Path(文件路徑.strip('"'))

    # 打開 PDF 文件
    pdf_document = fitz.open(pdf_path)

    # 計算中間頁
    total_pages = len(pdf_document)
    half = total_pages // 2
    output_part1 = pdf_path.with_stem(f'{pdf_path.stem}_1')
    output_part2 = pdf_path.with_stem(f'{pdf_path.stem}_2')

    # 創建兩個新的 PDF 文件
    part1 = fitz.open()
    part2 = fitz.open()

    # 將前半部分加入 part1
    for page_num in range(half):
        part1.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

    # 將後半部分加入 part2
    for page_num in range(half, total_pages):
        part2.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

    # 保存分割後的 PDF 文件
    part1.save(output_part1, deflate=True)
    part2.save(output_part2, deflate=True)

    # 關閉文件
    part1.close()
    part2.close()
    pdf_document.close()

    logger.info(f'{pdf_path.name} -\\\\-> [{output_part1}, {output_part2}]')

def 取內文(pdf, 圖內文語言='chi_tra'):
    """
    提取 pdf 內文字並辨識圖內文字。
    """
    from zhongwen.圖 import 取圖內文
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    import fitz
    import io
    import os

    pdf_path = str(pdf)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"錯誤：找不到 PDF 檔案 '{pdf_path}'")

    OCR_LANG = 圖內文語言

    doc = fitz.open(pdf_path)
    results = [f"源檔：{pdf}"]

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text().strip()

        if text:
            results.append(f"第 {page_num+1} 頁（文字擷取）:\n{text}")
        else:
            # 將該頁轉為圖片，再進行 OCR
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1
                                       ,dpi=300
                                       ,poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin'
                                       )
            if images:
                image = images[0]
                ocr_text = pytesseract.image_to_string(image, lang=OCR_LANG).strip()
                results.append(f"第 {page_num+1} 頁（OCR 擷取）:\n{ocr_text}")
            else:
                results.append(f"第 {page_num+1} 頁：無法載入圖片")

    return "\n\n".join(results)

def 剖析頁碼字串(page_str):
    """
    將頁碼字串轉成 Python 頁碼列表（0-based）
    支援格式：
      "3"          -> [2]
      "3,5,7"      -> [2,4,6]
      "3-5"        -> [2,3,4]
      "3-5,8,10-12"-> [2,3,4,7,9,10,11]
    """
    pages = []
    for part in page_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start, end = int(start), int(end)
            pages.extend(range(start - 1, end))
        else:
            pages.append(int(part) - 1)
    return sorted(set(pages))  # 排序並去重

def 擷取頁面(源檔, 頁面=None, 目的檔=None):
    '擷取頁面(input_pdf, "3-7,10,12-14", "抽出頁面.pdf")'
    from pypdf import PdfReader, PdfWriter
    from pathlib import Path
    input_pdf = Path(源檔)
    page_str = 頁面
    if page_str == None:
        page_str = input(f'請依格式範例"3-7,10,12-14"輸入要擷取之頁面區間：')
    if not 目的檔:
        output_pdf = Path(input_pdf).with_name(f"{input_pdf.stem}_{page_str}{input_pdf.suffix}")
    else:
        output_pdf = 目的檔


    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    pages = 剖析頁碼字串(page_str)
    for p in pages:
        if 0 <= p < len(reader.pages):
            writer.add_page(reader.pages[p])
        else:
            print(f"頁碼 {p+1} 超出範圍（共 {len(reader.pages)} 頁）")

    with open(output_pdf, "wb") as f:
        writer.write(f)

    print(f"已將 {page_str} 頁輸出為：{output_pdf}")

def 移動頁面(源檔, 頁面, 移動頁數, 目的檔=None):
    """
    將 PDF 檔案中的某頁往後移動一頁。

    參數:
    input_pdf_path (str): 輸入的 PDF 檔案路徑。
    output_pdf_path (str): 儲存新 PDF 檔案的路徑。
    page_number (int): 要移動的頁碼（從 1 開始）。
    """
    from pathlib import Path
    from zhongwen.數 import 取數值
    import PyPDF2
    源檔 = Path(源檔 )
    input_pdf_path = str(源檔)
    page_to_move_num = 頁面 = 取數值(頁面)
    m = 移動頁數 = 取數值(移動頁數)
    if not 目的檔:
        output_pdf_path = 源檔.with_name(f"{源檔.stem}移動第{頁面}頁至第{頁面+移動頁數}頁.pdf")
        output_pdf_path = str(output_pdf_path)
    else:
        output_pdf_path = 目的檔
    try:
        with open(input_pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()

            total_pages = len(reader.pages)

            # 將使用者輸入的頁碼轉為索引（從 0 開始）
            page_to_move_index = page_to_move_num - 1

            # 檢查頁碼是否有效
            if not 0 <= page_to_move_index < total_pages:
                print(f"錯誤：頁碼 {page_to_move_num} 不存在。")
                return

            # 計算目標頁碼索引
            target_page_index = page_to_move_index + m
            
            # 檢查目標位置是否超出範圍
            if not 0 <= target_page_index <= total_pages:
                print(f"錯誤：目標位置 {page_to_move_num + m} 超出範圍。")
                return

            # 取得要移動的頁面物件
            page_to_move = reader.pages[page_to_move_index]

            # 建立新的頁面列表，排除要移動的頁面
            remaining_pages = [page for i, page in enumerate(reader.pages) if i != page_to_move_index]
            
            # 將要移動的頁面插入到新的目標位置
            remaining_pages.insert(target_page_index, page_to_move)

            # 將所有頁面添加到 writer
            for page in remaining_pages:
                writer.add_page(page)

            # 儲存新的 PDF 檔案
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)
        print(f"{Path(input_pdf_path).name} ~{頁面}>>{頁面+移動頁數}~> {Path(output_pdf_path).name}")
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {input_pdf_path}")
    except Exception as e:
        print(f"發生錯誤：{e}")

def 整理頁面(pdf):
    '整理頁面'
    import time
    print(f'整理{pdf}頁面……')
    操作 = input('1.請選擇操作：(r)旋轉頁面；(m)移動頁面：')
    if 操作 == 'r':
        角度 = input('2.請指定旋轉角度(90、180、270、-90、-180、-270)：')
        頁面 = input('3.請指定旋轉頁面(示例1,3,4-5)：')
        旋轉(pdf, 角度, 頁面)
    if 操作 == 'm':
        頁面= input('2.請指定移動之頁面(示例1,2,3…)：')
        移動頁數 = input('3.請指定移動頁數(示例1,-5,)：')
        移動頁面(pdf, 頁面, 移動頁數)
    time.sleep(10)

if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action='store_true')
    parser.add_argument('--to_excel', nargs='+', type=str, help='2excel')
    parser.add_argument('--merge_pdfs', nargs='+', type=str, help='合併PDF')
    parser.add_argument("--split", type=str, help="平分", required=False)
    parser.add_argument('--extract_pages', type=str, help='擷取頁面')
    parser.add_argument('--arrange', type=str, help='整理文件頁面')
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif pdf := args.split:
        平分(pdf)
    elif pdfs := args.merge_pdfs:
        合併(pdfs)
    elif pdfs := args.to_excel:
        to_excel(pdfs)
    elif pdf := args.arrange:
        整理頁面(pdf)
