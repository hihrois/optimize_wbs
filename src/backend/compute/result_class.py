import pandas as pd

# from dataclasses import dataclass
import re
import networkx as nx


class ResultClass:
    def __init__(
        self,
        problem,
        task_assignments,
        employees,
        tasks,
        dependencies,
        start_times_dict,
    ):
        self.problem_list = problem
        self.task_assignments_list = task_assignments
        self.employees_list = employees
        self.tasks_list = tasks
        self.dependencies_list = dependencies
        self.start_times_dict = start_times_dict

    # print(type(result))
    # print(type(task_assignments))
    # print(type(employees))
    # print(type(tasks))
    # print(type(dependencies))
    # print(type(start_times_dict))

    # def _validate_task_df(self):
    #     task_df = self.task_df
    #     employees_df = self.employees_df
    #     skills_df = self.skills_df
    #     dependencies_df = self.dependencies_df

    #     errors = []

    #     if task_df["Task"].isnull().any():
    #         errors.append("Task列にNaNが含まれています。")

    #     if (task_df["Task"].astype(str).str.strip() == "").any():
    #         errors.append("Task列に空文字列が含まれています。")

    #     if not task_df["Task"].is_unique:
    #         duplicated_tasks = task_df["Task"][task_df["Task"].duplicated()].unique()
    #         errors.append(
    #             f"Task列に重複する値が存在します（重複値: {duplicated_tasks.tolist()}）"
    #         )

    #     if task_df["ProcessingTime"].isnull().any():
    #         errors.append("ProcessingTime列にNaNが含まれています。")

    #     if (task_df["ProcessingTime"].astype(str).str.strip() == "").any():
    #         errors.append("ProcessingTime列に空文字列が含まれています。")

    #     for idx, value in task_df["DeadLineDate"].dropna().items():
    #         if not (re.fullmatch(r"\d{8}", str(int(value)))):
    #             errors.append(
    #                 f"DeadLineDate列の{idx}行目が不正なフォーマットです（値: {value}）"
    #             )

    #     # エラーまとめ
    #     if errors:
    #         raise ValueError("\n".join(errors))
    #     else:
    #         print("✅ 検証成功！問題ありません。")

    # def _validate_employees_df(self):
    #     task_df = self.task_df
    #     employees_df = self.employees_df
    #     skills_df = self.skills_df
    #     dependencies_df = self.dependencies_df

    #     errors = []

    #     # 1. Employee列のNaNチェック + 空文字列チェック
    #     if employees_df["Employee"].isnull().any():
    #         errors.append("Employee列にNaNが含まれています。")

    #     if (employees_df["Employee"].astype(str).str.strip() == "").any():
    #         errors.append("Employee列に空文字列が含まれています。")

    #     # 2. Rate列のNaNチェック
    #     if employees_df["Rate"].isnull().any():
    #         errors.append("Rate列にNaNが含まれています。")

    #     # if employees_df["Rate"].dtype not in ["float64", "int64"]:
    #     #     errors.append(
    #     #         f"Rate列の型がfloat64またはint64ではありません（実際: {employees_df['Rate'].dtype}）"
    #     #     )

    #     # 3. Rate列の範囲チェック（0以上1以下）
    #     invalid_rates = employees_df[
    #         (employees_df["Rate"] < 0) | (employees_df["Rate"] > 1)
    #     ]
    #     if not invalid_rates.empty:
    #         errors.append(
    #             f"Rate列に0〜1以外の値が含まれています（行番号: {invalid_rates.index.tolist()}）"
    #         )

    #     # エラーまとめ
    #     if errors:
    #         raise ValueError("\n".join(errors))
    #     else:
    #         print("✅ 検証成功！問題ありません。")

    # def _validate_skills_df(self):
    #     task_df = self.task_df
    #     employees_df = self.employees_df
    #     skills_df = self.skills_df
    #     dependencies_df = self.dependencies_df

    #     errors = []

    #     required_columns = ["Employee", "Task", "IsCapable"]

    #     # 1. 必須列の存在確認
    #     for col in required_columns:
    #         if col not in skills_df.columns:
    #             errors.append(f"{col}列がskills_dfに存在しません。")

    #     # 2. 各列についてNaN・空文字チェック
    #     for col in required_columns:
    #         if skills_df[col].isnull().any():
    #             errors.append(f"{col}列にNaNが含まれています。")
    #         if (skills_df[col].astype(str).str.strip() == "").any():
    #             errors.append(f"{col}列に空文字列が含まれています。")

    #     # 3. Employee列の値がemployees_df["Employee"]に存在するかチェック
    #     valid_employees = set(employees_df["Employee"])
    #     invalid_employees = skills_df.loc[
    #         ~skills_df["Employee"].isin(valid_employees), "Employee"
    #     ]
    #     if not invalid_employees.empty:
    #         errors.append(
    #             f"Employee列に不正な値が含まれています（{invalid_employees.unique().tolist()}）"
    #         )

    #     # 4. Task列の値がtask_df["Task"]に存在するかチェック
    #     valid_tasks = set(task_df["Task"])
    #     invalid_tasks = skills_df.loc[~skills_df["Task"].isin(valid_tasks), "Task"]
    #     if not invalid_tasks.empty:
    #         errors.append(
    #             f"Task列に不正な値が含まれています（{invalid_tasks.unique().tolist()}）"
    #         )

    #     # エラーまとめ
    #     if errors:
    #         raise ValueError("\n".join(errors))
    #     else:
    #         print("✅ skills_df 検証成功！問題ありません。")

    # def _validate_dependencies_df(self):
    #     task_df = self.task_df
    #     employees_df = self.employees_df
    #     skills_df = self.skills_df
    #     dependencies_df = self.dependencies_df

    #     errors = []

    #     required_columns = ["BeforeTask", "AfterTask"]

    #     # 1. 必須列の存在確認
    #     for col in required_columns:
    #         if col not in dependencies_df.columns:
    #             errors.append(f"{col}列がdependencies_dfに存在しません。")

    #     # 2. 各列についてNaN・空文字チェック
    #     for col in required_columns:
    #         if dependencies_df[col].isnull().any():
    #             errors.append(f"{col}列にNaNが含まれています。")
    #         if (dependencies_df[col].astype(str).str.strip() == "").any():
    #             errors.append(f"{col}列に空文字列が含まれています。")

    #     # 3. 各列がtask_df["Task"]に存在するかチェック
    #     valid_tasks = set(task_df["Task"])

    #     invalid_before = dependencies_df.loc[
    #         ~dependencies_df["BeforeTask"].isin(valid_tasks), "BeforeTask"
    #     ]
    #     if not invalid_before.empty:
    #         errors.append(
    #             f"BeforeTask列に不正な値が含まれています（{invalid_before.unique().tolist()}）"
    #         )

    #     invalid_after = dependencies_df.loc[
    #         ~dependencies_df["AfterTask"].isin(valid_tasks), "AfterTask"
    #     ]
    #     if not invalid_after.empty:
    #         errors.append(
    #             f"AfterTask列に不正な値が含まれています（{invalid_after.unique().tolist()}）"
    #         )

    #     # 4. 循環関係（サイクル）検出
    #     if dependencies_df.shape[0] > 0:
    #         G = nx.DiGraph()
    #         G.add_edges_from(
    #             dependencies_df[["BeforeTask", "AfterTask"]].itertuples(
    #                 index=False, name=None
    #             )
    #         )
    #         try:
    #             cycle = nx.find_cycle(G, orientation="original")
    #             if cycle:
    #                 errors.append(f"依存関係に循環（サイクル）が存在します: {cycle}")
    #         except nx.NetworkXNoCycle:
    #             pass  # サイクルが無ければOK

    #     # エラーまとめ
    #     if errors:
    #         raise ValueError("\n".join(errors))
    #     else:
    #         print("✅ dependencies_df 検証成功！問題ありません。")

    # def validate(self) -> bool:
    #     # エラーの場合はその場でValueErrorをスロー
    #     self._validate_task_df()
    #     self._validate_employees_df()
    #     self._validate_skills_df()
    #     self._validate_dependencies_df()
    #     return True
