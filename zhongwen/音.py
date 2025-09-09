import logging
logger = logging.getLogger(Path(__file__).stem)

def 設定環境():
    r"""
    一、安裝套件 pdf2image，先至github下載 poppler-windows 預編檔，
        放到 poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin'
    """
    from zhongwen.winman import 增加檔案右鍵選單功能
    import sys
    
    cmd = f'cmd.exe /c "{sys.executable} -m zhongwen.音 --arrange %1 || pause"'
    增加檔案右鍵選單功能('轉錄文檔', cmd, 'audio')

def 音轉文(音檔, 語言="zh"):
    """
    使用 OpenAI Whisper 進行語音轉文字。
    """
    import whisper

    # 載入 Whisper 模型，
    # 'base' 為基礎模型，尚有 'small', 'medium', 'large'
    # 模型越大，精準度越高，惟所需的運算資源也越多

    model = whisper.load_model("base")
    logger.info("正在將音訊轉為文字...")
    result = model.transcribe(str(音檔), language=語言) # 設定語言為中文
    text = result["text"]
    logger.info(f"轉錄文字：\r{text}")
    return text

def 轉錄文檔(音檔):
    from pathlib import Path
    
    音檔 = Path(音檔)
    文 = 音轉文(音檔)
    文檔 = 音檔.with_suffix(".txt")
    文檔.write_text(文)

if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action='store_true')
    parser.add_argument('--to_txt', type=str, help='轉錄文字')
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif audio := args.to_txt:
        音轉文(audio)
