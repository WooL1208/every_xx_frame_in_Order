FROM python:3.9-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY . .

# 建立必要的目錄
RUN mkdir -p ./data/videos ./data/subtitles ./data/input ./data/output

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 開放端口
EXPOSE 7777

# 設定入口點
CMD ["python", "main.py"]
