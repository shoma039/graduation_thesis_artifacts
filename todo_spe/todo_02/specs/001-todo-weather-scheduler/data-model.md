# data-model.md

## エンティティ定義

### Task
- id: INTEGER (PRIMARY KEY)
- title: TEXT (必須, 最大長 255)
- completed: BOOLEAN (既定: FALSE)
- priority: TEXT ENUM ('low','medium','high') (既定: 'medium')
- location_id: INTEGER (Location.id への外部キー, NULL 許容? 位置指定必須にする)
- due_date: TIMESTAMP WITH TZ (期限日時、タイムゾーン付き)
- candidate_date: TIMESTAMP WITH TZ (選択された候補日、NULL 可)
- created_at: TIMESTAMP WITH TZ
- updated_at: TIMESTAMP WITH TZ

検証ルール:
- `title` は空でないこと。
- `due_date` は `created_at` より未来であること（または同日内の未来時間）。
- `candidate_date` は `due_date` の同期間内であるか、代替提案（期限外予備）としてマークされる。

### Location
- id: INTEGER (PRIMARY KEY)
- name: TEXT (都市名など、ユーザー入力)
- latitude: REAL
- longitude: REAL
- timezone: TEXT (IANA タイムゾーン名)

検証ルール:
- 緯度は -90..90、経度は -180..180
- timezone は `zoneinfo` で解決可能な IANA 名であること

### Forecast (キャッシュ用)
- id: INTEGER (PRIMARY KEY)
- location_id: INTEGER (Location.id への外部キー)
- date: DATE (タイムゾーンを含めた日付表示のため日付と tz を組合せて保存)
- precipitation_prob: REAL (0.0 - 1.0)
- temp_min: REAL
- temp_max: REAL
- fetched_at: TIMESTAMP WITH TZ (キャッシュ取得時刻)

キャッシュポリシー:
- 予報は一定期間（例: 6 時間）キャッシュし、それ以降は再取得する。

## リレーション
- Task.location_id → Location.id (1:N)
- Forecast.location_id → Location.id (1:N)

## 状態遷移（Task）
- NEW -> CANDIDATE_ASSIGNED (候補日が割り当てられた)
- CANDIDATE_ASSIGNED -> COMPLETED (ユーザーが完了と更新)
- COMPLETED -> DELETED (完了時にストレージから削除するため遷移は短命)

## インデックス/制約
- Task(candidate_date) はユニークに近いルール（候補日は基本的に他タスクと被らない）をアプリケーションレベルで保証する。厳密な DB の UNIQUE 制約は候補日が NULL となるケースやタイムゾーン差で難しいため、アプリケーションロジックで検証してから保存する。

