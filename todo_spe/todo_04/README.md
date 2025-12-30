# todo-cli-weather

軽量な CLI ベースの Todo アプリケーション（天気連動スケジューリング）です。

主な機能
- 自然言語（日付）でのタスク登録（例: 「明日」「来週の月曜」）
- 地名をジオコーディングして天気予報を取得し、期限内で降水確率が低い最適な候補日を提案
- タスクの一覧・詳細・更新・完了（完了で削除）
- 月単位のカレンダー表示（候補日をハイライト）

注意: 本プロジェクトはローカル実行向けです。外部 API（Nominatim, Open-Meteo）を利用するためネットワーク接続が必要です。

セットアップと実行（Windows PowerShell の例）:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# DB マイグレーション
python -m src.storage.migrate

# タスクの追加例
python -m src.cli add "図書館で本を返す" --deadline "明日" --location "東京" --priority 中

# タスク一覧
python -m src.cli list

# カレンダー表示
python -m src.cli calendar --month 2025-12
```

詳細は `specs/001-todo-cli-weather/quickstart.md` を参照してください。
