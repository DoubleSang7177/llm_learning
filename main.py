import json
import requests
from openai import OpenAI
import time

client = OpenAI(
    api_key='sk-8269b69d2ffc4c32aab3dd9dfdcfe2e5',
    base_url='https://api.deepseek.com'
)

messages = [
    {
        "role": "system",
        "content": """你是一个专业的加密货币交易员，擅长技术分析和宏观分析。

请用JSON格式输出：
{
  "direction": "",
  "reason": [],
  "levels": {
    "support": "",
    "resistance": ""
  },
  "risk": ""
}

不要输出任何解释"""
    }
]

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url, timeout=5)
    data = response.json()
    return float(data["price"])


def get_symbol(user_input):
    user_input = user_input.lower()

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

    valid_symbols = ['btc', 'eth', 'sol', 'zec', 'doge']

    for word in user_input.split():
        if word in valid_symbols:
            return word.upper() + "USDT"

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
        return float(low), float(high)
    else:
        val = float(level_str)
        return val, val


def do_long():
    print("🔥 做多")


def do_short():
    print("🔥 做空")


last_price = None

while True:
    user_input = 'btc'   # 你后面可以换 input()

    if user_input.lower() in ['exit', 'quit']:
        print('结束对话')
        break

    try:
        symbol = get_symbol(user_input)
        price = get_price(symbol)

        print("当前价格：", price)

        if last_price is None:
            last_price = price
            time.sleep(1)
            continue

        change = abs(price - last_price)
        percent = change/last_price

        if percent > 0.01:
            print("📈 触发AI分析")

            messages.append({
                "role": "user",
                "content": f"当前价格是{price}，{user_input}"
            })

            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=messages,
                timeout=30,
                max_tokens=500
            )

            api_reply = response.choices[0].message.content
            data = json.loads(api_reply)

            if '多' in data['direction'] or '涨' in data['direction']:
                print("👉 建议做多")

                sup_low, sup_high = parse_level(data["levels"]["support"])
                res_low, res_high = parse_level(data["levels"]["resistance"])

                print("支持：", sup_low, sup_high)
                print("压力：", res_low, res_high)

                if sup_low <= price <= sup_high * 1.01:
                    do_long()

            elif '空' in data['direction']:
                print("👉 建议做空")

                sup_low, sup_high = parse_level(data["levels"]["support"])
                res_low, res_high = parse_level(data["levels"]["resistance"])

                print("支持：", sup_low, sup_high)
                print("压力：", res_low, res_high)

                if res_low <= price <= res_high * 1.01:
                    do_short()

            else:
                print("震荡行情")

            print("原因：", data["reason"])
            print("风险：", data["risk"])

            messages.append({
                "role": "assistant",
                "content": api_reply
            })

        # ✅ 每轮都更新
        last_price = price

    except Exception as e:
        print("请求失败:", e)

    # ✅ 永远执行
    time.sleep(1)