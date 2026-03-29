import json
import requests
from openai import OpenAI
import time
import re

client = OpenAI(
    api_key='sk-8269b69d2ffc4c32aab3dd9dfdcfe2e5',
    base_url='https://api.deepseek.com'
)

# ===== 策略 =====
TREND_STRATEGY = """
趋势行情：
- 顺势做单
- 回调做多或反弹做空
- 不逆势
"""

RANGE_STRATEGY = """
震荡行情：
- 高空低多
- 接近支撑做多
- 接近压力做空
- 不追单
"""

# ===== 加载规则 =====
def load_rules():
    with open('rules.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    rules_text = ''
    for r in data['rules']:
        rules_text += f"{r['condition']} → {r['action']}\n"

    return rules_text

rules = load_rules()

# ===== 市场状态判断 =====
def detect_market_state(price_history):
    if len(price_history) < 5:
        return "noise"

    diff = max(price_history) - min(price_history)

    if diff < 50:
        return "range"
    elif diff < 200:
        return "noise"
    else:
        return "trend"

# ===== 获取价格 =====
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

    return None

# ===== 获取币种 =====
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

# ===== 解析支撑/压力 =====
def parse_level(level_str):
    nums = re.findall(r'\d+\.?\d*', str(level_str))

    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    elif len(nums) == 1:
        val = float(nums[0])
        return val, val
    else:
        return None, None

# ===== 执行动作 =====
def do_long():
    print("🔥 做多")

def do_short():
    print("🔥 做空")

# ===== 主循环 =====
last_price = None
price_history = []

while True:
    user_input = 'btc怎么看'  # 后面可以换 input()

    if user_input.lower() in ['exit', 'quit']:
        print('结束对话')
        break

    try:
        symbol = get_symbol(user_input)
        price = get_price(symbol)

        if price is None:
            continue

        price_history.append(price)

        if len(price_history) > 100:
            price_history.pop(0)

        print("当前价格：", price)

        if last_price is None:
            last_price = price
            time.sleep(1)
            continue

        change = abs(price - last_price)

        my_confidence = 0

        # ===== 市场判断 =====
        state = detect_market_state(price_history)

        # 趋势行情
        if state == 'trend':
            my_confidence += 0.3

        if state == "noise":
            last_price = price
            time.sleep(1)
            continue

        # ===== 选择策略 =====
        if state == "trend":
            strategy = TREND_STRATEGY
        elif state == "range":
            strategy = RANGE_STRATEGY
        else:
            strategy = ""

        # ===== 触发AI =====
        if change > 5 and len(price_history) >= 5:
            my_confidence += 0.3

            print("📈 触发AI分析")

            messages = [
                {
                    "role": "system",
                    "content": f"""
你是一个专业的加密货币交易员。

当前市场状态：{state}

当前使用策略：
{strategy}

你的交易策略如下：
{rules}

你必须严格按照上述策略进行分析，
所有结论必须对应具体规则，
如果无法匹配，请输出观望。

请基于“价格走势”进行分析，而不是单点价格。

请用JSON格式输出：
{{
  "direction": "",
  "confidence": 0.0,
  "reason": [],
  "levels": {{
    "support": "",
    "resistance": ""
  }},
  "risk": ""
}}
"""
                },
                {
                    "role": "user",
                    "content": f"最近价格走势是{price_history}，当前价格是{price}，{user_input}"
                }
            ]

            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=messages,
                timeout=30,
                max_tokens=500
            )

            api_reply = response.choices[0].message.content
            # print("AI返回:", api_reply)
            try:
                api_reply = api_reply.strip('```json').strip('```').strip()
                data = json.loads(api_reply)
            except:
                print("❌ JSON解析失败")
                continue

            ai_conf = data.get("confidence", 0)

            if '多' in data['direction'] or '涨' in data['direction']:
                print("👉 建议做多")

                sup_low, sup_high = parse_level(data["levels"]["support"])
                res_low, res_high = parse_level(data["levels"]["resistance"])

                print("支持：", sup_low, sup_high)
                print("压力：", res_low, res_high)

                if sup_low is not None and sup_high is not None and sup_low <= price <= sup_high * 1.01:
                    my_confidence += 0.4

                final_conf = 0.5 * ai_conf + 0.5 * my_confidence

                if final_conf > 0.6:
                    do_long()
                else:
                    print("❌ 信号不够强，不执行")

            elif '空' in data['direction']:
                print("👉 建议做空")

                sup_low, sup_high = parse_level(data["levels"]["support"])
                res_low, res_high = parse_level(data["levels"]["resistance"])

                print("支持：", sup_low, sup_high)
                print("压力：", res_low, res_high)

                if res_low is not None and res_high is not None and res_low <= price <= res_high * 1.01:
                    my_confidence += 0.4

                final_conf = 0.5 * ai_conf + 0.5 * my_confidence
                if final_conf > 0.6:
                    do_short()
                else:
                    print("❌ 信号不够强，不执行")

            else:
                print("震荡行情")

            print("原因：", data.get("reason"))
            print("风险：", data.get("risk"))

        last_price = price

    except Exception as e:
        print("请求失败:", e)

    time.sleep(1)