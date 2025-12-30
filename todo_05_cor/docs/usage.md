# 使用方法（Quickstart）

このドキュメントはローカル開発環境でのクイックスタートと主要なコマンド例をまとめたものです。

前提: Python 3.11 がインストールされていること。

セットアップ（Windows PowerShell）:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

ローカルでの簡易起動（プロトタイプ）:

```powershell
# タスク追加（場所は曖昧検索が行われ候補を選べます）
python -m src.cli.main add "買い物" --deadline "明日" --place "Tokyo"

# タスク一覧
python -m src.cli.main list

# タスク詳細
python -m src.cli.main detail 1

# タスク更新
python -m src.cli.main update 1 --title "買い物(更新)" --place "Osaka"

# タスク完了（候補日も削除されます）
python -m src.cli.main complete 1

# 候補日の自動生成（単一タスク）
python -m src.cli.main schedule --task-id 1

# 候補日の確定（candidate_id は calendar で確認）
python -m src.cli.main confirm 7

# 月別カレンダー表示
python -m src.cli.main calendar --month 2025-12
```

テスト実行:

```powershell
pytest -q
```

実装メモ:

- 天気／ジオコーディングは API キー不要の Open-Meteo / Nominatim を利用します。
- テストでは外部 API をモックして再現性を確保してください。
- タイムゾーンは `locations.timezone` を使ってローカル日付を計算します。

詳しい仕様は `specs/001-todo-weather-scheduler/` にあります。
