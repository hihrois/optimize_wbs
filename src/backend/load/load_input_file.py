import os
from dotenv import load_dotenv
import pandas as pd
from dataclasses import dataclass
import sys

sys.path.append(os.getenv("PROJECT_ROOT_PATH"))
from src.backend.config.load_config import load_config
import pandas as pd


@dataclass
class LoadedDataframe:
    # 現状任意の設定項目であっても、空のDFを返す
    task_df: pd.DataFrame
    employees_df: pd.DataFrame
    skills_df: pd.DataFrame
    dependencies_df: pd.DataFrame


def load_input_file():
    # .envファイルの内容を読み込む
    load_dotenv()

    # .envファイルから環境変数を取得
    project_root_path = os.getenv("PROJECT_ROOT_PATH")
    config = load_config()["load"]
    input_folder_path = config["input_folder_path"]

    # CSVからデータを読み込む
    tasks_df = pd.read_csv(project_root_path + input_folder_path + "tasks.csv")
    employees_df = pd.read_csv(
        project_root_path + input_folder_path + "employees.csv"
    )  # 稼働率列を含む
    skills_df = pd.read_csv(
        project_root_path + input_folder_path + "skills.csv"
    )  # スキルがない情報のみ
    dependencies_df = pd.read_csv(
        project_root_path + input_folder_path + "dependencies.csv"
    )

    return LoadedDataframe(tasks_df, employees_df, skills_df, dependencies_df)
