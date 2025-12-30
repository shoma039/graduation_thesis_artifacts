# Quickstart — Todo CLI (天気連動)

前提: Python 3.11 がインストールされていること。

セットアップ（推奨: 仮想環境）:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# DB マイグレーション
python -m src.storage.migrate

# パッケージ化して `todo` エントリポイントを使う場合
```
python -m build
pip install dist/todo-cli-weather-0.0.0-py3-none-any.whl
todo --help
```
```

使い方の例:

- タスク登録:
```powershell
python -m src.cli add "図書館で本を返す" --deadline "明日" --location "東京" --priority 高
```

- タスク一覧 (当月):
```powershell
python -m src.cli list
```

- カレンダー表示:
```powershell
python -m src.cli calendar --month 2025-12
```

エラー発生時: 画面に日本語で原因を表示します。自動化用途には `--json` を付けると機械判定用 JSON を返します。
