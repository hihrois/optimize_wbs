import sys
from dotenv import load_dotenv
# .envファイルを読み込む
load_dotenv()
import os
sys.path.append(os.getenv('PROJECT_ROOT_PATH'))
import pandas as pd
from src.backend.load.load_input_file import load_input_file
from src.backend.compute.define_and_solve import define_and_solve
from src.backend.visualize.visualize_result import plot_gantt_chart

def main():
  # 読み込み
  loaded_dataframe = load_input_file()

  # 定式化・計算
  result = define_and_solve(loaded_dataframe)

  # 可視化・出力
  # ガントチャートを表示
  result_image_file_name = plot_gantt_chart(result)

  return result_image_file_name


if __name__ == "__main__":
  # このスクリプトが直接実行された場合のみ呼ばれる
  main()