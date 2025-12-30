# todo-weather-cli

軽量な CLI ベースの Todo 管理ツール（天気連携）

Quickstart
---------

基本コマンド例:

```
python -m src.cli.cli add --title "公園清掃" --due "明日" --priority 高 --location "東京"
python -m src.cli.cli list
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run CLI (examples):

```powershell
python -m src.cli.cli add --title "会議" --due "明日" --priority 中 --location "東京"
python -m src.cli.cli list
python -m src.cli.cli calendar 2026-01
```

Additional command reference: see `docs/commands.md`.
