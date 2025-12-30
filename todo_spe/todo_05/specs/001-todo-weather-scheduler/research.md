# research.md

## Unknowns / Research Tasks

1. 日付自然言語解析（日本語）の最適ライブラリ：`dateparser` を採用する。  
   - Task: 評価 - `dateparser` の日本語対応とタイムゾーン解釈の挙動を確認（テストケース: 「明日」「来週の月曜」「来月10日」）。

2. ジオコーディング（都市名→緯度経度）：APIキー不要で信頼性の高いサービス  
   - Decision: OpenStreetMap の Nominatim を想定（利用規約とレート制限に注意）。  
   - Task: 実運用ではキャッシュ（都市名→座標）を入れてレートを抑える。

3. 天気データ（APIキー不要）：短期の降水確率と気温を取得  
   - Decision: Open-Meteo を採用（無料・APIキー不要・地点ベースの予報を取得可能）。  
   - Task: 取得する変数（降水確率、最高/最低気温、平均気温）と時間解像度（日次/時間毎）を確定。

4. タイムゾーン処理：場所のタイムゾーンに基づいて日付境界を解釈  
   - Decision: `zoneinfo`（標準ライブラリ）と `pytz` 補助。ジオコーディングで返るタイムゾーン名を利用してUTC→ローカル変換を行う。

5. 候補日スケジューリングアルゴリズムの詳細  
   - Decision: 仕様に記載の通り、降水確率が低い日を日ごとに評価し、重複は先に登録されたタスクを優先して割り当てる。再配置上限は3回。代替候補は最大3つ提示。

## Decisions (まとめ)

- Date parsing: `dateparser`（日本語対応） — Rationale: 日本語自然文解析の実績があり、タイムゾーン指定をサポートする。  
- Geocoding: Nominatim (OpenStreetMap) — Rationale: APIキー不要で都市名→緯度経度が取得可能。注意: レート制限あり、利用規約順守。  
- Weather: Open-Meteo — Rationale: APIキー不要で地点ベースの短期予報（降水確率・気温）を取得できる。  
- Storage: SQLite — Rationale: 小規模CLIアプリで導入負荷が低く、トランザクションや検索が容易。

## Alternatives Considered

- 日付解析: `parsedatetime` や `natty`（Java）を検討。`parsedatetime` は日本語サポートが弱く、natty はJava依存のため不採用。
- ジオコーディング: Google Geocoding（高精度だがAPIキーと費用が必要）→今回は非採用。
- 天気API: Meteostat, WeatherAPI 等も検討したが、APIキー不要かつ地点ベースで使いやすい点で Open-Meteo を選定。

## Next Steps (for Phase 1)

1. `data-model.md` を作成して永続化スキーマを確定する。  
2. CLIコマンド一覧（`contracts/`）を作り、ユーザーインターフェースを定義する。  
3. `quickstart.md` を作成して開発者がローカルで動かせる手順を用意する。
