import json
import requests
from openai import OpenAI
import time
import re

client = OpenAI(
    api_key='sk-8269b69d2ffc4c32aab3dd9dfdcfe2e5',
    base_url='https://api.deepseek.com'
)

def load_rules():
    with open('rules.json','r',encoding='utf-8') as f:
        data = json.load(f)
    rules_text = ''
    for r in data['rules']:
        rules_text += f"{r['condition']} → {r['action']}\n"
    return rules_text



rules = load_rules()
messages = [
    {
        "role": "system",
        "content": f"""你是一个专业的加密货币交易员。
        
你的交易策略如下：
{rules}
要求：
- 你必须严格按照上述交易策略进行分析，
- 所有结论必须能对应到具体策略，
- 如果无法匹配任何策略，请输出“观望”。


请基于“价格走势”进行分析，而不是单点价格。

分析步骤：
1. 判断短期趋势（上涨 / 下跌 / 震荡）
2. 判断当前价格所处位置（高位 / 低位 / 区间）
3. 给出支撑位和压力位
4. 最后给出交易方向（看多 / 看空 / 观望）

请用JSON格式输出：
{{
  "direction": "",
  "reason": [],
  "levels": {{
    "support": "",
    "resistance": ""
  }},
  "risk": ""
}}

要求：
- 必须基于给定价格走势分析
- 不要输出任何解释，只输出JSON。如果无法输出JSON，请返回空JSON
- 不要胡编价格
- 如果无法判断，请输出观望
"""
    }
]

def get_price(symbol, retries=3):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            return float(data["price"])

        except Exception as e:
            print(f"获取价格失败，第{i+1}次重试:", e)
            time.sleep(1)

    # 所有重试都失败
    return None


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
    # 提取所有数字（核心！！！）
    nums = re.findall(r'\d+\.?\d*', level_str)

    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    elif len(nums) == 1:
        val = float(nums[0])
        return val, val
    else:
        return None, None


def do_long():
    print("🔥 做多")


def do_short():
    print("🔥 做空")


last_price = None
price_history = []
while True:
    user_input = 'btc怎么看'   # 你后面可以换 input()

    if user_input.lower() in ['exit', 'quit']:
        print('结束对话')
        break

    try:
        symbol = get_symbol(user_input)
        price = get_price(symbol,3)
        if price is None:
            continue

        price_history.append(price)
        # 限制长度（很重要）
        if len(price_history) > 200:
            price_history.pop(0)

        print("当前价格：", price)

        if last_price is None:
            last_price = price
            time.sleep(1)
            continue

        change = abs(price - last_price)
        percent = change/last_price

        if change > 5 and len(price_history) >= 5: # 为了测试方便 实际为percent>0.01
            print("📈 触发AI分析")

            messages.append({
                "role": "user",
                "content": f"最近价格走势是{price_history}，当前价格是{price}，{user_input}"
            })

            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=messages,
                timeout=30,
                max_tokens=500
            )

            api_reply = response.choices[0].message.content
            print('api_reply: ',api_reply)
            try:
                api_reply = api_reply.strip('```json').strip('```').strip()
                data = json.loads(api_reply)
            except:
                print("data解析失败",api_reply)
                continue

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