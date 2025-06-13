__zhipuai_api_key__="7b337bd4c21e4ec5af06cd1e013cc7fd.TrI6SFhI6gcC1wp3"
def 設定環境():
    from zhongwen.python_dev import 安裝套件
    for 套件 in ['zhipuai']:
        安裝套件(套件)

def deepseek():
    from openai import OpenAI

    client = OpenAI(api_key="sk-53cb1eee5c7d47ad88f45c1ca9d9a65a", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "數字科技公司(台股代號5287)營收組成及市佔率"},
        ],
        stream=False
    )
    print(response.choices[0].message.content)

def 摘要(原始內容):
    '需連入中國網域'
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=__zhipuai_api_key__)
    response = client.chat.completions.create(
        model="glm-4-plus",  
        messages=[
            {"role": "system", "content": "你是一個專業的中文摘要助手。"},
            {"role": "user", "content": f"請幫我摘要以下內容：{原始內容}"}
        ],
    )
    print(response)

def 取年報摘要(年報內容):
    '需連入中國網域'
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=__zhipuai_api_key__)
    response = client.chat.completions.create(
        model="glm-4-plus",  
        messages=[
            {"role": "system", "content": "你是一個專業財報分析師"},
            {"role": "user", "content": f"請依據以下公司公布年報內容，用中文摘要公司收入組成、市占率及利潤率：{年報內容}"}
        ],
    )
    return response.choices[0].message.content

def 詢問(問題):
    '需連入中國網域'
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=__zhipuai_api_key__)
    response = client.chat.completions.create(
        model="glm-4-plus",  
        messages=[
            {"role": "system", "content": "你是一個繁體中文資訊助理"},
            {"role": "user", "content": f"請用繁體中文回答以下問題：{問題}"}
        ],
    )
    return response.choices[0].message.content


