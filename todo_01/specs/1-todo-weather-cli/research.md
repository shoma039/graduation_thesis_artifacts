# research: Todo 天気連携CLI（todo-weather-cli）

## 概要

このドキュメントは、`spec.md` の未解決点（NEEDS CLARIFICATION）を解消し、実装に向けた技術選定と理由付けをまとめたもの。

---

## 決定事項一覧

1. Date parsing
   - Decision: `dateparser`（Python package）を採用
   - Rationale: 日本語を含む自然言語表現の解析に対応しており、ローカル実行でAPIキー不要。広く使われているためドキュメントが豊富。
   - Alternatives considered: `parsedatetime`（英語寄り）、自前ルールベース（工数大）

2. Geocoding (都市名 → 緯度経度)
   - Decision: Nominatim（OpenStreetMap）の公開API を `geopy` 経由で利用する
   - Rationale: APIキー不要で地名解決が可能。利用制限に注意し、複数候補が返る場合はユーザー選択を行う。
   - Alternatives considered: 公開のジオコーディングAPI（APIキー必要なもの）

3. Weather forecast
   - Decision: Open-Meteo（https://api.open-meteo.com/）を利用
   - Rationale: APIキー不要で時間別/日別の降水確率・気温を取得可能。タイムゾーン処理や複数パラメータ取得が容易。
   - Alternatives considered: 他の無料サービス（精度/利用制限を比較）

4. Time zone determination
   - Decision: `timezonefinder` ライブラリ（緯度経度からタイムゾーン名を算出）を利用
   - Rationale: オフラインでタイムゾーン判定が可能。Open-Meteo の timezone 機能も併用して検証する。
   - Alternatives considered: 外部タイムゾーンAPI（多くはキーが必要）

5. CLI framework
   - Decision: `click` をコマンド定義の主軸とし、対話的入力には `prompt-toolkit` を併用（必要時）
   - Rationale: `click` は宣言的でテストしやすく、`prompt-toolkit` はリッチなインタラクションを提供するためユーザー体験向上に寄与する。
   - Alternatives considered: `argparse`（シンプルだが対話性が弱い）、`inquirer`（代替）

6. Storage / 永続化
   - Decision: 単一JSONファイル（ユーザー指定パス、デフォルトは `~/.todo_weather_cli/tasks.json`）
   - Rationale: 可搬性が高く実装が簡単。要件で選ばれた方式。同時更新を防ぐため `filelock` を用いた排他制御を行う。
   - Alternatives considered: SQLite（拡張性ありだが複雑度増）、TinyDB（JSONベースで便利だが依存増）

7. Concurrency / ファイルロック
   - Decision: `filelock` を利用してJSONの読み書き時にロックを行う

8. Candidate date selection algorithm
   - Decision: 期限期間内の日ごとに降水確率（primary）と気温（secondary）を評価し、降水確率が最も低い日を採用。複数日で並んだ場合は平均気温が高い日を優先。
   - Conflict resolution: 候補日は既存タスクの候補日と被らないように、選択した順に空き状況を確認して次善の候補を選ぶ。すべて不可なら最大3つの代替候補を提示。

---

## 実装上の注意点 / リスク

- Nominatim は利用規約で大規模自動アクセスを禁止している。商用や高頻度アクセスがある場合は独自インスタンスや別サービスを検討する必要がある。
- `dateparser` の日本語対応は万能ではない。複雑な日本語表現（「来月第2金曜の午後」等）についてはテストケースを用意し、必要であれば補助的なルールを追加する。
- Open-Meteo の降水確率フィールドは地域・時刻の粒度によって精度が変わる。候補選定では日単位の集約戦略（その日の最大または平均）を定義する必要がある。

---

## 実装候補スタック（requirements）

- Python >= 3.11
- Dependencies (pip):
  - `click`
  - `prompt-toolkit` (任意の対話用)
  - `requests`
  - `geopy`
  - `dateparser`
  - `timezonefinder`
  - `filelock`

---

## 実施タスク（短期）

1. 代表的な日本語日時のユニットテストを50件用意し、`dateparser` でのパース結果を検証する。
2. Open-Meteo を使って、指定都市の緯度経度で3日〜14日の降水確率と気温を取得して、アルゴリズムの挙動を確認する。
3. Nominatim で複数候補が返るケースのUI（選択プロンプト）を作成する。

---

## まとめ（Decision / Rationale / Alternatives）

- Decision: `dateparser` + `geopy(Nominatim)` + `Open-Meteo` + `timezonefinder`、CLIは`click`、Storageは単一JSON（`filelock`で保護）
- Rationale: 要件（APIキー不要、ローカルで軽量に動く、日本語入出力）を満たし、実装の複雑さを抑えられるため。
- Alternatives: 商用にスケールする場合はNominatimの代わりに有償ジオコーディング、データ量が増える場合はSQLite移行を想定。
