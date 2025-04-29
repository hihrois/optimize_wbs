import os
from dotenv import load_dotenv
import pandas as pd
from dataclasses import dataclass
import sys
import yaml
from abc import ABC, abstractmethod

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))
from src.backend.config.load_config import load_config
from src.backend.load.loaded_dataframe import LoadedDataframe


class OutputStrategy(ABC):
    def __init__(self):
        # .envファイルの内容を読み込む
        load_dotenv()

        # .envファイルから環境変数を取得
        self.project_root_path = os.getenv("PROJECT_ROOT_PATH")
        self.config = load_config()["load"]
        self.input_folder_path = self.config["input_folder_path"]

        self.loaded_dataframe = LoadedDataframe(
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )

    @abstractmethod
    def load_input_file(self, path: str) -> LoadedDataframe:
        pass


class CsvLoader(InputLoaderStrategy):
    def load_input_file(self) -> LoadedDataframe:
        # CSVからデータを読み込む
        self.loaded_dataframe.task_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "tasks.csv"
        )
        self.loaded_dataframe.employees_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "employees.csv"
        )  # 稼働率列を含む
        self.loaded_dataframe.skills_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "skills.csv"
        )  # スキルがない情報のみ
        self.loaded_dataframe.dependencies_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "dependencies.csv"
        )

        print(self.loaded_dataframe)
        return self.loaded_dataframe


class YamlLoader(InputLoaderStrategy):
    def load_input_file(self) -> LoadedDataframe:
        root_path = self.project_root_path + self.input_folder_path + "input.yml"
        with open(root_path, "r") as f:
            config = yaml.safe_load(f)

        # 1. tasks_df
        task_rows = []
        dependencies_rows = []

        for task in config["task"]:
            task_name = task["task_name"]
            processing_time = task.get("processing_time", None)
            deadline = task.get("deadline", None)

            task_rows.append(
                {
                    "Task": task_name,
                    "ProcessingTime": processing_time,
                    "DeadLineDate": deadline,
                }
            )

            # 依存関係
            depends_on = task.get("depends_on", [])
            for dep in depends_on:
                dependencies_rows.append({"BeforeTask": dep, "AfterTask": task_name})

        self.loaded_dataframe.task_df = pd.DataFrame(task_rows)
        self.loaded_dataframe.dependencies_df = pd.DataFrame(dependencies_rows)

        # 2. employees_df
        employee_rows = []
        for emp in config["employee"]:
            employee_rows.append({"Employee": emp["name"], "Rate": emp["rate"]})

        self.loaded_dataframe.employees_df = pd.DataFrame(employee_rows)

        # 3. skills_df
        skill_rows = []
        for skill in config["skill"]:
            skill_rows.append(
                {
                    "Employee": skill["employee"],
                    "Task": skill["task"],
                    "IsCapable": int(skill["is_capable"]),  # true/falseを1/0にする
                }
            )

        self.loaded_dataframe.skills_df = pd.DataFrame(skill_rows)

        return self.loaded_dataframe


def load_input_file():
    # インスタンス化
    # loader = CsvLoader()
    loader = YamlLoader()

    # データを読み込む
    loaded_dataframe = loader.load_input_file()
    # print(loaded_dataframe.skills_df)
    # sys.exit(0)

    # validation
    loaded_dataframe.validate()

    return loaded_dataframe
