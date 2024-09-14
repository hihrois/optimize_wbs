import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from get_config import get_config

# 8. ガントチャートの描画
def plot_gantt_chart(result):
  problem, task_assignments, employees, tasks, dependencies, start_times_dict = result.values()
  
  config = get_config()
  regular_time = config.getfloat('employee', 'regular_time')

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


  print(start_times_dict)
  
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
  days = max_time / regular_time  # 1日を8目盛りにする
  ax.set_xticks([i * regular_time for i in range(int(days) + 2)])  # 日単位の目盛りを設定
  ax.set_xticklabels([f'Day {i+1}' for i in range(int(days) + 2)])  # ラベルを「Day 1」などに設定

  # 軸ラベルとタイトルの設定
  ax.set_xlabel('Days')
  ax.set_ylabel('Tasks')
  ax.set_title('Gantt Chart for Task Assignments with Dependencies')

  # グリッドとフォーマットの設定
  ax.grid(True)
  plt.tight_layout()
  plt.show()