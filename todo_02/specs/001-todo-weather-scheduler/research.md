# research.md

Phase 0: 技術的決定と根拠（`NEEDS CLARIFICATION` を全て解消）

## 決定 1: 言語とランタイム
- Decision: Python 3.11 を使用する（ただし 3.10 でも動作するよう互換性を保つ）。
- Rationale: ユーザー要求で Python 指定があり、豊富な日時・HTTP・SQLite サポートとエコシステム（`dateparser`, `requests` など）があるため。3.11 の `zoneinfo` 利用や最新標準に合う。
- Alternatives considered: Go（単一バイナリで配布しやすい）、Rust（高速・安全）があるが、開発速度・日本語ライブラリ対応を優先して Python を選択。

## 決定 2: 日付自然言語パーサ
- Decision: `dateparser` を採用（日本語入力サポートあり）。
- Rationale: 日本語の相対日付（"明日", "来週の月曜" 等）を解釈できる実績がある。ローカルで処理できるため外部依存が少ない。
- Alternatives considered: `parsedatetime`（日本語サポートが弱い）、独自のパーサ（開発負荷が高い）。

## 決定 3: ジオコーディングと天気 API（API キー不要）
- Decision: Open-Meteo のジオコーディング API と Open-Meteo 気象 API を使用する（API キー不要）。
- Rationale: Open-Meteo は都市名検索のジオコーディングエンドポイントと、降水確率・気温の予報を API キー無しで提供する。要件の「APIキー登録不要」を満たす。
- Alternatives considered: Nominatim（OSM）ジオコーディング（レート制限と利用規約注意）、Met.no（YR）など。他は API 連携の複雑さやライセンス/利用制限で劣る。

## 決定 4: タイムゾーン処理
- Decision: 標準ライブラリの `zoneinfo`（Python 3.9+）を用い、必要に応じて `dateutil` を補助的に使用する。
- Rationale: タイムゾーン情報は location の緯度経度から決定し、`zoneinfo` と組み合わせて日時変換を正確にする。
- Alternatives considered: `pytz`（レガシー）、`pendulum`（高機能だが依存が増える）。

## 決定 5: ストレージ
- Decision: SQLite を主ストレージとして採用。人間が読めるバックアップ用に JSON エクスポートを実装。
- Rationale: ローカル DB で ACID があるためデータ整合性が保ちやすい。外部サービス不要で配布が簡易。
- Alternatives considered: 単純な JSON ファイルのみ（競合・整合性問題の懸念）、TinyDB（柔軟だが SQLite の信頼性に劣る）。

## 決定 6: CLI 実装ライブラリ
- Decision: `typer` を推奨（開発効率のため）。ただし最小実装では標準 `argparse` でも可。
- Rationale: Typer は Click ベースで宣言的なコマンド定義が可能で、ヘルプ表示や引数パースが簡潔。ユーザーフレンドリな CLI を短期間で実装できる。
- Alternatives considered: `argparse`（標準だがボイラープレート多め）、`click`（Typer の代替）。

## 決定 7: 候補日選定ロジック
- Decision: 期限内の各日の降水確率を取得し、最も低い日のうち最も早い日を候補日とする。候補日が既存タスクと重複する場合は「先着順（作成日時が早いもの優先）」で保持し、後から作られたタスクは次点の良い空き日に割り当てる。
- Rationale: 単純で予測可能なルール。ユーザーの期待に合いやすい（早く登録した人を優先）。自動化により手間が少ない。
- Alternatives considered: 優先度ベース（高優先を優先）、手動介入（通知してユーザーに選ばせる）。優先度ベースは公平性の判断が必要、手動は自動化メリットが下がる。

## 決定 8: 代替日提案ポリシー
- Decision: 期限内に降水確率の低い日が存在しない場合、期限後の最初の空き（候補日重複を回避した日）を "予備日" として提案する。提案にはその日の降水確率と最低/最高気温を表示する。
- Rationale: ユーザーが代替日を即時判断できるようにするため。

## 決定 9: エラーとフォールバック
- Decision: 外部 API が利用不可（タイムアウト/エラー）な場合はユーザーに明確な日本語メッセージを表示し、候補日算出を一時停止してローカルで登録のみ行う（ユーザーに再試行オプションを提示）。
- Rationale: API障害時に誤った候補日を自動で決めるより、ユーザーに状況を知らせる方が安全。
- Alternatives considered: 既存の過去の天気傾向を用いる（精度低下のため初期リリースでは採用しない）。

---

すべての `NEEDS CLARIFICATION` はこの `research.md` で解消されました。
