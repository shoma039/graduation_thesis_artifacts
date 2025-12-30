# Todo CLI アプリ

日本語の対話式 CLI Todo アプリです。機能:

- タスクの登録・一覧・詳細表示・更新・削除
- タスク属性: ID, タイトル, 完了フラグ, 優先度(1-3), 場所(都市→自動で緯度経度・タイムゾーン取得), 期限
- 日付は日本語の自然言語入力に対応（例：`明日`, `来週の月曜`）
- Open-Meteo を使って期限内の降水確率と気温を取得し、降水確率が低い最適日を候補日として登録
- カレンダー表示（年月選択）

API キー不要の外部サービスを使用しています（Nominatim, Open-Meteo）。

セットアップ:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python todo.py
```

注意:
- Nominatim の利用規約に従ってください（大量アクセス禁止）。
- Windows の Python で実行することを想定しています。

---
ファイル:
- `todo.py` : メイン CLI
- `models.py`, `storage.py`, `geocode.py`, `weather.py`, `utils.py` : 補助モジュール
