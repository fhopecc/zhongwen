def 設定環境():
    from zhongwen.程式 import 安裝套件, 安裝程式
    安裝程式('ffmpeg-shared')
    安裝套件('yt-dlp')

def 下載音樂(url):
    """
    下載 YouTube 影片並轉換為 MP3 格式。

    Args:
        url (str): YouTube 影片的 URL。
    """
    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',  # 選擇最佳音訊格式
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # 使用 FFmpeg 提取音訊
            'preferredcodec': 'mp3',      # 轉換為 MP3
            'preferredquality': '192',    # MP3 品質，例如 192kbps
        }],
        'outtmpl': '%(title)s.%(ext)s',  # 輸出檔案名稱，以影片標題命名
        'noplaylist': True,  # 避免下載播放列表中的所有影片
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            print(f"'{info_dict.get('title', '影片')}' 已成功下載為 MP3。")
    except Exception as e:
        print(f"下載失敗: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action='store_true')
    parser.add_argument("--url", help="下載音樂")
    args = parser.parse_args()
    if args.setup:
        設定環境()
    elif args.url:
        下載音樂(args.url) 
