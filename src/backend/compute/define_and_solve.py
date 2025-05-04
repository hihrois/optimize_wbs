import os
import sys
from datetime import datetime, timedelta

import jpholiday  # 日本の祝日ライブラリ
import pandas as pd
import pulp

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))
from src.backend.compute.result_class import ResultClass
from src.backend.load.load_input_file import AbstractInputLoad


class SkillConflictException(Exception):
    """1と0の両方が同じタスクに存在する場合の例外"""

    # print(Exception)
    pass


class InfeasibleSolutionError(Exception):
    """解が infeasible の場合に投げられる例外"""

    pass


def calculate_hours(
    project_start_date: str, task_dead_line: str, regular_time: int
) -> int:
    """
    プロジェクト開始日から締切日までの平日かつ祝日を除いた労働日数を基に、総労働時間を計算する。

    Args:
        project_start_date (str): プロジェクトの開始日（"yyyymmdd"形式の文字列）。
        task_dead_line (str): タスクの締切日（"yyyymmdd"形式の文字列）。
        regular_time (int): 1日あたりの労働時間（時間単位、例：8）。

    Returns:
        int: 総労働時間（平日かつ祝日を除く日数 × 1日あたりの労働時間）。
    """
    # yyyymmdd形式の日付文字列をdatetimeオブジェクトに変換
    start_date = datetime.strptime(project_start_date, "%Y%m%d")
    end_date = datetime.strptime(task_dead_line, "%Y%m%d")

    # 労働日をカウントするための変数
    total_days = 0

    # 現在の日付をスタートとしてループし、土日祝日を除外して日数をカウント
    current_date = start_date
    while current_date <= end_date:
        # 平日かつ祝日でない場合のみ労働日としてカウント
        if current_date.weekday() < 5 and not jpholiday.is_holiday(current_date):
            total_days += 1
        current_date += timedelta(days=1)

    # 総労働時間を計算
    total_hours = total_days * regular_time

    return total_hours


def define_and_solve(loader: AbstractInputLoad) -> ResultClass:
    """
    タスク割り当て問題を定式化し、最適化ソルバー（PuLP）で解を求める。

    スキル、タスク処理時間、依存関係、従業員の稼働率などを考慮した上で
    最小メイクスパン（全タスク終了時間の最小化）を目的とする問題を解く。

    主な制約条件:
    - 各タスクは1人にのみ割り当てる
    - スキルがない従業員には割り当て不可
    - タスク依存関係を守る
    - タスクは締切内に完了すること
    - 同一従業員の同時タスク割り当て不可

    Args:
        loader (AbstractInputLoad): 入力データ（タスク、従業員、スキル、依存関係）を含むローダー

    Returns:
        ResultClass: 解の詳細（割り当て結果、開始・終了時間、依存関係など）

    Raises:
        SkillConflictException: 同一タスクに対してスキル1と0が混在している場合
        InfeasibleSolutionError: 問題に実行可能な解が存在しない場合
    """
    tasks_df = loader.loaded_dataframe.task_df
    employees_df = loader.loaded_dataframe.employees_df
    skills_df = loader.loaded_dataframe.skills_df
    dependencies_df = loader.loaded_dataframe.dependencies_df

    # config = load_config()["compute"]
    # project_start_date = config["project"]["start_date"]
    # regular_time = config["employee"]["regular_time"]

    config = loader.config_input["common"]
    project_start_date = config["project"]["start_date"]
    regular_time = config["employee"]["regular_time"]

    # タスクリストとその処理時間
    tasks = tasks_df["Task"].tolist()
    task_times = dict(zip(tasks_df["Task"], tasks_df["ProcessingTime"]))
    task_deadline = dict(
        zip(tasks_df["Task"], tasks_df["DeadLineDate"].astype(pd.Int64Dtype()))
    )

    # 従業員リスト
    employees = employees_df["Employee"].tolist()

    # 従業員の稼働率を取得 (例: 稼働率は0.5〜1.0の範囲)
    employee_rates = dict(zip(employees_df["Employee"], employees_df["Rate"]))

    # 全従業員は初期値としてNoneを設定
    employee_skills = {e: {t: None for t in tasks} for e in employees}

    # skills_dfのIsCapable列を参照して、1なら1、0なら0をemployee_skillsに設定
    for _, row in skills_df.iterrows():
        if employee_skills[row["Employee"]][row["Task"]] is not None:
            raise SkillConflictException(
                f"{row['Employee']} and {row['Task']} is already defined."
            )
        employee_skills[row["Employee"]][row["Task"]] = row["IsCapable"]

    # 各タスクについて1人以上1がいる場合、他の従業員に0を割り当てる
    # 1人以上0がいる場合、他の従業員に1を割り当てる
    for t in tasks:
        has_one = False
        has_zero = False

        # タスクについて1がいるか、0がいるかをチェック
        for e in employees:
            if employee_skills[e][t] == 1:
                has_one = True
            if employee_skills[e][t] == 0:
                has_zero = True

        # 1と0が同一のタスクに存在する場合は例外をスロー
        if has_one and has_zero:
            raise SkillConflictException(f"Task '{t}' has both 1 and 0 assignments.")

        elif not has_one and not has_zero:
            for e in employees:
                employee_skills[e][t] = 1

        # 1人以上1がいる場合、残りの従業員に0を割り当てる
        elif has_one:
            for e in employees:
                if employee_skills[e][t] != 1:
                    employee_skills[e][t] = 0

        # 1人以上0がいる場合、残りの従業員に1を割り当てる
        elif has_zero:
            for e in employees:
                if employee_skills[e][t] != 0:
                    employee_skills[e][t] = 1

    # タスクの依存関係をCSVからロード
    dependencies = list(
        zip(dependencies_df["BeforeTask"], dependencies_df["AfterTask"])
    )

    # 2. 問題の定義
    problem = pulp.LpProblem(
        "Task Assignment Problem with Makespan Minimization", pulp.LpMinimize
    )

    # 3. 変数の定義
    # バイナリ変数: 従業員がタスクに割り当てられるかどうか
    x = pulp.LpVariable.dicts(
        "assignment", [(e, t) for e in employees for t in tasks], cat="Binary"
    )

    # 各タスクの開始時間 (実数変数)
    start_times = pulp.LpVariable.dicts(
        "start_time", tasks, lowBound=0, cat="Continuous"
    )

    # 最終的な終了時間 (メイクスパン)
    makespan = pulp.LpVariable("makespan", lowBound=0, cat="Continuous")

    # 4. 目的関数の定義 (最後のタスクが終了するまでの時間を最小化)
    problem += makespan, "Minimize_Makespan"

    # 5. 制約条件
    # 各タスクは1人の従業員にのみ割り当てられる
    for t in tasks:
        problem += pulp.lpSum([x[e, t] for e in employees]) == 1, f"Task_{t}_assignment"

    # 従業員がスキルを持たないタスクには割り当てられない
    for e in employees:
        for t in tasks:
            if employee_skills[e][t] == 0:
                problem += x[e, t] == 0, f"{e}_cannot_do_{t}"

    # タスクの依存関係の制約 (BeforeTaskの終了時間 < AfterTaskの開始時間)
    for e in employees:
        for before, after in dependencies:
            problem += (
                start_times[after]
                >= start_times[before]
                + x[e, before] * task_times[before] / employee_rates[e],
                f"Dependency_{e}_{before}_before_{after}",
            )

    # for name, constraint in problem.constraints.items():
    #   print(f"{name}: {constraint}")

    # sys.exit()

    # 各タスクの終了時間はメイクスパン以下でなければならない
    for e in employees:
        for t in tasks:
            problem += (
                makespan
                >= start_times[t] + x[e, t] * task_times[t] / employee_rates[e],
                f"Makespan_constraint_{e}_{t}",
            )

    # タスク終了時間が締め切りより小さいことを追加
    for t in tasks:
        if isinstance(task_deadline[t], pd._libs.missing.NAType):
            continue
        problem += (
            start_times[t]
            + pulp.lpSum(
                [x[e, t] * task_times[t] / employee_rates[e] for e in employees]
            )
            <= calculate_hours(
                project_start_date, str(int(task_deadline[t])), regular_time
            ),
            f"Deadline_constraint_{t}",
        )

    # 同じ従業員が同じ時間に複数のタスクを処理しないようにする制約
    for e in employees:
        for t1 in tasks:
            for t2 in tasks:
                if t1 < t2:
                    problem += (
                        start_times[t1] + task_times[t1] / employee_rates[e]
                        <= start_times[t2] + (2 - x[e, t1] - x[e, t2]) * 9999,
                        f"Overlap_{e}_{t1}_{t2}_1",
                    )
                elif t1 > t2:
                    problem += (
                        start_times[t2] + task_times[t2] / employee_rates[e]
                        <= start_times[t1] + (2 - x[e, t1] - x[e, t2]) * 9999,
                        f"Overlap_{e}_{t1}_{t2}_2",
                    )

    # 6. 問題の解決
    problem.solve()
    # 結果が infeasible かどうかをチェック
    if pulp.LpStatus[problem.status] == "Infeasible":
        raise InfeasibleSolutionError("The problem is infeasible")

    # 7. 結果の表示
    task_assignments = []
    start_times_dict = {}
    print(f"Status: {pulp.LpStatus[problem.status]}")
    for e in employees:
        for t in tasks:
            if x[e, t].value() == 1:
                start = start_times[t].value()
                end = start + task_times[t] / employee_rates[e]
                task_assignments.append((e, t, start, end))
                start_times_dict[t] = (start, end)
                print(f"{e} is assigned to {t}. Start time: {start}.")

    # 最小化されたメイクスパン（最後のタスク終了時間）
    print(f"Makespan (total time): {pulp.value(makespan)} hours")

    result_class = ResultClass(
        problem_list=problem,
        task_assignments_list=task_assignments,
        employees_list=employees,
        tasks_list=tasks,
        dependencies_list=dependencies,
        start_times_dict=start_times_dict,
    )
    print(result_class.task_assignments_list)

    return result_class
