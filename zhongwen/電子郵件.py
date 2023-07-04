import os
import email
import base64
     
def 另存附件(電子郵件檔, 儲存目錄=None):
    '儲存目錄預設為執行檔目錄'
    if not 儲存目錄:
        from pathlib import Path
        儲存目錄 = Path(__file__).parent
    output_dir = 儲存目錄
    eml_file = 電子郵件檔 
    with open(eml_file, 'rb') as file:
        eml_data = file.read()
    msg = email.message_from_bytes(eml_data)

    for part in msg.walk():
        if part.get_content_disposition() and 'attachment' in part.get_content_disposition():
            filename = part.get_filename()
            if filename:
                attachment_data = part.get_payload(decode=True)
                save_path = os.path.join(output_dir, filename)
                with open(save_path, 'wb') as attachment_file:
                    attachment_file.write(attachment_data)
                print(f'附件儲存為{filename}！')
