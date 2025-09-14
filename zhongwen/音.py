from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 轉錄文字(音檔, 語言="zh"):
    """
    運用 OpenAI Whisper 進行語音轉錄文字。
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
