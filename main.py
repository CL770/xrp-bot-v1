from flask import Flask, request, jsonify
import time, hmac, hashlib, requests, os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    if not API_KEY or not SECRET_KEY:
        return jsonify({"status": "error", "message": "API keys not set"}), 500

    data = request.get_json()
    symbol = data.get("symbol", "XRPUSDT")
    side = data.get("side", "BUY").upper()
    order_type = data.get("type", "MARKET").upper()
    quantity = data.get("quantity", 50)
    timestamp = int(time.time() * 1000)

    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "timestamp": timestamp
    }

    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    url = f"https://fapi.binance.com/fapi/v1/order?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}

    try:
        response = requests.post(url, headers=headers)
        print("Binance response:", response.status_code, response.text)
        response.raise_for_status()
        return jsonify({"status": "success", "binance_response": response.json()})
    except Exception as e:
        print("Binance error:", e)
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
