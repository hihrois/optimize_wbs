import os
import sys
from abc import ABC, abstractmethod

import pandas as pd
import yaml
from dotenv import load_dotenv

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))

from src.backend.config.load_config import load_config
from src.backend.load.loaded_dataframe import LoadedDataframe


class AbstractInputLoad(ABC):
    """
    入力データの読み込みを抽象化した基底クラス。
    サブクラスで load_input_file メソッドを実装する必要がある。
    """

    def __init__(self):
        """
        環境変数や設定ファイルを読み込み、プロジェクトのパスや設定情報を初期化する。
        """
        load_dotenv()
        self.project_root_path = os.getenv("PROJECT_ROOT_PATH")
        self.config = load_config()["load"]
        self.input_folder_path = self.config["input_folder_path"]
        self.config_input = None

        self.loaded_dataframe = LoadedDataframe(
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )

    @abstractmethod
    def load_input_file(self, path: str) -> LoadedDataframe:
        """
        入力ファイルを読み込み、LoadedDataframe に格納する。

        Args:
            path (str): 入力ファイルのパス

        Returns:
            LoadedDataframe: 読み込まれたデータフレームのセット
        """
        pass

    def validate(self) -> None:
        """
        読み込まれたデータの整合性を検証する。
        """
        self.loaded_dataframe.validate()


class CsvLoad(AbstractInputLoad):
    """
    CSVファイルを読み込むためのローダークラス。
    """

    def load_input_file(self) -> LoadedDataframe:
        """
        複数のCSVファイル（tasks, employees, skills, dependencies）を読み込み、
        LoadedDataframe に格納して返す。

        Returns:
            LoadedDataframe: 読み込まれたデータフレームのセット
        """
        self.loaded_dataframe.task_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "tasks.csv"
        )
        self.loaded_dataframe.employees_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "employees.csv"
        )
        self.loaded_dataframe.skills_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "skills.csv"
        )
        self.loaded_dataframe.dependencies_df = pd.read_csv(
            self.project_root_path + self.input_folder_path + "dependencies.csv"
        )

        print(self.loaded_dataframe)
        return self.loaded_dataframe


class YamlLoad(AbstractInputLoad):
    """
    YAMLファイルを読み込むためのローダークラス。
    """

    def load_input_file(self) -> LoadedDataframe:
        """
        YAMLファイル（input.yml）を読み込み、各構成要素（tasks, employees, skills, dependencies）
        をデータフレームに変換して LoadedDataframe に格納する。

        Returns:
            LoadedDataframe: 読み込まれたデータフレームのセット
        """
        root_path = self.project_root_path + self.input_folder_path + "input.yml"
        with open(root_path, "r") as f:
            self.config_input = yaml.safe_load(f)

        # 1. tasks_df
        task_rows = []
        dependencies_rows = []

        for task in self.config_input["task"]:
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

            depends_on = task.get("depends_on", [])
            for dep in depends_on:
                dependencies_rows.append({"BeforeTask": dep, "AfterTask": task_name})

        self.loaded_dataframe.task_df = pd.DataFrame(task_rows)
        self.loaded_dataframe.dependencies_df = pd.DataFrame(dependencies_rows)

        # 2. employees_df
        employee_rows = []
        for emp in self.config_input["employee"]:
            employee_rows.append({"Employee": emp["name"], "Rate": emp["rate"]})

        self.loaded_dataframe.employees_df = pd.DataFrame(employee_rows)

        # 3. skills_df
        skill_rows = []
        for skill in self.config_input["skill"]:
            skill_rows.append(
                {
                    "Employee": skill["employee"],
                    "Task": skill["task"],
                    "IsCapable": int(skill["is_capable"]),
                }
            )

        self.loaded_dataframe.skills_df = pd.DataFrame(skill_rows)

        return self.loaded_dataframe


def load_input_file() -> AbstractInputLoad:
    """
    デフォルトで YamlLoad を使用して入力データを読み込み、ローダーインスタンスを返す。

    Returns:
        AbstractInputLoad: データ読み込みを行ったローダーのインスタンス
    """
    loader = YamlLoad()
    loader.load_input_file()
    return loader
