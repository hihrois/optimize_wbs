# optimize_wbs 
## What is optimize_wbs?

### input
- タスク（タスク名、工数、デッドライン）
- タスクの依存関係（先行タスク、後続タスク）
- 従業員（従業員名、稼働率）
- 従業員のタスク遂行可否（従業員名、タスク名、タスク遂行可否）

### output
- 全体の工数が最小になるWBS

なお、問題のサイズに応じて、最適解か近似解かは切り替わり、どちらの解かをユーザは知ることができる
![WBS](https://github.com/user-attachments/assets/b0f94470-ee07-4336-8bdf-34697f4a2cf7)

## How to use
### 1.必要な情報をcsv二入力する
#### tasks.csv
タスクに関わる情報を入力するファイル。

- Task
  - タスク名を入力する。WBSの１行に相当するイメージ。（例）xxx.sql実装
- ProcessingTime
  - タスクにかかる工数（h）。（例）3
- DeadLineDate（任意）
  - タスクの締め切り。yyyymmdd形式で入力する。（例）20240917
  - 計算量が増えてしまうため、なるべく入力しないことを推奨します。


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
PJTメンバーとタスクの関係を記載するファイル。  
あるTaskについて、
- 1件も入力がない場合は、全員担当可能とみなす。
- IsCapable=1となる設定が１行以上入力されている場合、IsCapable=1と入力されたEmployeeの中から担当者が決まる。
- IsCapable=0となる設定が１行以上入力されている場合、IsCapable=0と入力されたEmployee以外の中から担当者が決まる。
- IsCapable=0とIsCapable=1が混在する入力はエラー扱いとなる。

<入力項目>
- Employee
  - 従業員名。employees.csvと紐づけられるよう、同名を入力する。（例）Nakahara
- Task
  - タスク名。Employeeが「担当できないタスク名を入力する。tasks.csvと紐づけられるよう、同名を入力する。（例）バク転
- IsCapable
  - タスクを担当可能かを入力する。（例）1または0


### （任意）2.Dockerを起動する
プロジェクトのセットアップとDockerの利用方法

```bash
# Dockerイメージをビルド
docker build -t my-app .

# コンテナを起動
docker run -d -p 8501:8501 --name my-running-app my-app

# 実行中のコンテナに接続してbashシェルに入る
docker exec -it my-running-app /bin/bash


### 3.コマンド実行
計算を実行する関数を実行する

```bash
#プロジェクトルートディレクトリ上で
python src/backend/main.py
