# Quickstart — todo-weather-cli

短時間で試すための最小手順を示します（Windows / PowerShell 想定）。

1. Python 仮想環境の作成（推奨）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 依存関係のインストール

```powershell
pip install --upgrade pip
pip install click requests geopy dateparser timezonefinder filelock prompt-toolkit
```

3. 実行（開発用）

```powershell
python -m todo_weather_cli.cli    # まだ未作成のエントリポイント例
```

4. サンプルコマンド例

```powershell
# タスク追加（自然言語日付）
todo add --title "公園清掃" --due "明日" --priority 高 --location "東京"

# タスク一覧
todo list

# カレンダー表示（来月）
todo calendar 2026-01
```

5. 注意

- `geopy` の Nominatim 利用時は過度なリクエストを避けること。キャッシュとユーザー選択UIを実装してください。
- Open-Meteo の仕様に合わせて日単位の集計ロジックを実装する必要があります。
