# Todo CLI アプリ

日本語で対話的に操作できるCLI Todoアプリです。主な機能:

- タスクの登録（ID, タイトル, 完了有無, 優先度(1-3), 場所, 期限）
- 一覧、詳細、更新、削除
- 日付は「明日」「来週の月曜」など自然文で入力可能（日本語対応）
- 登録した場所から自動で緯度/経度とタイムゾーンを取得
- Open-Meteo（APIキー不要）で降水確率・気温を取得し、期限内で最適な候補日を自動選定
- 候補日は他タスクと被らないように調整。最適日がなければ代替日を提案
- カレンダービュー（月選択可）で日付順表示

依存パッケージのインストールと実行方法:

```powershell
python -m pip install -r requirements.txt
python todo_cli.py
```

注意:
- 外部APIはNominatim（ジオコーディング）とOpen-Meteo（天気・タイムゾーン）を使用します。どちらもAPIキー不要です。
- タイムゾーンや日付処理は場所のタイムゾーンに合わせて処理します。

## 仮想環境での実行方法（Windows PowerShell）

開発・実行は仮想環境を使うことを推奨します。以下は PowerShell（Windows）での手順です。

1. Python（3.8+ 推奨）がインストールされていることを確認します。

2. プロジェクトルート（この `README.md` があるフォルダ）で仮想環境を作成:

```powershell
python -m venv .venv
```

3. 仮想環境をアクティベート:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. 依存パッケージをインストール:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. CLI を起動:

```powershell
python todo_cli.py
```

6. 終了・仮想環境の無効化:

```powershell
deactivate
```

補足:
- PowerShell の実行ポリシーにより `.\ .venv\Scripts\Activate.ps1` 実行が制限される場合は、管理者権限で `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` を一時的に実行してください（社内ポリシーに従ってください）。
- 代替として Git Bash や Windows Terminal の PowerShell で同じ手順を実行できます。
