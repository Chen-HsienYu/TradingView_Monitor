#!/bin/bash

# 1. 啟動 Nginx (交通指揮官)
service nginx start

# 2. 啟動 Flask (接收器) - 在後台運行
python server.py &

# 3. 啟動 Streamlit (顯示器)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0