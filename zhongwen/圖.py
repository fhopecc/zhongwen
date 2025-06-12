def 安裝依賴套件及程式():
    from zhongwen.python_dev import 安裝套件
    import os
    for 應用程式 in ['tesseract', 'tesseract-languages']:
        os.system(f'scoop install {應用程式}')
    安裝套件('pytesseract')

def 取圖陣列(圖):
    '取圖的 ndarray 表示'
    from PIL import Image
    import numpy as np
    import cv2 
    import os
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
