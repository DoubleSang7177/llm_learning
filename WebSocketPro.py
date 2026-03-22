import time
import requests
from dotenv import load_dotenv
import os
from py_clob_client.client import ClobClient

load_dotenv()

# ========= 配置 =========
TARGET = os.getenv("TARGET").lower()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

FOLLOW_RATIO = 0.2
REAL_TRADE = False   # ❗ 先保持False

# 风控参数
MAX_ORDER_SIZE = 3
MIN_SIZE = 20
PRICE_MIN = 0.4
PRICE_MAX = 0.6

# ========= 使用已保存的 API 凭证（🔥核心改动） =========
creds = {
    "api_key": os.getenv("API_KEY"),
    "api_secret": os.getenv("API_SECRET"),
    "passphrase": os.getenv("API_PASSPHRASE"),
}

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,
    key=PRIVATE_KEY,
    creds=creds
)

print("✅ Polymarket client ready")

# ========= 状态 =========
seen_ids = set()
market_activity = {}

# ========= 下单 =========
def place_order(token_id, side, price, size):

    print("\n🚨 跟单触发")
    print(token_id, side, price, size)

    if not REAL_TRADE:
        print("🧪 模拟下单")
        return

    try:
        order = client.create_order(
            token_id=token_id,
            side=side.upper(),
            price=price,
            size=size,
        )

        res = client.post_order(order)
        print("✅ 下单成功:", res)

    except Exception as e:
        print("❌ 下单失败:", e)

# ========= 过滤 =========
def should_follow(t):
    try:
        price = float(t["price"])
        size = float(t["size"])

        if price < PRICE_MIN or price > PRICE_MAX:
            return False

        if size < MIN_SIZE:
            return False

        return True

    except:
        return False

# ========= 热度判断 =========
def is_hot_market(market):
    now = time.time()

    if market not in market_activity:
        market_activity[market] = []

    market_activity[market].append(now)

    # 保留5秒
    market_activity[market] = [
        t for t in market_activity[market] if now - t < 5
    ]

    return len(market_activity[market]) >= 3

# ========= 处理交易 =========
def process_trade(t):

    try:
        trade_id = t["id"]

        if trade_id in seen_ids:
            return

        seen_ids.add(trade_id)

        token_id = t["asset_id"]
        market = t["market"]
        side = t["side"]
        price = float(t["price"])
        size = float(t["size"])

        print("🧪 新成交:", market, side, price, size)

        # 过滤
        if not should_follow(t):
            return

        # 热度
        if not is_hot_market(market):
            return

        # 仓位
        my_size = min(size * FOLLOW_RATIO, MAX_ORDER_SIZE)

        # 滑点
        if side == "buy":
            my_price = price + 0.003
        else:
            my_price = price - 0.003

        place_order(token_id, side, my_price, my_size)

    except Exception as e:
        print("❌ process error:", e)

# ========= 主循环（🔥稳定轮询版） =========

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Connection": "keep-alive"
}

def poll_trades():
    print("🚀 开始监听 Polymarket trades")

    fail_count = 0

    while True:
        try:
            r = session.get(
                "https://clob.polymarket.com/trades",
                headers=headers,
                timeout=10
            )

            if r.status_code != 200:
                print("⚠️ status:", r.status_code)
                fail_count += 1
                time.sleep(min(5, fail_count))
                continue

            fail_count = 0  # ✅ 成功就清零

            data = r.json()

            if "data" not in data:
                time.sleep(1)
                continue

            trades = data["data"]

            print(f"✅ 收到 {len(trades)} 条交易")

        except Exception as e:
            print("❌ poll error:", e)
            fail_count += 1

            # 🔥 核心：指数退避（防封）
            sleep_time = min(10, 2 ** fail_count)
            print(f"⏳ 重试等待 {sleep_time}s")
            time.sleep(sleep_time)

        # 🔥 降频（非常关键）
        time.sleep(2)

# ========= 启动 =========
if __name__ == "__main__":
    poll_trades()