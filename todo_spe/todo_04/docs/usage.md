# Usage — Todo CLI

インストール（Windows / PowerShell）:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

DB のマイグレーション:

```powershell
python -m src.storage.migrate
```

基本コマンド例 (日本語出力):

```powershell
python -m src.cli add "図書館で本を返す" --deadline "明日" --location "東京" --priority 高
python -m src.cli list
python -m src.cli show 1
python -m src.cli update 1 --deadline "来週" --location "渋谷"
python -m src.cli complete 1
python -m src.cli calendar --month 2025-12
```

自動化（JSON 出力）:

```powershell
python -m src.cli add "資料作成" --deadline "来週" --location "横浜" --json
```

パッケージ化後は `todo` エントリポイントが利用可能になります:

```powershell
todo add "テスト" --deadline 明日 --location 東京
```
