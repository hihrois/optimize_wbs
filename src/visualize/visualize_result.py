import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from get_config import get_config
from datetime import datetime, timedelta
import jpholiday  # 日本の祝日ライブラリ

# 営業日のみを扱うための関数（祝日も除外）
def generate_business_days(start_date, total_days):
    business_days = []
    current_date = start_date
    days_added = 0

    # 営業日のみを取得するループ
    while days_added < total_days:
        # 平日（月〜金）かつ日本の祝日でない日をチェック
        if current_date.weekday() < 5 and not jpholiday.is_holiday(current_date):
            business_days.append(current_date.strftime('%Y-%m-%d'))
            days_added += 1
        current_date += timedelta(days=1)

    return business_days

# 8. ガントチャートの描画
def plot_gantt_chart(result):
    problem, task_assignments, employees, tasks, dependencies, start_times_dict = result.values()
    
    config = get_config()
    regular_time = config.getfloat('employee', 'regular_time')
    project_start_date = config.get('date', 'project_start_date')  # 'yyyymmdd'形式の日付文字列

    # project_start_dateをdatetime型に変換
    project_start_date = datetime.strptime(project_start_date, '%Y%m%d')

    fig, ax = plt.subplots(figsize=(10, 6))

    # 色を従業員ごとに設定
    colors = plt.cm.get_cmap('tab20', len(employees))
    employee_colors = {employee: colors(i) for i, employee in enumerate(employees)}

    task_pos = {}  # タスクの位置を保存しておく
    ypos = 0  # 初期の縦軸の位置

    # タスクごとにプロット
    for assignment in sorted(task_assignments, key=lambda x: x[1], reverse=True):
        employee, task, start, end = assignment
        ax.barh(task, end - start, left=start, color=employee_colors[employee], edgecolor='black')
        task_pos[task] = ypos  # 各タスクのy座標位置を保存
        ypos += 1

    # 凡例を設定
    patches = [mpatches.Patch(color=employee_colors[employee], label=employee) for employee in employees]
    ax.legend(handles=patches, title="Employees")

    # 依存関係に基づいて矢印を描画
    for before, after in dependencies:
        before_start, before_end = start_times_dict[before]
        after_start, _ = start_times_dict[after]
        ax.annotate('',
                    xy=(after_start, task_pos[after]),  # 矢印の先
                    xytext=(before_end, task_pos[before]),  # 矢印の元
                    arrowprops=dict(arrowstyle="->", color='black'))

    # X軸の目盛りを「8時間=1日」として調整し、日付を営業日のみをproject_start_dateに基づいて設定
    max_time = max([end for _, _, _, end in task_assignments])  # 最大時間を取得
    total_days = max_time // regular_time + 1  # 日数を計算

    # 営業日のみのラベルを作成（祝日も除外）
    date_labels = generate_business_days(project_start_date, int(total_days))

    ax.set_xticks([i * regular_time for i in range(len(date_labels))])  # 営業日単位の目盛りを設定
    ax.set_xticklabels(date_labels)  # 日付ラベルに変換
    ax.set_xticklabels(date_labels, rotation=90)  # 日付ラベルを縦に回転

    # 軸ラベルとタイトルの設定
    ax.set_xlabel('Date')
    ax.set_ylabel('Tasks')
    ax.set_title('Gantt Chart for Task Assignments with Dependencies')

    # グリッドとフォーマットの設定
    ax.grid(True)
    plt.tight_layout()
    plt.show()
