# data-model.md — Todo CLI データモデル

## Entities

- **Task**
  - `id` (INTEGER PRIMARY KEY)
  - `title` (TEXT, not null)
  - `priority` (TEXT CHECK IN ('高','中','低'), default '中')
  - `location_id` (INTEGER, FK -> Location.id)
  - `deadline_utc` (TEXT ISO8601 UTC)
  - `candidate_date_local` (TEXT ISO8601 local date string) — 候補日のローカル日付
  - `status` (TEXT CHECK IN ('open','complete'), default 'open')
  - `created_at` (TEXT), `updated_at` (TEXT)

- **Location**
  - `id` (INTEGER PRIMARY KEY)
  - `user_input_name` (TEXT)
  - `latitude` (REAL)
  - `longitude` (REAL)
  - `timezone` (TEXT, tz database name)
  - `geocoded_at` (TEXT)

- **ForecastSample** (キャッシュ／記録用)
  - `id` (INTEGER PRIMARY KEY)
  - `location_id` (INTEGER)
  - `date_local` (TEXT)  # local date
  - `precip_probability` (REAL) # 0-100
  - `temperature_c` (REAL)
  - `fetched_at` (TEXT)

## Relationships
- Task.location_id → Location.id (1:N)
- ForecastSample.location_id → Location.id (1:N)

## Validation rules
- `deadline_utc` must be after `created_at`.
- `candidate_date_local` must be within range [deadline - lookback window, deadline] (ローカル日付基準)

## Notes on timezone handling
- 保存は `deadline_utc`（UTC）とし、表示／候補日計算は `Location.timezone` でローカル変換して行う。
