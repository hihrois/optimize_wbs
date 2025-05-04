from datetime import datetime, timedelta

import jpholiday  # 日本の祝日ライブラリ


def is_business_day(date: datetime) -> bool:
    """
    指定された日付が営業日（平日かつ祝日でない日）かどうかを判定する。

    Args:
        date (datetime.datetime): 判定対象の日付。

    Returns:
        bool: 営業日の場合は True、それ以外（土日または祝日）の場合は False。
    """
    return date.weekday() < 5 and not jpholiday.is_holiday(date)


# 営業日のみを扱うための関数（祝日も除外）
def generate_business_days(start_date: datetime, total_days: int) -> list:
    """
    指定された開始日から数えて、営業日（平日かつ祝日でない日）のみを対象に、指定日数分の日付リストを生成する。

    Args:
        start_date (datetime.datetime): 営業日計算を開始する日付。
        total_days (int): 取得したい営業日数。

    Returns:
        list: 取得された営業日を "YYYY-MM-DD" 形式の文字列で格納したリスト。
    """
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
