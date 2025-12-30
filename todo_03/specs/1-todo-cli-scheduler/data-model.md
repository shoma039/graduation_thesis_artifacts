# Data Model: Todo CLI Scheduler

Entities

- Task
  - `id` (integer) — 一意の識別子
  - `title` (string, required, max 200 chars)
  - `completed` (boolean, default: false)
  - `priority` (enum: "high" | "medium" | "low", default: "medium")
  - `location_id` (reference to `Location`)
  - `due_date` (ISO 8601 date string, local date in the location's timezone)
  - `candidate_dates` (array of `CandidateDate`)
  - `created_at` (ISO 8601 datetime UTC)
  - `updated_at` (ISO 8601 datetime UTC)

- Location
  - `id` (string, e.g., slug or UUID)
  - `name` (string, user-entered city name)
  - `latitude` (number)
  - `longitude` (number)
  - `timezone` (IANA timezone string, e.g., `Asia/Tokyo`)

- CandidateDate
  - `date` (ISO 8601 date string — stored as local date in `Location.timezone`)
  - `precipitation_probability` (number: 0..100, percent)
  - `temperature` (number: degrees Celsius; may be min/avg/max depending on API granularity)
  - `reason` (string, e.g., "降水確率最小")
  - `task_id` (reference back to `Task`)

Validation Rules

- `title` is required and non-empty.
- `due_date` must be on or after today's date in the `Location.timezone` (reject past dates).
- `priority` must be one of the allowed enums.
- `location` must resolve to a lat/lon and timezone via geocoding; if not resolvable, prompt user to retry.
- `candidate_dates` must not overlap with other tasks' `candidate_dates` (enforced by selection algorithm at assignment time).

Timezone & Date Handling

- All date parsing uses the location's timezone for disambiguation. Tasks store `due_date` as local date plus the `Location.timezone` string.
- CandidateDate `date` is stored as a local date string and when displayed converted to local human-readable forms using `zoneinfo`.

Persistence

- Stored as JSON file containing arrays: `locations`, `tasks`, `candidate_dates`.
- On write, perform an atomic replace (write to temp file then move) to avoid corruption.
