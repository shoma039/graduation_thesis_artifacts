# todo_weather_scheduler

対話的な CLI Todo アプリ。期限内の天気（降水確率・気温）を考慮して候補日を自動提案します。日本語出力を優先します。

Quickstart:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.cli.main todo add --title "買い物" --location "札幌" --due "明日"
```
