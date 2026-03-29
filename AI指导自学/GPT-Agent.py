import json
import requests
from openai import OpenAI
import time

client = OpenAI(
    api_key='sk-8269b69d2ffc4c32aab3dd9dfdcfe2e5',
    base_url='https://api.deepseek.com'
)

# ===== 工具定义 =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "获取某个加密货币的实时价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "do_long",
            "description": "执行做多操作",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "do_short",
            "description": "执行做空操作",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# ===== 获取价格 =====
def get_price(symbol, retries=3):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            # ✅ 防崩溃
            if "price" not in data:
                print("❌ 返回异常:", data)
                return None

            return float(data["price"])

        except Exception as e:
            print(f"获取价格失败，第{i+1}次重试:", e)
            time.sleep(1)

    return None


# ===== symbol清洗（核心🔥）=====
def normalize_symbol(raw_symbol, fallback="BTCUSDT"):
    if not raw_symbol:
        return fallback

    raw_symbol = raw_symbol.upper().replace("/", "")

    if raw_symbol in ["BTC", "BTCUSDT"]:
        return "BTCUSDT"
    elif raw_symbol in ["ETH", "ETHUSDT"]:
        return "ETHUSDT"

    return fallback


# ===== 执行动作 =====
def do_long():
    print("🔥 做多")

def do_short():
    print("🔥 做空")

has_called_price = False
# ===== 主循环 =====
while True:
    user_input = "btc怎么看"

    messages = [
        {
            "role": "system",
            "content": """
你是一个加密交易Agent。

规则：
1. 必须先调用 get_price 获取价格
2. 获取价格后，必须立即做决策
3. 只能选择一个：
   - do_long
   - do_short
4. 不允许再次调用 get_price
5. 不允许询问用户
6. 不允许输出分析文字

你的目标：
快速完成交易决策

只允许调用工具，不允许输出文本
"""
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    try:
        for _ in range(5):

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            # ===== AI调用工具 =====
            if msg.tool_calls:
                tool_call = msg.tool_calls[0]

                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")

                print("🧠 AI调用工具:", tool_name, args)

                # ===== 工具执行 =====
                if tool_name == "get_price":

                    # 🚫 防止重复调用（关键）
                    if has_called_price:
                        print("⚠️ 已获取价格，禁止重复调用")
                        break

                    has_called_price = True

                    raw_symbol = args.get("symbol", "BTCUSDT")
                    clean_symbol = normalize_symbol(raw_symbol)

                    result = get_price(clean_symbol)
                    print("📊 当前价格:", result)

                elif tool_name == "do_long":
                    do_long()
                    break

                elif tool_name == "do_short":
                    do_short()
                    break

                else:
                    result = "unknown tool"

                # ===== 加入上下文 =====
                messages.append(msg)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            else:
                print("AI:", msg.content)
                break

    except Exception as e:
        print("请求失败:", e)

    time.sleep(2)