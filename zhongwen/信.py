def eml_to_html(eml_path):
    import os
    from email import policy
    from email.parser import BytesParser
    from pathlib import Path

    # 讀取並解析 .eml 檔案
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # 取得郵件主旨作為檔名（過濾掉非法字元）
    subject = msg.get('Subject', 'no_subject')
    safe_subject = "".join([c for c in subject if c.isalnum() or c in (' ', '-', '_')]).rstrip()
    output_filename = f"{safe_subject}.html"

    # 尋找郵件中的 HTML 內容，若無則取純文字
    html_content = msg.get_body(preferencelist=('html', 'plain')).get_content()

    # 組合簡單的 HTML 標頭資訊（方便列印時看到主旨與日期）
    header_info = f"""
    <div style="font-family: sans-serif; border-bottom: 2px solid #ccc; margin-bottom: 20px; padding-bottom: 10px;">
        <h2>Subject: {subject}</h2>
        <p><b>From:</b> {msg.get('From')}</p>
        <p><b>Date:</b> {msg.get('Date')}</p>
    </div>
    """
    
    final_html = f"<html><head><meta charset='utf-8'></head><body>{header_info}{html_content}</body></html>"

    # 儲存檔案
    with open(Path(eml_path).with_suffix('.html') , 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"已轉換: {output_filename}")

def 取信函內文(eml_path):
    """
    解析 .eml 檔案並直接回傳格式化後的純文字字串。
    """
    from email import policy
    from email.parser import BytesParser
    try:
        with open(eml_path, 'rb') as f:
            # 使用 default policy 會自動處理 Base64 與 Quoted-printable 編碼
            msg = BytesParser(policy=policy.default).parse(f)

        # 提取元數據
        subject = msg.get('Subject', '(無主旨)')
        sender = msg.get('From', '(未知寄件者)')
        date = msg.get('Date', '(未知日期)')
        
        # 優先提取純文字 (plain)，若郵件只有 HTML 則提取 HTML
        body_part = msg.get_body(preferencelist=('plain', 'html'))
        
        if body_part:
            content = body_part.get_content()
        else:
            content = "(此郵件無內文內容)"

        # 組合回傳字串
        result = [
            f"Subject: {subject}",
            f"From: {sender}",
            f"Date: {date}",
            "-" * 40,
            content
        ]
        
        return "\n".join(result)

    except Exception as e:
        return f"解析錯誤: {str(e)}"
