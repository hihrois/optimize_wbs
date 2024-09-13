import pandas as pd
import pulp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# CSVからデータを読み込む
tasks_df = pd.read_csv('tasks.csv')
employees_df = pd.read_csv('employees.csv')
skills_df = pd.read_csv('skills.csv')  # スキルがない情報のみ
dependencies_df = pd.read_csv('dependencies.csv')

# タスクリストとその処理時間
tasks = tasks_df['Task'].tolist()
task_times = dict(zip(tasks_df['Task'], tasks_df['ProcessingTime']))

# 従業員リスト
employees = employees_df['Employee'].tolist()

# スケジュールの日数を設定
days = 5  # スケジュールは5日間にわたると仮定

# 各従業員の1日あたりの上限作業時間
# (例: Employee 1は1日8時間, Employee 2は1日7時間)
employee_max_hours_per_day = {
    'Employee1': 6,
    'Employee2': 7,
    'Employee3': 3,
    'Employee4': 1,
}

# 全従業員は基本的に全タスクが可能で、スキルがない場合だけ制約を加える
employee_skills = {e: {t: 1 for t in tasks} for e in employees}  # 全員が全タスク可能
for _, row in skills_df.iterrows():  # スキルがない場合のみ上書き
    employee_skills[row['Employee']][row['Task']] = 0  # スキルがない場合

# タスクの依存関係をCSVからロード
dependencies = list(zip(dependencies_df['BeforeTask'], dependencies_df['AfterTask']))

# 2. 問題の定義
problem = pulp.LpProblem("Task Assignment Problem with Makespan Minimization", pulp.LpMinimize)

# 3. 変数の定義
# バイナリ変数: 従業員がタスクに割り当てられるかどうか
x = pulp.LpVariable.dicts("assignment", 
                          [(e, t, d) for e in employees for t in tasks for d in range(days)], 
                          cat='Binary')

# 各タスクの開始時間 (実数変数)
start_times = pulp.LpVariable.dicts("start_time", [(t, d) for t in tasks for d in range(days)], lowBound=0, cat='Continuous')

# 最終的な終了時間 (メイクスパン)
makespan = pulp.LpVariable("makespan", lowBound=0, cat='Continuous')

# 4. 目的関数の定義 (最後のタスクが終了するまでの時間を最小化)
problem += makespan, "Minimize_Makespan"

# 5. 制約条件
# 各タスクは1人の従業員に割り当てられ、1つのタスクは1人しか担当しない
for t in tasks:
    problem += pulp.lpSum([x[e, t, d] for e in employees for d in range(days)]) == 1, f"Task_{t}_assignment"

# 従業員がスキルを持たないタスクには割り当てられない
for e in employees:
    for t in tasks:
        if employee_skills[e][t] == 0:
            for d in range(days):
                problem += x[e, t, d] == 0, f"{e}_cannot_do_{t}_on_day_{d}"

# タスクの依存関係の制約 (BeforeTaskの終了時間 < AfterTaskの開始時間)
for before, after in dependencies:
    for d in range(days):
        problem += start_times[after, d] >= start_times[before, d] + task_times[before], f"Dependency_{before}_before_{after}_day_{d}"

# 各従業員の1日あたりの作業時間の制約
for e in employees:
    for d in range(days):
        problem += pulp.lpSum([x[e, t, d] * task_times[t] for t in tasks]) <= employee_max_hours_per_day[e], f"Max_hours_{e}_day_{d}"

# 各タスクの終了時間はメイクスパン以下でなければならない
for t in tasks:
    for d in range(days):
        problem += makespan >= start_times[t, d] + task_times[t], f"Makespan_constraint_{t}_day_{d}"

# 同じ従業員が同じ時間に複数のタスクを処理しないようにする制約
for e in employees:
    for t1 in tasks:
        for t2 in tasks:
            if t1 != t2:
                for d in range(days):
                    # t1 と t2 が同じ従業員に割り当てられている場合に、時間が重ならないようにする制約
                    problem += start_times[t1, d] + task_times[t1] <= start_times[t2, d] + (2 - x[e, t1, d] - x[e, t2, d]) * 9999, f"Overlap_{e}_{t1}_{t2}_day_{d}"

# 6. 問題の解決
problem.solve()

# 7. 結果の表示
task_assignments = []
print(f"Status: {pulp.LpStatus[problem.status]}")
for e in employees:
    for t in tasks:
        for d in range(days):
            if x[e, t, d].value() == 1:
                task_assignments.append((e, t, start_times[t, d].value(), start_times[t, d].value() + task_times[t], d))
                print(f"{e} is assigned to {t} on day {d+1}. Start time: {start_times[t, d].value()}.")

# 最小化されたメイクスパン（最後のタスク終了時間）
print(f"Makespan (total time): {pulp.value(makespan)} hours")

# 8. ガントチャートの描画
def plot_gantt_chart(task_assignments, employees, tasks, days):
    fig, ax = plt.subplots(figsize=(10, 6))

    # 色を従業員ごとに設定
    colors = plt.cm.get_cmap('tab20', len(employees))
    employee_colors = {employee: colors(i) for i, employee in enumerate(employees)}

    # タスクごとにプロット
    for assignment in sorted(task_assignments, key=lambda x:x[1], reverse=True):
        employee, task, start, end, day = assignment
        ax.barh(f"{task} (Day {day+1})", end - start, left=start, color=employee_colors[employee], edgecolor='black')
    
    # 凡例を設定
    patches = [mpatches.Patch(color=employee_colors[employee], label=employee) for employee in employees]
    ax.legend(handles=patches, title="Employees")

    # 軸ラベルとタイトルの設定
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Tasks (Day)')
    ax.set_title('Gantt Chart for Task Assignments Across Days')

    # グリッドとフォーマットの設定
    ax.grid(True)
    plt.tight_layout()
    plt.show()

# ガントチャートを表示
plot_gantt_chart(task_assignments, employees, tasks, days)
