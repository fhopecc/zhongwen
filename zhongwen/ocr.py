# 截圖辨字
from pathlib import Path
from PIL import ImageGrab
from socket import gethostname 
import clipboard
import win32api, win32clipboard, win32con, win32gui
import threading, ctypes
import os, sys
import wmi
import time
import winshell

待識圖目錄 = Path(os.environ['TEMP']) / 'to_ocr'
# c = wmi.WMI()
# p = c.Win32_Processor()[0].ProcessorId

def 截圖辨字():
    def 儲存截圖():
        from zhongwen.圖 import 取圖內文
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

def 設定環境():
    待識圖目錄.mkdir(exist_ok=True)
    h = gethostname()
    if h.upper() in ['LAPTOP-6J3H5COA']:
        os.system('python -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116')

    for package in ['winshell', 'clipboard']:
        os.system(f'pip3 install {package}')

    winshell.CreateShortcut(
       Path=os.path.join(winshell.desktop(),"截圖辨字.lnk")
      ,Target=sys.executable
      ,Arguments=f'{Path(__file__)}'
      ,Icon=(sys.executable, 0)
      ,Description="截圖辨字"
    )
    print(f'建立捷徑[截圖辨字]。')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action="store_true")
    args = parser.parse_args()
    if args.setup:
        設定環境()
    else:
        截圖辨字()
