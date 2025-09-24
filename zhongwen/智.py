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
            {"role": "user", "content": f"請依據以下公司公布年報內容【{年報內容}】，用中文摘要公司收入組成、市占率及利潤率。"}
        ],
    )
    return response.choices[0].message.content

def 諮詢智譜(問題):
    '需連入中國網域'
    from zhongwen.時 import 今日
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=__zhipuai_api_key__)

    # 獲取當前日期，可以用於 System Prompt，幫助模型理解時間上下文
    current_date = str(今日)

    # 設定 System Prompt，引導模型具備網路搜尋能力
    # 這部分非常重要，它會告訴模型它的角色和如何使用網路資訊
    system_prompt = f"""
    你是一個具備網路搜尋能力的智能助手。
    在適當的時候，優先使用網路資訊（參考資訊）及繁體中文來回答，確保用戶獲得最新和最準確的幫助。
    當前日期是 {current_date}。
    """

    # 設定 Tools 參數，啟用網路搜尋功能
    # 具體的結構請參考智譜AI的 Web Search API 文件
    tools = [
        {
            "type": "web_search",
            "web_search": {
                "enable": True  # 設置為 True 表示啟用網路搜尋
                # 您也可以在這裡添加其他搜尋參數，例如：
                # "search_query": "自定義搜尋關鍵字"
                # "count": 5 # 返回的搜尋結果數量
            }
        }
    ]

    # 用戶提問
    user_question = 問題

    try:
        response = client.chat.completions.create(
            model="glm-4-plus",  # 使用支援搜尋功能的模型，例如 GLM-4
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            tools=tools, # 將啟用的 tools 傳遞給 API
            stream=False # 如果需要流式輸出，可以設為 True
        )

        # 如果模型使用了工具，響應中可能會包含 tool_calls 信息，
        # 具體如何解析可能需要參考智譜AI的文檔
        if response.choices[0].message.tool_calls:
            print("\n模型使用了工具：")
            for tool_call in response.choices[0].message.tool_calls:
                print(f"- 工具類型: {tool_call.type}")
                print(f"  調用詳細: {tool_call.function.name}({tool_call.function.arguments})")

        return response.choices[0].message.content
    except Exception as e:
        print(f"發生錯誤: {e}")

def 諮詢谷歌雙子星(問題, 服務金鑰=None):
    import google.generativeai as genai
    from clipboard import copy
    try:
        from fhopecc import 金鑰
        服務金鑰 = 金鑰.__gemini_api_key__
    except Exception:
        if not 服務金鑰:
            raise ValueError('請提供服務金鑰！')
    
    # genai.configure(api_key=服務金鑰)
    # model = genai.GenerativeModel("gemini-2.5-flash"
    #                              )
    # response = model.generate_content(問題)
    # print(response.text)
    # copy(response.text)
    # return response.text

    from google import genai
    from google.genai.types import (
        GenerateContentConfig,
        GoogleSearch,
        HttpOptions,
        Tool,
    )

    client = genai.Client(api_key=服務金鑰)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=問題,
        config=GenerateContentConfig(
            tools=[
                # Use Google Search Tool
                Tool(google_search=GoogleSearch())
            ],
        ),
    )
    print(response.text)
    copy(response.text)
    return response.text

def 詢問(問題, 服務金鑰=None):
    return 諮詢谷歌雙子星(問題, 服務金鑰=None)
