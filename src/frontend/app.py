import sys
from dotenv import load_dotenv
load_dotenv()
import os
sys.path.append(os.getenv('PROJECT_ROOT_PATH'))
import streamlit as st
from src.backend.main import main
from PIL import Image

# バックエンドで実行される関数
# def run_some_process():
#     # ここに実行したい処理を記述
#     return "バックエンドで関数が実行されました！"

# フロントエンド部分
st.title('WBS Optimization')

# ボタンの設置
if st.button('Execute'):
    # ボタンが押された場合に実行される処理
    unique_filename = main()
    # Streamlitアプリのタイトル
    st.title('Result')

    # ローカルの画像ファイルを読み込む
    image = Image.open(unique_filename)

    # 画像を表示
    st.image(image, caption='Example Image', use_column_width=True)