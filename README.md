# optimize_wbs 
## What is optimize_wbs?

### input
- タスク（タスク名、工数）
- タスクの依存関係（先行タスク、後続タスク）
- 従業員（従業員名、稼働率）
- 従業員のタスク遂行可否（従業員名、タスク名、タスク遂行可否）

### output
全体の工数が最小になるWBS（問題のサイズに応じて、最適解か近似解かは切り替わる。どちらの解かをユーザは知ることができる）
![WBS](https://github.com/user-attachments/assets/b0f94470-ee07-4336-8bdf-34697f4a2cf7)

## How to use
### 入力方法
#### tasks.csv
タスクに関わる情報を入力するファイル。

- Task
  - タスク名を入力する。WBSの１行に相当するイメージ。（例）xxx.sql実装
- ProcessingTime
  - タスクにかかる工数（h）。（例）3

#### dependencies.csv
タスク同士の依存関係を入力するファイル。１行に入力できるのはBeforeTask、AfterTaskそれぞれ１つまでであるため、1対多や多対多の場合は、１対１に書き下す必要がある。なお、A→B→Cのような依存関係を表現したい際は、A→Cの依存関係は自動で考慮されるため、入力する必要はなく、A→B、B→Cのみを入力すれば十分である。

- BeforeTask
  - AfterTaskが始まる際、既に完了している必要があるタスク。（例）xxx.sql実装
- AfterTask
  - BeforeTaskが完了しないと始めることができないファイル。（例）xxx.sqlレビュー

#### employees.csv
PJTメンバーに関する情報を記載するファイル。
- Employee
  - メンバー名を入力する。（例）Nakahara
- Rate
  - メンバーの稼働率を入力する。デフォルトでは１人１日あたりの工数を8時間としているため、例えば稼働率を0.8と入力すると、１日6.4時間を工数として当てられる扱いとなる。（例）0.8

#### skills.csv
PJTメンバーとタスクの関係を記載するファイル。「担当することができない」タスクのみを記載する。

- Employee
  - 従業員名。employees.csvと紐づけられるよう、同名を入力する。（例）Nakahara
- Task
  - タスク名。Employeeが「担当できない
  タスク名を入力する。tasks.csvと紐づけられるよう、同名を入力する。（例）バク転