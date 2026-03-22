import time
import requests
import ssl
import certifi
import json
import threading
from web3 import Web3
from py_clob_client.client import ClobClient
from dotenv import load_dotenv
import os
import websocket


load_dotenv()

# ========= 配置 =========

RPC = os.getenv("RPC")
TARGET = Web3.to_checksum_address(os.getenv("TARGET"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

FOLLOW_RATIO = 0.2
REAL_TRADE = False

# ========= 初始化 =========

ssl_context = ssl.create_default_context(cafile=certifi.where())

w3 = Web3(
    Web3.LegacyWebSocketProvider(
        RPC,
        websocket_kwargs={"ssl": ssl_context}
    )
)

assert w3.is_connected(), "❌ WebSocket连接失败"
print("✅ Connected to Polygon")

# ========= Polymarket =========

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,
    key=PRIVATE_KEY
)

creds = client.create_or_derive_api_creds()

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,
    key=PRIVATE_KEY,
    creds=creds
)

# ========= 状态 =========

seen_tx = set()
seen_market = set()

# ========= 工具 =========

def get_trade_detail(tx_hash):
    try:
        url = f"https://clob.polymarket.com/trades?tx_hash={tx_hash}"
        r = requests.get(url, timeout=5)
        data = r.json()

        # 🔥 核心修复
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return []

    except Exception as e:
        print("❌ API error:", e)
        return []

def is_new_tx(tx_hash):
    if tx_hash in seen_tx:
        return False
    seen_tx.add(tx_hash)
    return True

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

# ========= 核心逻辑 =========

def process_tx(tx_hash):

    trades = get_trade_detail(tx_hash)
    print("DEBUG trades:", trades)
    if not trades:
        return

    for t in trades:

        # 🔥 防御式编程（关键）
        if not isinstance(t, dict):
            continue

        try:
            market = t.get("market")
            price = float(t.get("price", 0))

            if not market:
                continue

            print("🧪 trade:", t)

        except Exception as e:
            print("❌ process error:", e)

# ========= WebSocket订阅 =========

def on_message(ws, message):
    try:
        data = json.loads(message)

        if "params" in data:
            tx_hash = data["params"]["result"]

            if tx_hash:
                process_tx(tx_hash)

    except Exception as e:
        print("❌ message error:", e)


def on_open(ws):
    print("🚀 WebSocket订阅已启动")

    sub_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["newPendingTransactions"]
    }

    ws.send(json.dumps(sub_msg))


def on_error(ws, error):
    print("❌ WS错误:", error)


def on_close(ws, *args):
    print("⚠️ WebSocket断开，5秒后重连...")
    time.sleep(5)
    start_ws()


def start_ws():
    ws = websocket.WebSocketApp(
        RPC,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever(
        sslopt={
            "cert_reqs": ssl.CERT_REQUIRED,
            "ca_certs": certifi.where()
        }
    )


# ========= 启动 =========

if __name__ == "__main__":
    start_ws()