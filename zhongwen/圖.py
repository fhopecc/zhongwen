
def has_NVIDIA_GPU():
    from pynvml import nvmlInit, nvmlDeviceGetCount
    from pynvml import nvmlDeviceGetHandleByIndex, nvmlDeviceGetName
    from pynvml import nvmlDeviceGetMemoryInfo, nvmlShutdown
    try:
        nvmlInit()
        deviceCount = nvmlDeviceGetCount()
        if deviceCount > 0:
            print(f"检测到 {deviceCount} 个 NVIDIA GPU！")
            for i in range(deviceCount):
                handle = nvmlDeviceGetHandleByIndex(i)
                print(f"GPU {i}: {nvmlDeviceGetName(handle)}")
                # 可以获取更多信息，例如内存使用
                # info = nvmlDeviceGetMemoryInfo(handle)
                # print(f"  总内存: {info.total / (1024**3):.2f} GB")
                # print(f"  已使用内存: {info.used / (1024**3):.2f} GB")
                return True
        else:
            print("未检测到 NVIDIA GPU。")
        nvmlShutdown()
        return False
    except NVMLError as error:
        print(f"NVML 初始化失败或未检测到 NVIDIA 驱动: {error}")
        print("请确保已安装 NVIDIA 驱动程序。")
    except ImportError:
        print("pynvml 模块未安装。请运行 'pip install pynvml' 安装。")
        print("未检测到 GPU。")
    return False

def 安裝必要套件():
    from zhongwen.python_dev import 安裝套件
    import torch
    import os
    import paddle
    # if has_NVIDIA_GPU():
        # cmd = 'python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/'
        # os.system(cmd) 
        # 安裝套件('paddlepaddle-gpu')
    # else:
    安裝套件('paddlepaddle')
    paddle.utils.run_check()
    安裝套件('paddleocr')   

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

    # 如果需要，將 RGB 轉換為 BGR (OpenCV 和某些深度學習框架的預設)
    # PaddleOCR 的 `ocr()` 方法可以直接處理 RGB 陣列，但有些其他函式或庫可能需要 BGR
    # 如果確定 PaddleOCR 可以直接處理 RGB，這一步可以省略。
    # 通常為了相容性，尤其當與 OpenCV 協作時，會轉換為 BGR。
    # 如果 img_np 只有2個維度 (灰度圖)，則不需要轉換
    if len(img_np.shape) == 3 and img_np.shape[2] == 3: # 確保是彩色圖片
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    return img_np

def 取圖內文(圖):
    '圖可為 numpy.ndarray 或圖檔路徑'
    from paddleocr import PaddleOCR
    import numpy as np
    if not isinstance(圖, np.ndarray):
        # 不是陣列就是圖檔路徑，但只接受路徑字串表示
        圖 = 取圖陣列(str(圖))
    print(圖)
    ocr = PaddleOCR(
        use_doc_orientation_classify=False, 
        use_doc_unwarping=False, 
        use_textline_orientation=False) # 文本检测+文本识别
    result = ocr.predict(圖)
    return result

if __name__ == '__main__':
    安裝必要套件()
