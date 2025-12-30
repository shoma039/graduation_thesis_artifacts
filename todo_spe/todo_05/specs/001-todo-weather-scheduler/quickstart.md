# Quickstart — Todo リスト（天気連動スケジューラ）

前提: Python 3.11 がインストールされていること。

1. 開発環境セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. ローカルでの簡易起動（プロトタイプ）

```powershell
# 開発用 CLI 実行サンプル
python -m src.cli.main add --title "買い物" --deadline "明日" --place "Tokyo"
python -m src.cli.main list
python -m src.cli.main calendar --month 2025-12
```

3. テスト実行

```powershell
pytest
```

4. 実装メモ

- 天気/ジオコーディングのAPIはモック可能に実装し、テスト時は固定データでテストを回すこと。
- タイムゾーンは `Location.timezone` を参照して、UTC↔ローカルの変換を行う。
