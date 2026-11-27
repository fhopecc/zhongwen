from pathlib import Path
import os
import sys

待識圖目錄 = Path(
    os.environ["TEMP"]
) / "to_ocr"


# PaddleOCR 模型快取
_PADDLE_OCR = None

# OpenCC 轉換器快取
_OPENCC = None


def 設定環境():
    """
    建立截圖辨字桌面捷徑。

    捷徑預設：
    1. 使用 PaddleOCR。
    2. 將辨識結果轉成臺灣繁體中文。
    3. 不保留 OCR 區塊換行。
    """
    import winshell
    import sys

    待識圖目錄.mkdir(
        parents=True,
        exist_ok=True,
    )

    程式路徑 = Path(
        __file__
    ).resolve()

    捷徑路徑 = os.path.join(
        winshell.desktop(),
        "截圖辨字.lnk",
    )

    winshell.CreateShortcut(
        Path=捷徑路徑,
        Target=sys.executable,
        Arguments=(
            f'"{程式路徑}" '
            "--OCR "
            "--engine paddle"
        ),
        Icon=(
            sys.executable,
            0,
        ),
        Description="截圖辨字",
    )

    print(
        "建立捷徑[截圖辨字]。"
    )


def 安裝語言資料():
    """
    安裝 Tesseract 日文及日文直排語言資料。

    PaddleOCR 不使用這些語言資料；
    此函式只供 Tesseract 使用。
    """
    from zhongwen.檔 import 下載

    tesseract執行檔清單 = list(
        Path(
            os.environ["ProgramFiles"]
        ).glob(
            r"**/tesseract.exe"
        )
    )

    if not tesseract執行檔清單:
        raise FileNotFoundError(
            "在 Program Files 中找不到 tesseract.exe。"
        )

    tessdata_dir = (
        tesseract執行檔清單[0].parent
        / "tessdata"
    )

    jpn_url = (
        "https://github.com/"
        "tesseract-ocr/"
        "tessdata_fast/"
        "raw/refs/heads/main/"
        "jpn.traineddata"
    )

    jpn_vert_url = (
        "https://github.com/"
        "tesseract-ocr/"
        "tessdata_fast/"
        "raw/refs/heads/main/"
        "jpn_vert.traineddata"
    )

    for url in [
        jpn_url,
        jpn_vert_url,
    ]:
        下載(
            url,
            儲存目錄=tessdata_dir,
        )


def 取圖陣列(圖):
    """
    將圖片轉換為 OpenCV 使用的 BGR ndarray。

    支援的輸入類型：
    1. str
    2. pathlib.Path
    3. PIL.Image.Image
    4. bytes
    5. numpy.ndarray

    回傳：
        numpy.ndarray
    """
    from PIL import Image
    import numpy as np
    import cv2
    import io

    if isinstance(
        圖,
        np.ndarray,
    ):
        return 圖

    img_pil = None

    if isinstance(
        圖,
        (
            str,
            Path,
        ),
    ):
        圖 = Path(
            圖
        )

        if not 圖.exists():
            raise FileNotFoundError(
                f"圖片檔案不存在：{圖}"
            )

        try:
            img_pil = Image.open(
                圖
            ).convert(
                "RGB"
            )

        except Exception as e:
            raise ValueError(
                f"無法讀取圖片檔案「{圖}」，"
                "請檢查檔案是否損壞，"
                "或格式是否受支援。"
                f"錯誤：{e}"
            ) from e

    elif isinstance(
        圖,
        Image.Image,
    ):
        img_pil = 圖.convert(
            "RGB"
        )

    elif isinstance(
        圖,
        bytes,
    ):
        try:
            img_pil = Image.open(
                io.BytesIO(
                    圖
                )
            ).convert(
                "RGB"
            )

        except Exception as e:
            raise ValueError(
                "無法從二進位資料讀取圖片，"
                "請檢查資料是否為有效圖片格式。"
                f"錯誤：{e}"
            ) from e

    else:
        raise ValueError(
            "不支援的圖片輸入類型。"
            "請提供檔案路徑、"
            "PIL.Image、bytes 或 "
            "NumPy ndarray。"
        )

    img_np = np.array(
        img_pil
    )

    # PIL 使用 RGB；
    # OpenCV 通常使用 BGR。
    if (
        len(
            img_np.shape
        ) == 3
        and img_np.shape[2] == 3
    ):
        img_np = cv2.cvtColor(
            img_np,
            cv2.COLOR_RGB2BGR,
        )

    return img_np


def load_paddle_ocr():
    """
    載入並快取 PaddleOCR 模型。

    第一次呼叫時建立 PaddleOCR 物件；
    後續呼叫直接使用已載入的物件。

    Windows CPU 環境停用 oneDNN，
    避免發生：

    ConvertPirAttribute2RuntimeAttribute
    not support pir::ArrayAttribute

    的推論錯誤。
    """
    global _PADDLE_OCR

    if _PADDLE_OCR is None:
        from paddleocr import PaddleOCR

        print(
            "正在載入 PaddleOCR 模型，"
            "第一次執行可能需要下載模型……"
        )

        _PADDLE_OCR = PaddleOCR(
            # 繁體中文辨識模型
            lang="chinese_cht",

            # Windows CPU 停用 oneDNN，
            # 避免目前環境中的推論錯誤。
            enable_mkldnn=False,

            # 截圖通常已是正向畫面，
            # 不需要整頁方向分類。
            use_doc_orientation_classify=False,

            # 截圖不是彎曲紙張，
            # 不需要文件展平。
            use_doc_unwarping=False,

            # 一般截圖先不啟用文字行方向分類。
            use_textline_orientation=False,
        )

        print(
            "PaddleOCR 模型載入完成。"
        )

    return _PADDLE_OCR


def load_opencc():
    """
    載入並快取 OpenCC 轉換器。

    使用 s2twp：
    1. 簡體轉繁體。
    2. 使用臺灣慣用詞彙。
    3. 進行臺灣常用字詞調整。

    例如：
        事项 → 事項
        软件 → 軟體
        网络 → 網路
        信息 → 資訊
    """
    global _OPENCC

    if _OPENCC is None:
        try:
            from opencc import OpenCC

        except ImportError as e:
            raise ImportError(
                "尚未安裝 OpenCC。\n"
                "請執行：\n"
                "py -m pip install "
                "opencc-python-reimplemented"
            ) from e

        _OPENCC = OpenCC(
            "s2twp"
        )

    return _OPENCC


def 轉為繁體(
    文字,
    使用臺灣詞彙=True,
):
    """
    將文字轉換為繁體中文。

    參數
    ----
    文字：
        要轉換的文字。

    使用臺灣詞彙：
        True：
            使用 s2twp。
            簡體轉臺灣繁體，並轉換臺灣慣用詞。

        False：
            使用 s2t。
            僅做簡體轉繁體，不進行臺灣詞彙轉換。

    回傳
    ----
    str
        轉換後的繁體中文文字。

    注意
    ----
    OpenCC 是簡繁字詞轉換工具，
    不是 OCR 錯字校正工具。

    例如：
        项 → 項

    可以轉換；但若 OCR 把「項」誤辨成
    完全不相關的字，OpenCC 不會自行推測原字。
    """
    if 文字 is None:
        return ""

    文字 = str(
        文字
    )

    if not 文字:
        return 文字

    try:
        if 使用臺灣詞彙:
            轉換器 = load_opencc()

        else:
            from opencc import OpenCC

            轉換器 = OpenCC(
                "s2t"
            )

        return 轉換器.convert(
            文字
        )

    except Exception as e:
        print(
            f"繁體中文轉換失敗：{e}"
        )

        # 轉換失敗時保留原始 OCR 結果，
        # 不讓整個 OCR 流程失敗。
        return 文字


def paddleocr(
    圖,
    最低信心值=0.0,
    保留換行=True,
    轉為繁體中文=True,
    使用臺灣詞彙=True,
):
    """
    使用 PaddleOCR 辨識圖片文字。

    參數
    ----
    圖：
        圖片檔案路徑、Path、
        PIL Image、bytes 或 ndarray。

    最低信心值：
        範圍為 0.0 至 1.0。

        0.0：
            保留全部辨識結果。

        0.8：
            僅保留信心值 >= 0.8 的文字。

    保留換行：
        True：
            各 OCR 文字區塊以換行分隔。

        False：
            將全部文字直接連接。

    轉為繁體中文：
        True：
            使用 OpenCC 將結果轉為繁體。

        False：
            保留 PaddleOCR 原始輸出。

    使用臺灣詞彙：
        True：
            使用 OpenCC s2twp。

        False：
            使用 OpenCC s2t。

    回傳
    ----
    str
        OCR 辨識文字。
    """
    if not (
        0.0
        <= 最低信心值
        <= 1.0
    ):
        raise ValueError(
            "最低信心值必須介於 "
            "0.0 與 1.0 之間。"
        )

    ocr = load_paddle_ocr()

    圖陣列 = 取圖陣列(
        圖
    )

    結果 = ocr.predict(
        圖陣列
    )

    文字清單 = []

    for 頁結果 in 結果:
        資料 = 頁結果.json

        # 相容 json 屬性或 json 方法。
        if callable(
            資料
        ):
            資料 = 資料()

        if not isinstance(
            資料,
            dict,
        ):
            continue

        辨識結果 = 資料.get(
            "res",
            資料,
        )

        if not isinstance(
            辨識結果,
            dict,
        ):
            continue

        辨識文字 = 辨識結果.get(
            "rec_texts",
            [],
        )

        信心值 = 辨識結果.get(
            "rec_scores",
            [],
        )

        for 索引, 文字 in enumerate(
            辨識文字
        ):
            文字 = str(
                文字
            ).strip()

            if not 文字:
                continue

            分數 = 1.0

            if 索引 < len(
                信心值
            ):
                try:
                    分數 = float(
                        信心值[索引]
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    分數 = 1.0

            if 分數 >= 最低信心值:
                文字清單.append(
                    文字
                )

    分隔符號 = (
        "\n"
        if 保留換行
        else ""
    )

    文字 = 分隔符號.join(
        文字清單
    )

    if 轉為繁體中文:
        文字 = 轉為繁體(
            文字,
            使用臺灣詞彙=使用臺灣詞彙,
        )

    return 文字


def tesseract(
    圖,
    保留換行=True,
    轉為繁體中文=True,
    使用臺灣詞彙=True,
):
    """
    使用 Tesseract OCR 辨識繁體中文。

    Tesseract 使用 chi_tra 語言資料，
    但辨識結果仍可能出現簡體字或異體字。

    可選擇再使用 OpenCC 統一轉成臺灣繁體。
    """
    from PIL import Image
    import pytesseract
    import numpy as np
    import io

    if isinstance(
        圖,
        (
            str,
            Path,
        ),
    ):
        image = Image.open(
            圖
        )

    elif isinstance(
        圖,
        bytes,
    ):
        image = Image.open(
            io.BytesIO(
                圖
            )
        )

    elif isinstance(
        圖,
        Image.Image,
    ):
        image = 圖

    elif isinstance(
        圖,
        np.ndarray,
    ):
        import cv2

        if len(
            圖.shape
        ) == 3:
            圖 = cv2.cvtColor(
                圖,
                cv2.COLOR_BGR2RGB,
            )

        image = Image.fromarray(
            圖
        )

    else:
        raise ValueError(
            "不支援的圖片輸入類型。"
            "請提供檔案路徑、"
            "PIL.Image、bytes 或 ndarray。"
        )

    text = pytesseract.image_to_string(
        image,
        lang="chi_tra",
    )

    if 保留換行:
        行清單 = [
            行.strip()
            for 行 in text.splitlines()
            if 行.strip()
        ]

        text = "\n".join(
            行清單
        )

    else:
        text = text.replace(
            "\n",
            "",
        ).strip()

    if 轉為繁體中文:
        text = 轉為繁體(
            text,
            使用臺灣詞彙=使用臺灣詞彙,
        )

    return text


def 取圖內文(
    圖,
    引擎="paddle",
    最低信心值=0.0,
    保留換行=True,
    轉為繁體中文=True,
    使用臺灣詞彙=True,
    失敗時改用Tesseract=True,
):
    """
    取得圖片中的文字。

    預設流程：
        圖片
        → PaddleOCR
        → OpenCC 臺灣繁體
        → 回傳文字

    OCR 引擎：
        paddle
        tesseract

    若 PaddleOCR 發生例外，
    預設自動改用 Tesseract。
    """
    引擎 = 引擎.lower().strip()

    if 引擎 in {
        "paddle",
        "paddleocr",
    }:
        try:
            return paddleocr(
                圖,
                最低信心值=最低信心值,
                保留換行=保留換行,
                轉為繁體中文=轉為繁體中文,
                使用臺灣詞彙=使用臺灣詞彙,
            )

        except Exception as e:
            if not 失敗時改用Tesseract:
                raise

            print(
                f"PaddleOCR 辨識失敗：{e}"
            )

            print(
                "改用 Tesseract 辨識。"
            )

            return tesseract(
                圖,
                保留換行=保留換行,
                轉為繁體中文=轉為繁體中文,
                使用臺灣詞彙=使用臺灣詞彙,
            )

    if 引擎 == "tesseract":
        return tesseract(
            圖,
            保留換行=保留換行,
            轉為繁體中文=轉為繁體中文,
            使用臺灣詞彙=使用臺灣詞彙,
        )

    raise ValueError(
        f"不支援的 OCR 引擎：{引擎}。"
        "可用引擎為 paddle 或 tesseract。"
    )


def 截圖辨字(
    引擎="paddle",
    最低信心值=0.0,
    保留換行=False,
    轉為繁體中文=True,
    使用臺灣詞彙=True,
):
    """
    監聽 Windows 剪貼簿中的截圖。

    操作方式：
        按 Win + Shift + S，
        再以滑鼠選取截圖範圍。

    截圖完成後：
        1. 儲存暫存圖片。
        2. 執行 OCR。
        3. 轉成臺灣繁體中文。
        4. 印出結果。
        5. 將結果複製至剪貼簿。
    """
    from PIL import Image
    from PIL import ImageGrab

    import win32api
    import win32clipboard
    import win32con
    import win32gui

    import threading
    import ctypes
    import clipboard
    import time

    正在處理剪貼簿 = False

    def 儲存截圖():
        nonlocal 正在處理剪貼簿

        if 正在處理剪貼簿:
            return

        剪貼簿已開啟 = False
        有點陣圖 = False

        try:
            win32clipboard.OpenClipboard()

            剪貼簿已開啟 = True

            有點陣圖 = (
                win32clipboard
                .IsClipboardFormatAvailable(
                    win32con.CF_BITMAP
                )
            )

        except Exception:
            return

        finally:
            if 剪貼簿已開啟:
                win32clipboard.CloseClipboard()

        if not 有點陣圖:
            return

        try:
            im = ImageGrab.grabclipboard()

            if not isinstance(
                im,
                Image.Image,
            ):
                return

            正在處理剪貼簿 = True

            待識圖目錄.mkdir(
                parents=True,
                exist_ok=True,
            )

            圖檔 = (
                待識圖目錄
                / f"{time.time_ns()}.png"
            )

            im.save(
                圖檔,
                "PNG",
            )

            print(
                f"辨識圖片：{圖檔}"
            )

            文字 = 取圖內文(
                圖檔,
                引擎=引擎,
                最低信心值=最低信心值,
                保留換行=保留換行,
                轉為繁體中文=轉為繁體中文,
                使用臺灣詞彙=使用臺灣詞彙,
                失敗時改用Tesseract=True,
            )

            clipboard.copy(
                文字
            )

            print(
                "-" * 60
            )

            print(
                文字
            )

            print(
                "-" * 60
            )

            print(
                "辨識結果已複製至剪貼簿。"
            )

        except Exception as e:
            print(
                f"截圖辨字失敗：{e}"
            )

        finally:
            正在處理剪貼簿 = False

    def 監聽截圖(
        hwnd,
        msg,
        wparam,
        lparam,
    ):
        WM_CLIPBOARDUPDATE = 0x031D

        if msg == WM_CLIPBOARDUPDATE:
            儲存截圖()

        return 0

    def runner():
        wc = win32gui.WNDCLASS()

        wc.lpfnWndProc = 監聽截圖
        wc.lpszClassName = "監聽截圖"
        wc.hInstance = (
            win32api.GetModuleHandle(
                None
            )
        )

        try:
            class_atom = (
                win32gui.RegisterClass(
                    wc
                )
            )

        except Exception:
            # 如果同名視窗類別已經註冊，
            # 可直接使用類別名稱建立視窗。
            class_atom = (
                wc.lpszClassName
            )

        hwnd = win32gui.CreateWindow(
            class_atom,
            "監聽截圖",
            0,
            0,
            0,
            0,
            0,
            0,
            wc.hInstance,
            None,
        )

        ctypes.windll.user32.AddClipboardFormatListener(
            hwnd
        )

        win32gui.PumpMessages()

    if 引擎.lower() in {
        "paddle",
        "paddleocr",
    }:
        try:
            load_paddle_ocr()

        except Exception as e:
            print(
                f"PaddleOCR 載入失敗：{e}"
            )

            print(
                "後續辨識將嘗試使用 Tesseract。"
            )

    if 轉為繁體中文:
        try:
            load_opencc()

            print(
                "已啟用 OpenCC 臺灣繁體轉換。"
            )

        except Exception as e:
            print(
                f"OpenCC 載入失敗：{e}"
            )

            print(
                "OCR 將保留原始辨識結果。"
            )

    th = threading.Thread(
        target=runner,
        daemon=True,
    )

    th.start()

    print(
        f"啟動截圖辨字，OCR 引擎：{引擎}"
    )

    if 轉為繁體中文:
        print(
            "辨識結果將轉為臺灣繁體中文。"
        )

    else:
        print(
            "辨識結果將保留原始字形。"
        )

    print(
        "按 Win + Shift + S 後，"
        "以滑鼠選取螢幕截圖範圍。"
    )

    print(
        "辨識結果將儲存至系統剪貼簿。"
    )

    while th.is_alive():
        th.join(
            0.25
        )


def 取圖內表(
    圖檔,
    服務金鑰=None,
):
    """
    使用 Gemini 解析圖片中的表格，
    並回傳 OrgMode 表格。
    """
    from google import genai
    import PIL.Image

    try:
        from fhopecc import 金鑰

        服務金鑰 = (
            金鑰.__gemini_api_key__
        )

    except Exception:
        if not 服務金鑰:
            raise ValueError(
                "請提供服務金鑰！"
            )

    client = genai.Client(
        api_key=服務金鑰
    )

    image = PIL.Image.open(
        圖檔
    )

    response = (
        client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                (
                    "請精確解析圖中表格並轉換為 "
                    "OrgMode 表格格式，"
                    "同時確保每列數據對齊。"
                    "如有合併儲存格，"
                    "請盡量還原其邏輯結構。"
                ),
                image,
            ],
        )
    )

    return response.text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "圖片及 Windows 截圖 OCR 工具"
        )
    )

    parser.add_argument(
        "--setup",
        help="設定環境並建立桌面捷徑",
        action="store_true",
    )

    parser.add_argument(
        "--install_lang",
        help="安裝 Tesseract 日文語言資料",
        action="store_true",
    )

    parser.add_argument(
        "--OCR",
        help="啟動截圖辨字",
        action="store_true",
    )

    parser.add_argument(
        "--engine",
        choices=[
            "paddle",
            "tesseract",
        ],
        default="paddle",
        help=(
            "OCR 引擎，"
            "預設為 paddle"
        ),
    )

    parser.add_argument(
        "--min_score",
        type=float,
        default=0.0,
        help=(
            "PaddleOCR 最低信心值，"
            "範圍為 0.0 至 1.0"
        ),
    )

    parser.add_argument(
        "--keep_newline",
        action="store_true",
        help="保留 OCR 文字區塊換行",
    )

    parser.add_argument(
        "--no_traditional",
        action="store_true",
        help=(
            "不要使用 OpenCC 轉成臺灣繁體，"
            "保留 OCR 原始字形"
        ),
    )

    parser.add_argument(
        "--no_taiwan_phrases",
        action="store_true",
        help=(
            "只進行簡體轉繁體，"
            "不轉換臺灣慣用詞彙"
        ),
    )

    parser.add_argument(
        "--image",
        help="直接辨識指定圖片",
    )

    args = parser.parse_args()

    轉為繁體中文 = (
        not args.no_traditional
    )

    使用臺灣詞彙 = (
        not args.no_taiwan_phrases
    )

    if args.setup:
        設定環境()

    elif args.install_lang:
        安裝語言資料()

    elif args.image:
        文字 = 取圖內文(
            args.image,
            引擎=args.engine,
            最低信心值=args.min_score,
            保留換行=args.keep_newline,
            轉為繁體中文=轉為繁體中文,
            使用臺灣詞彙=使用臺灣詞彙,
        )

        print(
            文字
        )

    elif args.OCR:
        截圖辨字(
            引擎=args.engine,
            最低信心值=args.min_score,
            保留換行=args.keep_newline,
            轉為繁體中文=轉為繁體中文,
            使用臺灣詞彙=使用臺灣詞彙,
        )

    else:
        parser.print_help()
