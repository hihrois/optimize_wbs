import csv
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import jpholiday  # 日本の祝日ライブラリ
from dotenv import load_dotenv

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))

from src.backend.config.load_config import load_config


def is_business_day(date):
    """指定された日付が営業日かどうかを判定する関数"""
    return date.weekday() < 5 and not jpholiday.is_holiday(date)


# 営業日のみを扱うための関数（祝日も除外）
def generate_business_days(start_date, total_days):
    business_days = []
    current_date = start_date
    days_added = 0

    # 営業日のみを取得するループ
    while days_added < total_days:
        if is_business_day(current_date):
            business_days.append(current_date.strftime("%Y-%m-%d"))
            days_added += 1
        current_date += timedelta(days=1)

    return business_days


def convert_into_abs(loaded_info, result_class):
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


class UnloadStrategy(ABC):
    # def __init__(self):
    #     # .envファイルの内容を読み込む
    #     load_dotenv()

    #     # .envファイルから環境変数を取得
    #     self.project_root_path = os.getenv("PROJECT_ROOT_PATH")
    #     self.config = load_config()["load"]
    #     self.input_folder_path = self.config["input_folder_path"]

    #     self.loaded_dataframe = LoadedDataframe(
    #         pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    #     )
    @abstractmethod
    def unload(self, loaded_info, result_class, task_assignments_abs_date):
        pass


class CsvUnloader(UnloadStrategy):
    def unload(self, loaded_info, result_class, task_assignments_abs_date):
        # .envファイルの内容を読み込む
        load_dotenv()

        # .envファイルから環境変数を取得
        project_root_path = os.getenv("PROJECT_ROOT_PATH")
        config = load_config()["load"]
        input_folder_path = config["input_folder_path"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = project_root_path + input_folder_path.replace("input", "output")
        output_path = (
            project_root_path
            + input_folder_path.replace("input", "output")
            + "output_"
            + timestamp
            + ".csv"
        )

        # ヘッダーも設定したいならここで定義
        header = ["Employee", "Task", "StartTime", "EndTime"]

        # ファイルに書き出し
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)  # ヘッダー行
            writer.writerows(task_assignments_abs_date)  # データ本体


def unload_result(loaded_info, result_class):
    # インスタンス化
    # loader = CsvLoader()
    task_assignments_abs_date = convert_into_abs(loaded_info, result_class)
    unloader = CsvUnloader()
    unloader.unload(loaded_info, result_class, task_assignments_abs_date)

    return
