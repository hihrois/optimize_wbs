import pandas as pd
import pulp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# CSVからデータを読み込む
tasks_df = pd.read_csv('../data/input/tasks.csv')
employees_df = pd.read_csv('../data/input/employees.csv')  # 稼働率列を含む
skills_df = pd.read_csv('../data/input/skills.csv')  # スキルがない情報のみ
dependencies_df = pd.read_csv('../data/input/dependencies.csv')

# タスクリストとその処理時間
tasks = tasks_df['Task'].tolist()
task_times = dict(zip(tasks_df['Task'], tasks_df['ProcessingTime']))

# 従業員リスト
employees = employees_df['Employee'].tolist()

# 従業員の稼働率を取得 (例: 稼働率は0.5〜1.0の範囲)
employee_rates = dict(zip(employees_df['Employee'], employees_df['Rate']))

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
for e in employees:
  for before, after in dependencies:
    problem += start_times[after] >= start_times[before] + x[e, before] * task_times[before] / employee_rates[e] , f"Dependency_{e}_{before}_before_{after}"


# 各タスクの終了時間はメイクスパン以下でなければならない
for e in employees:
  for t in tasks:
    problem += makespan >= start_times[t] +  x[e, t] * task_times[t] / employee_rates[e], f"Makespan_constraint_{e}_{t}"


# 同じ従業員が同じ時間に複数のタスクを処理しないようにする制約
for e in employees:
  for t1 in tasks:
    for t2 in tasks:
      if t1 < t2:
        problem += start_times[t1] + task_times[t1] / employee_rates[e] <= start_times[t2] + (2 - x[e, t1] - x[e, t2]) * 9999, f"Overlap_{e}_{t1}_{t2}_1"
      elif t1 > t2:
        problem += start_times[t2] + task_times[t2] / employee_rates[e] <= start_times[t1] + (2 - x[e, t1] - x[e, t2]) * 9999, f"Overlap_{e}_{t1}_{t2}_2"

# 6. 問題の解決
problem.solve()

# 7. 結果の表示
task_assignments = []
start_times_dict = {}
print(f"Status: {pulp.LpStatus[problem.status]}")
for e in employees:
    for t in tasks:
        if x[e, t].value() == 1:
            start = start_times[t].value()
            end = start + task_times[t] / employee_rates[e]
            task_assignments.append((e, t, start, end))
            start_times_dict[t] = (start, end)
            print(f"{e} is assigned to {t}. Start time: {start}.")

# 最小化されたメイクスパン（最後のタスク終了時間）
print(f"Makespan (total time): {pulp.value(makespan)} hours")

# 8. ガントチャートの描画
def plot_gantt_chart(task_assignments, employees, tasks, dependencies):
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

    # 軸ラベルとタイトルの設定
    ax.set_xlabel('Days')
    ax.set_ylabel('Tasks')
    ax.set_title('Gantt Chart for Task Assignments with Dependencies')

    # グリッドとフォーマットの設定
    ax.grid(True)
    plt.tight_layout()
    plt.show()


# 8. ガントチャートの描画
def plot_gantt_chart(task_assignments, employees, tasks, dependencies):
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

    # X軸の目盛りを「8目盛り＝1日」として調整
    max_time = max([end for _, _, _, end in task_assignments])  # 最大時間を取得
    days = max_time / 8  # 1日を8目盛りにする
    ax.set_xticks([i * 8 for i in range(int(days) + 2)])  # 日単位の目盛りを設定
    ax.set_xticklabels([f'Day {i+1}' for i in range(int(days) + 2)])  # ラベルを「Day 1」などに設定

    # 軸ラベルとタイトルの設定
    ax.set_xlabel('Days')
    ax.set_ylabel('Tasks')
    ax.set_title('Gantt Chart for Task Assignments with Dependencies')

    # グリッドとフォーマットの設定
    ax.grid(True)
    plt.tight_layout()
    plt.show()


# ガントチャートを表示
plot_gantt_chart(task_assignments, employees, tasks, dependencies)
