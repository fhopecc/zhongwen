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

from zhipuai import ZhipuAI
client = ZhipuAI(api_key="7b337bd4c21e4ec5af06cd1e013cc7fd.TrI6SFhI6gcC1wp3")
response = client.chat.completions.create(
    model="glm-4-plus",  
    messages=[
        {"role": "user", "content": "台積電營收組成及市佔率"},
    ],
)
print(response)
