# Quickstart

## 前提
- Python 3.10+ がインストールされていること
- ネットワークアクセスがあること（天気/ジオコーディング API へアクセス）

## インストール（プロジェクトルートで実行）
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` に含める想定パッケージ:
- requests
- dateparser
- typer
- python-dateutil

## 使い方の例
- タスク追加（自然言語期限）:
```powershell
python -m src.cli todo add --title "買い物" --location "札幌" --due "明日" --priority high
```
- タスク一覧:
```powershell
python -m src.cli todo list
```
- タスク詳細:
```powershell
python -m src.cli todo show 1
```
- カレンダー表示:
```powershell
python -m src.cli todo calendar --month 2025-12
```

## 開発・テスト
- テスト実行:
```powershell
pytest -q
```

## 注意事項
- 外部 API は API キー不要の公開 API を使用します。ネットワーク接続が不可の場合、候補日算出は保留されます。

