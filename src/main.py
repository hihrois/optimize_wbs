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
                          [(e, t) for e in employees for t in tasks], 
                          cat='Binary')

# 各タスクの開始時間 (実数変数)
start_times = pulp.LpVariable.dicts("start_time", tasks, lowBound=0, cat='Continuous')

# 最終的な終了時間 (メイクスパン)
makespan = pulp.LpVariable("makespan", lowBound=0, cat='Continuous')

# 4. 目的関数の定義 (最後のタスクが終了するまでの時間を最小化)
problem += makespan, "Minimize_Makespan"

# 5. 制約条件
# 各タスクは1人の従業員にのみ割り当てられる
for t in tasks:
    problem += pulp.lpSum([x[e, t] for e in employees]) == 1, f"Task_{t}_assignment"

# 従業員がスキルを持たないタスクには割り当てられない
for e in employees:
    for t in tasks:
        if employee_skills[e][t] == 0:
            problem += x[e, t] == 0, f"{e}_cannot_do_{t}"

# タスクの依存関係の制約 (BeforeTaskの終了時間 < AfterTaskの開始時間)
for before, after in dependencies:
    problem += start_times[after] >= start_times[before] + task_times[before], f"Dependency_{before}_before_{after}"

# 各タスクの終了時間はメイクスパン以下でなければならない
for t in tasks:
    problem += makespan >= start_times[t] + task_times[t], f"Makespan_constraint_{t}"

# 同じ従業員が同じ時間に複数のタスクを処理しないようにする制約
for e in employees:
  for t1 in tasks:
    for t2 in tasks:
      if t1 < t2:
        # t1 と t2 が同じ従業員に割り当てられている場合に、時間が重ならないようにする制約
        problem += start_times[t1] + task_times[t1] <= start_times[t2] + (2 - x[e, t1] - x[e, t2]) * 9999, f"Overlap_{e}_{t1}_{t2}_1"
      elif t1 > t2:
        problem += start_times[t2] + task_times[t2] <= start_times[t1] + (2 - x[e, t1] - x[e, t2]) * 9999, f"Overlap_{e}_{t1}_{t2}_1"


# 6. 問題の解決
problem.solve()

# 7. 結果の表示
task_assignments = []
print(f"Status: {pulp.LpStatus[problem.status]}")
for e in employees:
    for t in tasks:
        if x[e, t].value() == 1:
            task_assignments.append((e, t, start_times[t].value(), start_times[t].value() + task_times[t]))
            print(f"{e} is assigned to {t}. Start time: {start_times[t].value()}.")

# 最小化されたメイクスパン（最後のタスク終了時間）
print(f"Makespan (total time): {pulp.value(makespan)} hours")

# 8. ガントチャートの描画
def plot_gantt_chart(task_assignments, employees, tasks):
    fig, ax = plt.subplots(figsize=(10, 6))

    # 色を従業員ごとに設定
    colors = plt.cm.get_cmap('tab20', len(employees))
    employee_colors = {employee: colors(i) for i, employee in enumerate(employees)}

    # タスクごとにプロット
    for assignment in sorted(task_assignments, key=lambda x:x[1], reverse=True):
        employee, task, start, end = assignment
        ax.barh(task, end - start, left=start, color=employee_colors[employee], edgecolor='black')
    
    # 凡例を設定
    patches = [mpatches.Patch(color=employee_colors[employee], label=employee) for employee in employees]
    ax.legend(handles=patches, title="Employees")

    # 軸ラベルとタイトルの設定
    ax.set_xlabel('Day')
    ax.set_ylabel('Tasks')
    ax.set_title('Gantt Chart for Task Assignments')

    # グリッドとフォーマットの設定
    ax.grid(True)
    plt.tight_layout()
    plt.show()

# ガントチャートを表示
plot_gantt_chart(task_assignments, employees, tasks)
