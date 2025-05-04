import csv
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime

from dotenv import load_dotenv

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))

from src.backend.compute.result_class import ResultClass
from src.backend.config.load_config import load_config
from src.backend.load.load_input_file import AbstractInputLoad
from src.backend.output.utils import generate_business_days


def convert_into_abs(loaded_info: AbstractInputLoad, result_class: ResultClass) -> list:
    """
    タスク割り当ての開始・終了時間（時間単位）を営業日ベースの日付（文字列）に変換する。

    `result_class` に含まれるタスク割り当て結果（時間単位）を、
    プロジェクト開始日と 1日あたりの作業時間に基づいて、
    実際の営業日（日付）形式に変換したリストを返す。

    Args:
        loaded_info (AbstractInputLoad): プロジェクト設定（開始日や作業時間）を含む入力データローダー。
        result_class (ResultClass): 最適化によって得られたタスク割り当て結果。

    Returns:
        list: 各タスクの割り当て情報のリスト。
              要素は (従業員名, タスク名, 開始日, 終了日) のタプルで、日付は "YYYY-MM-DD" 形式の文字列。
    """
    task_assignments = result_class.task_assignments_list
    # print(result_class.task_assignments_list)
    project_start_date = loaded_info.config_input["common"]["project"]["start_date"]
    regular_time = loaded_info.config_input["common"]["employee"]["regular_time"]

    # X軸の目盛りを「8時間=1日」として調整し、日付を営業日のみをproject_start_dateに基づいて設定
    max_time = max([end for _, _, _, end in task_assignments])  # 最大時間を取得
    total_days = max_time // regular_time + 1  # 日数を計算

    # 営業日のみのラベルを作成（祝日も除外）
    project_start_date = datetime.strptime(project_start_date, "%Y%m%d")
    date_labels = generate_business_days(project_start_date, int(total_days))

    # 3項目目と4項目目を加工するlambda
    convert_into_abs_date = lambda x: int(x) // regular_time

    task_assignments_abs_date = [
        (
            name,
            task,
            date_labels[convert_into_abs_date(val3)],
            date_labels[convert_into_abs_date(val4)],
        )
        for name, task, val3, val4 in task_assignments
    ]

    print(task_assignments_abs_date)
    return task_assignments_abs_date


class AbstractUnload(ABC):
    @abstractmethod
    def unload(
        self,
        loaded_info: AbstractInputLoad,
        result_class: ResultClass,
        task_assignments_abs_date: list,
    ) -> None:
        pass


class CsvUnloader(AbstractUnload):
    def unload(
        self,
        loaded_info: AbstractInputLoad,
        result_class: ResultClass,
        task_assignments_abs_date: list,
    ) -> None:
        """
        タスク割り当て結果をCSVファイルに出力する。

        出力先パスは `.env` の PROJECT_ROOT_PATH と設定ファイルの input_folder_path に基づいて動的に決定される。
        出力ファイル名にはタイムスタンプ（YYYYMMDD_HHMMSS）が付与される。

        Args:
            loaded_info (AbstractInputLoad): 入力ファイルのロードに使ったローダー。パス構成などの設定を利用。
            result_class (ResultClass): 最適化処理によって得られた結果（未使用だが、将来的な拡張用に保持）。
            task_assignments_abs_date (list): 書き出すデータのリスト。形式は [(従業員, タスク, 開始日, 終了日), ...]。

        Returns:
            None
        """
        # .envファイルの内容を読み込む
        load_dotenv()

        # .envファイルから環境変数を取得
        project_root_path = os.getenv("PROJECT_ROOT_PATH")
        config = load_config()["load"]
        input_folder_path = config["input_folder_path"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = project_root_path + input_folder_path.replace("input", "output")
        output_path = f"{output_dir}output_{timestamp}.csv"

        # ヘッダーも設定したいならここで定義
        header = ["Employee", "Task", "StartTime", "EndTime"]

        # ファイルに書き出し
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)  # ヘッダー行
            writer.writerows(task_assignments_abs_date)  # データ本体


def unload_result(loaded_info: AbstractInputLoad, result_class: ResultClass) -> None:
    """
    最適化結果を実行形式（CSVファイル）に変換・保存する処理を実行する。

    この関数は、タスク割り当て結果（時間単位）を営業日ベースの日付に変換し、
    `CsvUnloader` を用いてCSVファイルとして出力する一連の流れをカプセル化している。

    Args:
        loaded_info (AbstractInputLoad): プロジェクト設定と入力データを含むローダー。
        result_class (ResultClass): 最適化によって得られたタスク割り当て結果。

    Returns:
        None
    """
    # インスタンス化
    # loader = CsvLoader()
    task_assignments_abs_date = convert_into_abs(loaded_info, result_class)
    unloader = CsvUnloader()
    unloader.unload(loaded_info, result_class, task_assignments_abs_date)
