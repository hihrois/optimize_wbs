import os
from dotenv import load_dotenv
import pandas as pd
from dataclasses import dataclass
import sys

@dataclass
class LoadedDataframe:
    task_df: pd.DataFrame
    employees_df: pd.DataFrame
    skills_df: pd.DataFrame
    dependencies_df: pd.DataFrame

def load_input_file():
  # .envファイルの内容を読み込む
  load_dotenv()

  # .envファイルから環境変数を取得
  PROJECT_ROOT_PATH = os.getenv('PROJECT_ROOT_PATH')
  INPUT_FOLDER_PATH = os.getenv('INPUT_FOLDER_PATH')

  # CSVからデータを読み込む
  tasks_df = pd.read_csv(PROJECT_ROOT_PATH+INPUT_FOLDER_PATH+'tasks.csv')
  employees_df = pd.read_csv(PROJECT_ROOT_PATH+INPUT_FOLDER_PATH+'employees.csv')  # 稼働率列を含む
  skills_df = pd.read_csv(PROJECT_ROOT_PATH+INPUT_FOLDER_PATH+'skills.csv')  # スキルがない情報のみ
  dependencies_df = pd.read_csv(PROJECT_ROOT_PATH+INPUT_FOLDER_PATH+'dependencies.csv')
  
  return LoadedDataframe(tasks_df, employees_df, skills_df, dependencies_df)