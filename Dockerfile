# ベースイメージを指定
FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係をコピー
COPY requirements.txt /app/
COPY runtime.txt /app/

# 依存関係をインストール
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . /app/

# 環境変数を設定
ENV PATH=/opt/venv/bin:$PATH

# デフォルトのコマンドを指定
CMD ["python", "app/kiyopybot.py"]
