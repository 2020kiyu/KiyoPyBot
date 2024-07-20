# ベースイメージを設定
FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# 依存関係をインストール
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

# 環境変数を設定
ENV PATH="/opt/venv/bin:$PATH"

# アプリケーションコードをコピー
COPY . /app

# アプリケーションを起動
CMD ["python", "main.py"]
