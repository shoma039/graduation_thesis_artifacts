# Quickstart: Todo CLI Scheduler（日本語）

前提

- Python 3.11 がインストールされていること
- 推奨: 仮想環境を作成して有効化

インストール（PowerShell）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

実行例（プロジェクトルートで）

```powershell
# 対話的にタスクを追加
python -m src.todo_cli add

# タスク一覧
python -m src.todo_cli list

# タスク詳細（IDを指定）
python -m src.todo_cli show 1

# タスク更新
python -m src.todo_cli update 1

# タスク完了（削除）
python -m src.todo_cli complete 1

# カレンダー表示（例: 2025-12）
python -m src.todo_cli calendar --month 2025-12
```

メモ

- データはローカルの JSON ファイルに保存されます。Windows では `%APPDATA%\\todo-cli-scheduler\\tasks.json` を優先します。
- `add` 実行時に都市名から緯度・経度・タイムゾーンを取得します。取得に失敗した場合は再入力を促します。
