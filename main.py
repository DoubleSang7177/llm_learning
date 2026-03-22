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

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])

def get_symbol(user_input):
    user_input = user_input.lower()

    # ===== 1️⃣ 中文映射（优先级最高）=====
    symbol_map = {
        "比特币": "BTC",
        "大饼": "BTC",
        "以太坊": "ETH",
        "以太": "ETH",
        "二饼": "ETH",
        "狗狗币": "DOGE",
    }

    for k, v in symbol_map.items():
        if k in user_input:
            return v + "USDT"

    # ===== 2️⃣ 英文单词匹配（标准用户）=====
    valid_symbols = ['btc', 'eth', 'sol', 'zec', 'doge']

    words = user_input.split()
    for word in words:
        if word in valid_symbols:
            return word.upper() + "USDT"

    # ===== 3️⃣ 英文字符提取（兜底方案）=====
    symbol = ""
    for c in user_input:
        if c.isascii() and c.isalpha():
            symbol += c

    if symbol:
        return symbol.upper() + "USDT"

    return None

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
    symbol = get_symbol(user_input)
    price = get_price(symbol)
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




