import streamlit as st
import pandas as pd
import json
import time
import os

# ==========================================
# 1. 頁面基礎設定
# ==========================================
# 移除 page_icon 參數
st.set_page_config(page_title="Mark 美股智能戰情室", layout="wide")

# CSS 美化
st.markdown("""
    <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
        h3 {border-bottom: 2px solid #444; padding-bottom: 10px; margin-top: 30px; font-size: 1.5em;}
        .stDataFrame {font-size: 1.1em;}
        div[data-testid="stCaptionContainer"] {font-size: 1.0em;}
    </style>
""", unsafe_allow_html=True)

# 標題移除 Emoji
st.title("Mark 美股智能戰情室")
st.caption("全板塊監控系統 | 訊號來源: TradingView Webhook | 時框: 15m/30m/4h/1D")

# ==========================================
# 2. 定義股票板塊分類
# ==========================================
SECTOR_MAP = {
    "明星科技股": ["TSLA", "NVDA", "AAPL", "AMZN", "META", "NFLX", "ORCL", "PLTR", "MU", "AMD", "AVGO", "TSM", "QCOM", "ADBE", "DIS"],
    "英偉達持倉概念": ["NVDA", "APLD", "CRWV", "NBIS", "ARM", "WRD", "RXRX"],
    "核電": ["SMR", "OKLO", "UUUU", "NEE", "VST", "UEC", "NXE", "DJT", "LEU"],
    "量子計算": ["QBTS", "RGTI", "IONQ", "QUBT", "LAES"],
    "AI應用軟件": ["PLTR", "SOUN", "PATH", "TTD", "PINS", "ZETA", "TEM", "SHOP", "DOCU", "FIG", "RDDT", "SNOW", "MDB"],
    "特朗普概念": ["TSLA", "MARA", "DJT", "MSTR", "XOM", "CLSK", "RIOT", "COIN", "RUM", "UNH"],
    "智能駕駛": ["TSLA", "UBER"],
    "AI晶片": ["INTC", "NVDA", "TSM"],
    "加密貨幣": ["ASST", "SOFI", "BMNR", "BTBT", "BITF", "MARA", "MSTR", "IREN", "CLSK", "HOOD", "HIVE", "RIOT", "WULF", "CIFR", "GME", "COIN", "CRCL", "SBET", "GLXY", "HUT", "BTDR", "DJT"],
    "機器人概念": ["TSLA", "MBLY", "PATH", "RR", "SERV", "PDYN"],
    "無人機概念": ["ONDS", "ACHR", "JOBY", "RCAT", "KTOS", "UMAC", "AVAV"],
    "人工智慧": ["NVDA", "INTC", "SMCI", "NVTS", "AMD", "TSM", "AVGO", "QCOM"],
    "半導體概念": ["INTC", "NVDA", "MU", "AMD", "AVGO", "LRCX", "TSM", "AMAT", "SMCI", "NVTS"],
    "太空概念": ["RKLB", "ASTS", "SIDU", "RDW", "PL", "LUNR", "SATS", "VSAT", "DXYZ", "FJET"],
    "稀土": ["CRML", "UAMY", "UUUU", "MP", "USAR", "AREC", "NB", "EOSE"],
    "鋰礦電池": ["LAC", "QS", "LAR", "ENVX", "SGML", "ALAB"],
    "存儲概念": ["MU", "SNDK", "WDC", "STX"]
}

DATA_FILE = "market_data.json"

# ==========================================
# 3. 輔助函數
# ==========================================
def color_map(val):
    """定義訊號顏色"""
    s = str(val)
    if "強力買進" in s: return 'background-color: #2962FF; color: white; font-weight: bold' 
    if "買進40%" in s: return 'background-color: #004D40; color: white; font-weight: bold' 
    if "狙擊做空" in s: return 'background-color: #800000; color: white; font-weight: bold' 
    if "賣出40%" in s: return 'background-color: #D32F2F; color: white; font-weight: bold' 
    return ''

def load_data():
    """讀取本地 JSON 資料庫"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

# ==========================================
# 4. 主程式循環 (自動刷新)
# ==========================================
placeholder = st.empty()

while True:
    with placeholder.container():
        # A. 讀取最新數據
        db_data = load_data()
        
        # B. 遍歷每個板塊並渲染表格
        for sector_name, tickers in SECTOR_MAP.items():
            
            # 準備該板塊的數據列表
            sector_rows = []
            
            for ticker in tickers:
                stock_info = db_data.get(ticker, {})
                
                row = {
                    "商品": ticker,
                    "現價": f"{stock_info.get('price', '-')}",
                    "15m": stock_info.get('15m', '-'),
                    "30m": stock_info.get('30m', '-'),
                    "4h": stock_info.get('4h', '-'),
                    "1d": stock_info.get('1d', '-')
                }
                sector_rows.append(row)
            
            # 只有當板塊內有定義股票時才顯示
            if sector_rows:
                # 這裡原本有 📊 Emoji，已移除
                st.subheader(f"{sector_name}")
                
                df = pd.DataFrame(sector_rows)
                
                # 強制欄位順序
                cols = ["商品", "現價", "15m", "30m", "4h", "1d"]
                df = df[cols]

                # 渲染表格
                st.dataframe(
                    df.style.applymap(color_map, subset=["15m", "30m", "4h", "1d"]),
                    height=(len(df) + 1) * 35 + 3,
                    use_container_width=True,
                    column_config={
                        "商品": st.column_config.TextColumn("商品", width="small"),
                        "現價": st.column_config.TextColumn("現價", width="small"),
                        "15m": st.column_config.TextColumn("15m", width="medium"),
                        "30m": st.column_config.TextColumn("30m", width="medium"),
                        "4h": st.column_config.TextColumn("4h", width="medium"),
                        "1d": st.column_config.TextColumn("1d", width="medium"),
                    },
                    hide_index=True 
                )
        
        st.caption(f"系統自動刷新中 | Last Updated: {time.strftime('%H:%M:%S')}")
        
    time.sleep(1)