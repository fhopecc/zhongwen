from pathlib import Path
import os

def 設定環境():
    import winshell
    import sys
    # for 應用程式 in ['tesseract', 'tesseract-languages']:
    #     os.system(f'scoop install {應用程式}')
    # 安裝套件('pytesseract')
    待識圖目錄.mkdir(exist_ok=True)
    winshell.CreateShortcut(
       Path=os.path.join(winshell.desktop(),"截圖辨字.lnk")
      ,Target=sys.executable
      ,Arguments=f'{Path(__file__)} --OCR'
      ,Icon=(sys.executable, 0)
      ,Description="截圖辨字"
    )
    print(f'建立捷徑[截圖辨字]。')

def 取圖陣列(圖):
    '取圖的 ndarray 表示'
    from PIL import Image
    import numpy as np
    import cv2 
    import io 

    img_pil = None

    if isinstance(圖, str):
        # 如果輸入是檔案路徑
        if not os.path.exists(圖):
            raise FileNotFoundError(f"圖片檔案不存在：{圖}")
        try:
            img_pil = Image.open(圖).convert('RGB') # 確保為 RGB 模式
        except Exception as e:
            raise ValueError(f"無法讀取圖片檔案 '{圖}'，請檢查檔案是否損壞或格式不支援。錯誤：{e}")
    elif isinstance(圖, Image.Image):
        # 如果輸入已經是 PIL Image 物件
        img_pil = 圖.convert('RGB') # 確保為 RGB 模式
    elif isinstance(圖, bytes):
        # 如果輸入是二進位數據
        try:
            img_pil = Image.open(io.BytesIO(圖)).convert('RGB') # 確保為 RGB 模式
        except Exception as e:
            raise ValueError(f"無法從二進位數據讀取圖片，請檢查數據是否為有效的圖片格式。錯誤：{e}")
    else:
        raise ValueError("不支援的圖片輸入類型。請提供檔案路徑、PIL.Image 物件或二進位數據。")

    # 將 PIL Image 轉換為 NumPy 陣列
    # PIL 預設是 RGB 格式 (Red, Green, Blue)
    img_np = np.array(img_pil)

    # 通常為了相容性，尤其當與 OpenCV 協作時，會轉換為 BGR。
    # 如果 img_np 只有2個維度 (灰度圖)，則不需要轉換
    if len(img_np.shape) == 3 and img_np.shape[2] == 3: # 確保是彩色圖片
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    return img_np

def tesseract(png):
    '採用 google tesseract 辨識圖內文，目前最精準快速之OCR。'
    from PIL import Image
    import pytesseract
    image = Image.open(str(png))
    text = pytesseract.image_to_string(image, lang='chi_tra')
    text = ''.join(text)
    text = text.replace('\n','')
    return text

def 取圖內文(圖檔):
    return tesseract(圖檔)



待識圖目錄 = Path(os.environ['TEMP']) / 'to_ocr'

def 截圖辨字():
    from PIL import ImageGrab
    import win32api, win32clipboard, win32con, win32gui
    import threading, ctypes
    import clipboard
    import time
    def 儲存截圖():
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_BITMAP):
            win32clipboard.CloseClipboard()
            im = ImageGrab.grabclipboard()
            圖檔 = 待識圖目錄/ f'{time.time()}.png'
            im.save(圖檔, 'PNG')
            文字 = 取圖內文(圖檔)
            clipboard.copy(文字)
            print(文字)
        else:
            win32clipboard.CloseClipboard()

    def 監聽截圖(hwnd: int, msg: int, wparam: int, lparam: int):
        WM_CLIPBOARDUPDATE = 0x031D
        if msg == WM_CLIPBOARDUPDATE:
            儲存截圖()
        return 0

    def runner():
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = 監聽截圖
        wc.lpszClassName = '監聽截圖'
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(class_atom, '監聽截圖', 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
        ctypes.windll.user32.AddClipboardFormatListener(hwnd)
        win32gui.PumpMessages()

    th = threading.Thread(target=runner, daemon=True)
    th.start()
    print('啟動截圖辨字…')
    print('Windows 10系統鍵入<W-Shift-S>後，以滑鼠選取矩形螢幕截圖範圍後，')
    print('截圖辨字結果將儲存至系統剪貼簿。')

    while th.is_alive():
        th.join(0.25)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action="store_true")
    parser.add_argument("--OCR", help="啟動截圖辨字", action="store_true")
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif args.OCR:
        截圖辨字()
