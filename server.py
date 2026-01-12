from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# 資料庫檔案名稱
DATA_FILE = 'market_data.json'

# ==========================================
# 1. 核心修復：時框對照表 (Interval Mapping)
# ==========================================
# 這張表讓伺服器能看懂 TradingView 傳來的各種格式
INTERVAL_MAP = {
    # 分鐘級別
    "1m": "1m", "1": "1m",
    "3m": "3m", "3": "3m",
    "5m": "5m", "5": "5m",
    "15m": "15m", "15": "15m",
    "30m": "30m", "30": "30m",
    "45m": "45m", "45": "45m",
    
    # 小時級別 (TV 傳來的是分鐘數)
    "1h": "4h", "60": "4h",   # 視情況調整，如果您沒設1h欄位，可對應到其他或忽略
    "2h": "4h", "120": "4h",
    "4h": "4h", "240": "4h",  # 關鍵：4小時 = 240分鐘
    
    # 日線級別
    "1d": "1d", "D": "1d", "1D": "1d"
}

# 讀取數據函數
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}

# 儲存數據函數
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    return "Mark Master Monitor Server is Running! 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    接收 TradingView 警報的入口
    """
    try:
        # 1. 接收 JSON 資料
        data = request.json
        if not data:
            return "No JSON received", 400

        print(f"📩 Received Alert: {data}") # 在 Log 顯示收到的原始資料

        # 2. 提取關鍵欄位
        ticker = data.get('ticker')
        raw_interval = str(data.get('interval')) # 強制轉字串，避免數字報錯
        signal = data.get('signal')
        price = data.get('price')

        # 3. 欄位映射 (解決 502 錯誤的關鍵)
        # 使用 get 查找，如果找不到對應的時框，target_col 會是 None
        target_col = INTERVAL_MAP.get(raw_interval)

        # 防呆機制：如果是不支援的時框，就不處理
        if not target_col:
            error_msg = f"⚠️ Warning: Unknown interval '{raw_interval}' from {ticker}. Skipped."
            print(error_msg)
            return error_msg, 400

        # 4. 讀取現有資料庫
        db = load_data()

        # 如果這支股票不在資料庫裡，先幫它開一個戶頭
        if ticker not in db:
            db[ticker] = {}

        # 5. 更新數據
        # 寫入訊號 (例如 "強力買進")
        db[ticker][target_col] = signal
        
        # (選用) 如果想紀錄現價，可以寫入另一個欄位，或更新前端顯示
        db[ticker]["現價"] = price

        # 6. 存檔
        save_data(db)
        
        print(f"✅ Data Saved: {ticker} [{target_col}] -> {signal}")
        return "Webhook received and processed", 200

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return f"Internal Server Error: {e}", 500

if __name__ == '__main__':
    # 根據 Railway 的環境變數設定 Port，本地端預設跑 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)