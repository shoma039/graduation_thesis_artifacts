# Todo CLI Scheduler

このリポジトリはローカルで動作する Python 製の CLI Todo アプリ（天気を考慮した候補日選定機能）です。

概要

- タスク登録・一覧・詳細・更新・削除を CLI で行えます。
- 自然言語の期限入力（例: 「明日」「来週の月曜」）をサポートします（日本語入力対応）。
- 都市名から自動で緯度・経度・タイムゾーンを取得し、Open-Meteo 系の API（APIキー不要）で天気予報を取得して最適候補日を選びます。

クイックスタート（PowerShell）

1. Python 3.11 を用意してください。
2. プロジェクトルートで仮想環境を作成し、有効化します。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

3. 依存関係をインストールします。

```powershell
pip install -r requirements.txt
```

4. CLI の基本コマンド例（プロジェクトルートから実行）

```powershell
# 対話的にタスクを追加（タイトル・期限（自然言語）・場所（都市名）を入力）
python -m src.todo_cli add

# タスク一覧を表示
python -m src.todo_cli list

# タスク詳細を表示（ID は一覧で確認）
python -m src.todo_cli show 1

# タスクを更新
python -m src.todo_cli update 1

# タスクを完了（削除）
python -m src.todo_cli complete 1

# タスクを削除
python -m src.todo_cli delete 1

# カレンダー表示（例: 2025-12）
python -m src.todo_cli calendar --month 2025-12
```

詳しい手順と追加の実例は `specs/1-todo-cli-scheduler/quickstart.md` を参照してください。

データ保存場所

- Windows: `%APPDATA%\\todo-cli-scheduler\\tasks.json`
- その他: `~/.local/share/todo-cli-scheduler/tasks.json`

注意

- 外部 API 呼び出しはネットワーク接続と利用規約の順守が必要です。
- 本ソフトはローカル単一ファイル（JSON）にデータを保存します。
