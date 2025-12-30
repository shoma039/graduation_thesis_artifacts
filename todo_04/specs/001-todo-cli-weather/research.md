# research.md — Todo CLI 天気連動 : 決定と代替案

## Decision: 実装言語と主要ライブラリ
- Decision: `Python 3.11` を採用。
- Rationale: CLI ツールに適合し、多数の関連ライブラリ（dateparser, requests, sqlite3）が利用可能で開発/配布が容易。
- Alternatives considered:
  - Node.js: CLI は可能だが、Python の日付/日時ライブラリや科学系エコシステムが有利。

## Decision: 日付パーサ
- Decision: `dateparser`（日本語サポートを含む）を採用。
- Rationale: 日本語表現（「明日」「来週の月曜」等）に対応する実績があり、設定で基準日や言語を指定可能。
- Alternatives:
  - `parsedatetime`（英語に強いが日本語サポートは弱い）

## Decision: ジオコーディング（都市名→緯度経度）
- Decision: Nominatim (OpenStreetMap) を一次候補とし、`geopy` を薄いラッパーとして使用する。
- Rationale: Nominatim は API キー不要で精度は都市レベルで十分。`geopy` は利用を簡易化する。
- Alternatives:
  - Google Geocoding（APIキー必要、商用制約あり）
  - Other paid services（外部キー必要）

## Decision: 天気 API
- Decision: Open-Meteo を採用（API キー不要、降水確率・気温を返す）。
- Rationale: API キー登録不要で、グローバルに利用可能。短期予報で降水確率を取得可能。
- Alternatives:
  - Meteostat / MET Norway 等（用途により検討）。

## Decision: 永続化
- Decision: `SQLite`（組み込み sqlite3）を採用。スキーマでタスク/場所/候補日を管理。
- Rationale: 依存が少なくローカルで安定。将来的に移行しやすい。

## Decision: CLI 表示
- Decision: `rich` を利用してテーブル/カレンダー表示を行う。
- Rationale: 見た目が良く、カレンダーや色付けが容易。

## その他運用ルール
- タイムゾーンはジオコーディング結果の `timezone` を優先して使用する。Open-Meteo はローカル日付と UTC の両方で扱えるため、呼び出し時に適切に変換する。
- レート制限対策: Nominatim の利用規約に従い、キャッシュ（location テーブル）を採用し再利用する。バルクジオコーディングは避ける。

## Open Questions (NEEDS CLARIFICATION -> resolved here)
- Q: CLI の対話性にどの程度の UI を用いるか（単純 input() か、対話ライブラリか）?  
  A: `rich` + 標準 input() で十分。高度なプロンプトは将来追加。

## Security / Privacy
- ユーザーの位置情報はローカルに保存する設計。外部サーバへ共有は行わない（ジオコーディングは外部へ問い合わせるが保存は最小限）。

## Conclusion
上の選択で初期実装を進め、必要に応じてライブラリを差し替え可能。次は Phase1 のデータモデルと CLI 契約を生成する。
