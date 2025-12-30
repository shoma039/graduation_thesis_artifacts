# data-model.md

## Entities

### Task
- `id` (integer, primary key, auto-increment)
- `title` (string, required)
- `completed` (boolean, default false)
- `priority` (enum: low, medium, high)
- `place_id` (integer, foreign key -> Location.id)
- `deadline` (datetime with timezone, required)
- `candidate_dates` (serialized list or normalized table CandidateDate)
- `created_at` (datetime UTC)
- `updated_at` (datetime UTC)

Validation rules:
- `title` 必須、最大長 200 文字
- `deadline` は `created_at` より未来であること（または同日）

### CandidateDate
- `id` (integer, primary key)
- `task_id` (integer, foreign key -> Task.id)
- `date` (date in local place timezone)
- `is_confirmed` (boolean)
- `expected_precipitation` (float: 0.0-100.0 as %)
- `expected_temperature` (float: Celsius)

Constraints:
- task と同一期限範囲内の日付のみ許可

### Location
- `id` (integer, primary key)
- `display_name` (string, e.g., "Tokyo, JP")
- `lat` (float)
- `lon` (float)
- `timezone` (string, IANA tz, e.g., Asia/Tokyo)

Indexes:
- Task.deadline (for calendar queries)
- CandidateDate.date, CandidateDate.task_id
- Location.display_name (unique per saved entry)

Persistence design:
- 単純実装では SQLite に以下のテーブルを作成: `tasks`, `candidate_dates`, `locations`。
- `candidate_dates` は正規化したテーブルとし、候補日重複検査を DB レベルでも補助する。

State transitions:
- Task: created -> (candidate dates assigned) -> in-progress -> completed (on complete, record removed from active tasks)
- CandidateDate: generated -> assigned -> confirmed (if user confirms)
