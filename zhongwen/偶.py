def 傳訊(訊):
    import requests
    import os
    # 建議將這些機密資訊放在 GitHub Secrets
    # token = os.environ.get('TG_TOKEN') 
    # chat_id = os.environ.get('TG_CHAT_ID')
    token = '8606697912:AAHBp2x1RJbVc6utMNEBKmtmO5zgacuv7k8' 
    chat_id = '7311282350'
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": 訊,
        "parse_mode": "Markdown" # 支援粗體、連結等格式
    }
    
    response = requests.post(url, data=payload)
    return response.json()
