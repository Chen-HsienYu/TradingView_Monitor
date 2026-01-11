from flask import Flask, request
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)
DATA_FILE = "market_data.json"

# 時框映射表：將 TradingView 的代碼轉為我們顯示的格式
INTERVAL_MAP = {
    "15": "15m",
    "30": "30m",
    "240": "4h",
    "1D": "1d",
    "D": "1d"
}

# 初始化資料庫
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def get_current_time():
    # 使用美東時間
    tz = pytz.timezone('US/Eastern')
    return datetime.now(tz).strftime('%H:%M')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 1. 接收數據
        data = request.json
        print(f"🔥 收到訊號: {data}")
        
        # 2. 讀取現有資料
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    db = json.load(f)
            except: db = {}
        else:
            db = {}

        # 3. 解析數據
        ticker = data.get('ticker')
        tv_interval = str(data.get('interval')) # TradingView 傳來的時框 (如 "240")
        signal = data.get('signal')
        price = data.get('price')
        
        if ticker and tv_interval:
            # 如果是新股票，初始化結構
            if ticker not in db:
                db[ticker] = {
                    "price": price, 
                    "update_time": get_current_time(),
                    "15m": "-", "30m": "-", "4h": "-", "1d": "-"
                }
            
            # 更新基本資訊
            db[ticker]["price"] = price
            db[ticker]["update_time"] = get_current_time()
            
            # 4. 關鍵：將訊號歸位
            target_col = INTERVAL_MAP.get(tv_interval)
            
            if target_col:
                db[ticker][target_col] = signal
                print(f"✅ 更新成功: {ticker} [{target_col}] -> {signal}")
            else:
                print(f"⚠️ 未知時框代碼: {tv_interval}")

            # 5. 存檔
            with open(DATA_FILE, "w") as f:
                json.dump(db, f, indent=4)
                
        return "OK", 200
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return "Error", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port)