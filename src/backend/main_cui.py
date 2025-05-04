import os
import sys

from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))
from src.backend.compute.define_and_solve import define_and_solve
from src.backend.load.load_input_file import load_input_file
from src.backend.output.unload import unload_result
from src.backend.output.unload_gantt_chart import unload_gantt_chart


def main():
    # 読み込み
    loaded_info = load_input_file()

    # 定式化・計算
    result_class = define_and_solve(loaded_info)

    # 可視化・出力
    # ガントチャートを作成・保存
    unload_gantt_chart(loaded_info, result_class)
    unload_result(loaded_info, result_class)


if __name__ == "__main__":
    # このスクリプトが直接実行された場合のみ呼ばれる
    main()
