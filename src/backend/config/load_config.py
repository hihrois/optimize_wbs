import os

import yaml

current_file_path = os.path.abspath(__file__)  # 自分の.pyファイルの絶対パス
base_dir = os.path.dirname(current_file_path)


def load_config() -> dict:
    root_path = base_dir + "/config.yml"
    with open(root_path, "r") as f:
        config = yaml.safe_load(f)
    return config
