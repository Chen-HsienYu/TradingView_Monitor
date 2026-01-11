# 使用 Python 基礎映像檔
FROM python:3.9-slim

# 安裝 Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製安裝清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼到雲端
COPY . .

# 設定 Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# 設定啟動腳本權限
RUN chmod +x entrypoint.sh

# 開放 80 Port (Railway 預設)
EXPOSE 80

# 啟動！
CMD ["./entrypoint.sh"]