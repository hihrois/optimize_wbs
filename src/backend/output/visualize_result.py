import os
import sys
import uuid
from datetime import datetime, timedelta

import jpholiday  # 日本の祝日ライブラリ
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from dotenv import load_dotenv

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))
from src.backend.compute.result_class import ResultClass
from src.backend.load.load_input_file import AbstractInputLoad


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


# 8. ガントチャートの描画
def plot_gantt_chart(loader: AbstractInputLoad, result_class: ResultClass) -> str:
    """
    タスク割り当て結果に基づいて、従業員ごとのガントチャートを描画・保存する。

    タスクのスケジュール（開始・終了時間）、従業員別の色分け、タスク間の依存関係（矢印）、
    日付の営業日変換（祝日・土日除外）などを含んだ視覚的なスケジュール図を出力する。

    Args:
        loader (AbstractInputLoad): 入力設定を保持するローダー。プロジェクト開始日や勤務時間などを参照。
        result_class (ResultClass): 最適化によって得られた結果。タスク・従業員・依存関係などを含む。

    Returns:
        str: ガントチャート画像を保存したファイルパス（※現在は未保存で `plt.show()` のみ実行）。
    """

    # def __init__(
    #     self, problem, task_assignments, employees, tasks, dependencies, start_times_dict
    # ):
    #     self.problem_list = problem
    #     self.task_assignments_list = task_assignments
    #     self.employees_list = employees
    #     self.tasks_list = tasks
    #     self.dependencies_list = dependencies
    #     self.start_times_dict = start_times_dict

    problem = result_class.problem_list
    task_assignments = result_class.task_assignments_list
    employees = result_class.employees_list
    tasks = result_class.tasks_list
    dependencies = result_class.dependencies_list
    start_times_dict = result_class.start_times_dict

    config = loader.config_input["common"]
    project_start_date = config["project"]["start_date"]
    regular_time = config["employee"]["regular_time"]

    # project_start_dateをdatetime型に変換
    project_start_date = datetime.strptime(project_start_date, "%Y%m%d")

    fig, ax = plt.subplots(figsize=(10, 6))

    # 色を従業員ごとに設定
    colors = plt.cm.get_cmap("tab20", len(employees))
    employee_colors = {employee: colors(i) for i, employee in enumerate(employees)}

    task_pos = {}  # タスクの位置を保存しておく
    ypos = 0  # 初期の縦軸の位置

    # タスクごとにプロット
    for assignment in sorted(task_assignments, key=lambda x: x[1], reverse=True):
        employee, task, start, end = assignment
        ax.barh(
            task,
            end - start,
            left=start,
            color=employee_colors[employee],
            edgecolor="black",
        )
        task_pos[task] = ypos  # 各タスクのy座標位置を保存
        ypos += 1

    # 凡例を設定
    patches = [
        mpatches.Patch(color=employee_colors[employee], label=employee)
        for employee in employees
    ]
    ax.legend(handles=patches, title="Employees")

    # 依存関係に基づいて矢印を描画
    for before, after in dependencies:
        before_start, before_end = start_times_dict[before]
        after_start, _ = start_times_dict[after]
        ax.annotate(
            "",
            xy=(after_start, task_pos[after]),  # 矢印の先
            xytext=(before_end, task_pos[before]),  # 矢印の元
            arrowprops=dict(arrowstyle="->", color="black"),
        )

    # X軸の目盛りを「8時間=1日」として調整し、日付を営業日のみをproject_start_dateに基づいて設定
    max_time = max([end for _, _, _, end in task_assignments])  # 最大時間を取得
    total_days = max_time // regular_time + 1  # 日数を計算

    # 営業日のみのラベルを作成（祝日も除外）
    date_labels = generate_business_days(project_start_date, int(total_days))

    ax.set_xticks(
        [i * regular_time for i in range(len(date_labels))]
    )  # 営業日単位の目盛りを設定
    ax.set_xticklabels(date_labels)  # 日付ラベルに変換
    ax.set_xticklabels(date_labels, rotation=90)  # 日付ラベルを縦に回転

    # 軸ラベルとタイトルの設定
    ax.set_xlabel("Date")
    ax.set_ylabel("Tasks")
    ax.set_title("Gantt Chart for Task Assignments with Dependencies")

    # グリッドとフォーマットの設定
    ax.grid(True)
    plt.tight_layout()

    load_dotenv()

    # .envファイルから環境変数を取得
    PROJECT_ROOT_PATH = os.getenv("PROJECT_ROOT_PATH")

    # UUIDを使って一意なファイル名を作成
    unique_filename = f"{PROJECT_ROOT_PATH}data\output\{uuid.uuid4()}.png"

    # 画像を保存
    plt.show()
    # plt.savefig(unique_filename)

    return unique_filename  # 保存したファイル名を返す
