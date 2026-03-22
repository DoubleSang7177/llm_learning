import json
import requests
from openai import OpenAI

client = OpenAI(
    api_key='sk-8269b69d2ffc4c32aab3dd9dfdcfe2e5',
    base_url='https://api.deepseek.com'
)
messages = [
    {
        "role": "system",
        "content": """你是一个专业的加密货币交易员，擅长技术分析和宏观分析。

请用JSON格式输出，格式如下：
{
  "direction": "",
  "reason": [],
  "levels": {
    "support": "",
    "resistance": ""
  },
  "risk": ""
}

要求：
- 不要输出多余内容
- 语言简洁
- 像真实交易员
-不要输出任何解释，只输出JSON"""
    }
]

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])

while True:
    user_input = input("你：")

    if user_input.lower() in ['exit','quit']:
        print('结束对话')
        break


    # 用户输入加入上下文
    messages.append({"role":"user","content":user_input})

    try:
        # 请求ai
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            timeout=30,
            max_tokens=500
        )

        # 获取ai回复
        api_reply = response.choices[0].message.content
        data = json.loads(api_reply)
        price = get_btc_price()
        print('当前价格： ',price)
        if data['direction'] == '看多':
            print("👉 建议做多")
            print("支撑位：", data["levels"]["support"])
            print("压力位：", data["levels"]["resistance"])
            print("风险：", data["risk"])
        elif data['direction'] == '看空':
            print("👉 建议做空")
            print("支撑位：", data["levels"]["support"])
            print("压力位：", data["levels"]["resistance"])
            print("风险：", data["risk"])
        else:
            print('震荡为主，没有明确方向')

        # ai回复加入上下文
        messages.append({"role": "assistant", "content": api_reply})

    except Exception as e:
        print("请求失败",e)
        print('👉 可能是网络问题，重试一下')




