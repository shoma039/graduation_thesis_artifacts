# Todo リスト（天気連動スケジューラ）

CLI ベースの Todo プロトタイプ（天気連動候補日提案）です。開発中の機能や使い方は `docs/usage.md` にまとめています。

主な場所:

- 仕様・タスク: `specs/001-todo-weather-scheduler/`
- クイックスタートと使い方: `docs/usage.md`

セットアップ（Windows PowerShell）:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

開発者向け: テストや CI は `pytest` と GitHub Actions を想定しています。詳細は `docs/usage.md` を参照してください。
