# ベースイメージを設定
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要な環境変数を設定
ENV PATH="/opt/venv/bin:$PATH"

# 依存関係をインストールする前に、キャッシュディレクトリをマウント
RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip python -m venv --copies /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# メインスクリプトを実行
CMD ["python", "main.py"]
