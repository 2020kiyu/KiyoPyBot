# ベースイメージを指定
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をキャッシュするためのディレクトリを作成
RUN mkdir -p /root/.cache/pip

# Python仮想環境を作成し、依存関係をインストール
# キャッシュを使用してビルド速度を向上
RUN --mount=type=cache,id=pip_cache,target=/root/.cache/pip \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# アプリケーションのコードをコンテナにコピー
COPY app/ /app/

# 環境変数を設定
ENV PATH="/opt/venv/bin:$PATH"

# コンテナが起動したときに実行するコマンドを指定
CMD ["python", "main.py"]
