def 音轉文(音檔, 語言="zh-TW"):
    """
    使用 OpenAI Whisper 進行語音轉文字。
    """
    import whisper
    # 載入 Whisper 模型，'base' 為基礎模型，您也可以選擇 'small', 'medium', 'large'
    # 模型越大，精準度越高，但所需的運算資源也越多
    model = whisper.load_model("base")

    print("正在將音訊轉為文字...")
    
    # 執行轉錄
    result = model.transcribe(音檔, language=語言) # 設定語言為中文

    # 輸出結果
    print("轉錄文字：{}".format(result["text"]))
    return result
