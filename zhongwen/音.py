
def 音轉文(filename, lang="zh-TW"):
    import speech_recognition as sr
    from pydub import AudioSegment
    recognizer = sr.Recognizer()

    # 如果不是 wav，就轉成 wav
    if not filename.endswith(".wav"):
        sound = AudioSegment.from_file(filename)
        filename = "temp.wav"
        sound.export(filename, format="wav")

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)

        try:
            # 使用 Google 語音辨識
            text = recognizer.recognize_google(audio_data, language=lang)
            return text
        except sr.UnknownValueError:
            return "無法辨識語音"
        except sr.RequestError as e:
            return f"無法連線到 Google API: {e}"
