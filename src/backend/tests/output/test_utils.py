import os
import sys
from datetime import datetime

import pytest
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getenv("PROJECT_ROOT_PATH"))
from src.backend.output.utils import generate_business_days, is_business_day


def convert_into_datetime(date_str):
    """
    文字列形式の日付をdatetimeオブジェクトに変換する関数。

    Args:
        date_str (str): 変換する日付の文字列（"YYYYMMDD"形式）。

    Returns:
        datetime: 変換されたdatetimeオブジェクト。
    """
    return datetime.strptime(date_str, "%Y%m%d")


test_cases = [
    ("20250505", False),  # 祝日
    ("20250506", False),  # 祝日
    ("20250507", True),  # 平日
    ("20250508", True),  # 平日
    ("20250509", True),  # 平日
    ("20250510", False),  # 土曜日
    ("20250511", False),  # 日曜日
]


@pytest.mark.parametrize(
    "project_start_date, expected",
    [(convert_into_datetime(date_str), expected) for date_str, expected in test_cases],
)
def test_add(project_start_date, expected):
    assert is_business_day(project_start_date) == expected


@pytest.mark.parametrize(
    "start_date, total_days, expected",
    [
        (
            convert_into_datetime("20250602"),
            3,
            ["2025-06-02", "2025-06-03", "2025-06-04"],
        ),
        (
            convert_into_datetime("20250501"),
            10,
            [
                "2025-05-01",
                "2025-05-02",
                "2025-05-07",
                "2025-05-08",
                "2025-05-09",
                "2025-05-12",
                "2025-05-13",
                "2025-05-14",
                "2025-05-15",
                "2025-05-16",
            ],
        ),
    ],
)
def test_generate_business_days(start_date, total_days, expected):
    assert generate_business_days(start_date, total_days) == expected
