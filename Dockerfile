# ベースイメージとしてPythonの公式イメージを使用
FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app
COPY . /app

# 必要なパッケージをインストール（システムパッケージとPythonパッケージ）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# pandas, pulp, streamlitの依存関係をインストール
RUN pip install -r requirements.txt

# ポート8501を公開 (Streamlit用)
EXPOSE 8501

# コンテナが起動したときのデフォルトコマンド
CMD ["streamlit", "run", "src/frontend/app.py"]
