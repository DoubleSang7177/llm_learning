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

def parse_level(level_str):
    if '-' in level_str:
        low, high = level_str.split('-')
        low = float(low)
        high = float(high)
    else:
        low = high = float(level_str)
    return low,high

def do_long():
    print("做多")

def do_short():
    print("做空")

while True:
    user_input = input("你：")

    if user_input.lower() in ['exit','quit']:
        print('结束对话')
        break


    # 用户输入加入上下文
    price = get_btc_price()
    print('当前价格： ', price)
    messages.append({"role":"user","content":f"当前比特币价格是{price},{user_input}"})

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
        # print('data: ',data)
        if '多' in data['direction'] or '涨' in data['direction']:
            print("👉 建议做多")
            support_low,support_high = parse_level(data["levels"]["support"])
            print("支持位置：",support_low,support_high)
            res_low,res_high = parse_level(data["levels"]["resistance"])
            print("压力位：", res_low,res_high)
            if support_low <= price <= support_high*1.01:
                do_long()
            print('原因： ',data['reason'])
            print("风险：", data["risk"])
        elif '空' in data['direction'] :
            print("👉 建议做空")
            support_low, support_high = parse_level(data["levels"]["support"])
            print("支持位置：", support_low, support_high)
            res_low, res_high = parse_level(data["levels"]["resistance"])
            print("压力位：", res_low, res_high)
            if res_low * -1.01 <= price <= res_high:
                do_short()
            print('原因： ', data['reason'])
            print("风险：", data["risk"])
        else:
            print('震荡为主，没有明确方向')

        # ai回复加入上下文
        messages.append({"role": "assistant", "content": api_reply})

    except Exception as e:
        print("请求失败",e)
        print('👉 可能是网络问题，重试一下')




