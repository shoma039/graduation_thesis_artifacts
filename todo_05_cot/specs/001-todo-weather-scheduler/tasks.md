---
description: "Generated task list for Todo リスト（天気連動スケジューラ）"
---

# Tasks: Todo リスト（天気連動スケジューラ）

**Input**: `spec.md`, `plan.md`, `data-model.md`, `research.md`, `contracts/openapi.yaml`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 初期プロジェクト構造、依存関係、基本ファイルを作成して開発が始められる状態にする

- [x] T001 Create project directories: `src/`, `src/cli/`, `src/models/`, `src/services/`, `src/utils/`, `tests/`, `docs/` (create folders at project root)
- [x] T002 Create `requirements.txt` with initial dependencies (`dateparser`, `httpx`, `pytest`) at `/requirements.txt`
- [x] T003 Create `README.md` with feature summary and usage at `/README.md`
- [x] T004 Create `.gitignore` and basic repo files at `/.gitignore`
- [x] T005 [P] Create CLI entrypoint skeleton `src/cli/main.py` (basic argparse/cli placeholder)
- [x] T006 [P] Create initial `specs/001-todo-weather-scheduler/quickstart.md` (copy from plan quickstart) if not present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: データモデル・永続化・外部APIインターフェースなど、すべてのユーザーストーリーに必要な基盤を実装する

- [x] T007 Create SQLite schema script `src/db/schema.py` to create tables `tasks`, `candidate_dates`, `locations`
- [x] T008 [P] Implement Task model in `src/models/task.py` (fields: id,title,completed,priority,place_id,deadline,created_at,updated_at)
- [x] T009 [P] Implement Location model in `src/models/location.py` (fields: id,display_name,lat,lon,timezone)
- [x] T010 [P] Implement CandidateDate model in `src/models/candidate_date.py` (fields: id,task_id,date,is_confirmed,expected_precipitation,expected_temperature)
- [x] T011 [P] Implement storage layer `src/services/storage.py` (SQLite CRUD helpers, connection management, transaction helpers)
- [x] T012 [P] Implement date parsing service `src/services/date_parser.py` (wrap `dateparser` and return timezone-aware datetimes)
- [x] T013 [P] Implement geocoding service interface `src/services/geocode.py` (Nominatim wrapper + simple cache in `src/services/cache.py`)
- [x] T014 [P] Implement weather service interface `src/services/weather.py` (Open-Meteo wrapper to fetch daily/hourly precip & temp)
 - [x] T015 Implement timezone helper `src/utils/timezone.py` (convert between UTC and place timezone)
 - [x] T016 Implement error types and handling helpers `src/lib/errors.py` and `src/lib/logging_config.py`

**Checkpoint**: Foundation complete — models, storage, date parsing, geocoding, weather, and timezone helpers implemented

---

## Phase 3: User Story 1 - タスク登録（優先度・場所・期限付き） (Priority: P1) 🎯 MVP

**Goal**: CLIでタスクを登録（自然言語期限、都市名→緯度経度・タイムゾーン取得、DB保存）できるようにする

**Independent Test**: `python -m src.cli.main add --title "..." --deadline "明日" --place "Tokyo"` を実行してタスクがDBに保存され、`python -m src.cli.main list` で確認できる

 - [x] T017 [US1] Implement `add` command in `src/cli/commands.py` to accept `--title`, `--deadline`, `--place`, `--priority`
 - [x] T018 [US1] Implement registration service `src/services/registration.py` that: parses natural date (`src/services/date_parser.py`), calls `src/services/geocode.py` to resolve place, and persists Task via `src/services/storage.py` (file: `src/services/registration.py`)
 - [x] T019 [P] [US1] Implement CLI output formatting helpers in `src/cli/output.py` for Japanese-friendly messages
 - [x] T020 [US1] Implement `list` command in `src/cli/commands.py` to show active tasks in date order (uses `src/services/storage.py`)
 - [x] T021 [US1] Implement `detail` command in `src/cli/commands.py` to show full task details including candidate dates and expected weather
 - [x] T022 [US1] Add input validation and Japanese error messages in `src/services/validation.py` (used by CLI and services)

**Checkpoint**: 新規登録と一覧・詳細が動くことで最小のMVPが成立する

---

## Phase 4: User Story 2 - 天気をもとに候補日を自動選択 (Priority: P1)

**Goal**: 期限内で降水確率が低い日を候補日として自動選出し、候補日の衝突は「先に登録されたタスクを優先」して解消する

**Independent Test**: モック天気データを使い `python -m src.cli.main schedule --task-id <id>` または `--all` を実行して `candidate_dates` テーブルに候補日が登録され、競合が解消される

 - [x] T023 [US2] Implement scheduler core `src/services/scheduler.py` that fetches weather (`src/services/weather.py`) and ranks dates by precip probability and availability
 - [x] T024 [P] [US2] Implement conflict resolution per spec in `src/services/scheduler.py` (registration-time priority, tie-breakers, max 3 reassign attempts)
 - [x] T025 [US2] Implement persistence of candidate dates in `src/services/scheduler.py` (insert into `candidate_dates` table)
 - [x] T026 [US2] Implement CLI `schedule` command in `src/cli/commands.py` to trigger candidate generation for a task or all tasks
 - [x] T027 [US2] Implement fallback: when no good date exists, present up to 3 alternative free dates with expected temperature (`src/services/scheduler.py`)
 - [x] T028 [US2] Add deterministic behavior and unit tests scaffold `tests/test_scheduler.py` (optional but recommended) at `/tests/`

---

## Phase 5: User Story 3 - タスクの一覧・詳細・更新・削除 / カレンダー機能 (Priority: P1)

**Goal**: タスクの更新・完了（削除）・カレンダー表示を実装し、期限・候補日の表示は場所のタイムゾーンで正しく行う

**Independent Test**: `complete` でタスクが消えること、`calendar --month YYYY-MM` で月別に日付順で表示されることを確認する

- [x] T029 [US3] Implement `complete` command in `src/cli/commands.py` that marks a task complete and removes it from active tasks (uses `src/services/storage.py`)
- [x] T030 [US3] Implement `update` command in `src/cli/commands.py` to edit title/priority/place/deadline (uses validation and registration service)
- [x] T031 [US3] Implement calendar view `src/cli/calendar.py` to render tasks by date and support `--month YYYY-MM` (file: `src/cli/calendar.py`)
- [x] T032 [US3] Implement candidate confirmation flow `src/cli/commands.py` and ensure confirming a candidate reserves it and prevents collisions (`src/services/scheduler.py` check)
- [x] T033 [US3] Implement place disambiguation flow in `src/cli/commands.py` (when `src/services/geocode.py` returns multiple candidates prompt user)

---

## Phase N: Polish & Cross-Cutting Concerns

- [x] T034 [P] Add `docs/` and polish `README.md` with Japanese usage examples and quickstart at `/docs/usage.md`
- [x] T035 Add unit test skeletons for key modules in `tests/` (`tests/test_storage.py`, `tests/test_date_parser.py`, `tests/test_geocode.py`)
- [x] T036 [P] Add CI workflow for running `pytest` (create `.github/workflows/ci.yml`)
- [x] T037 [P] Add logging and error reporting improvements in `src/lib/logging_config.py` and docs
- [x] T038 Run `specs/001-todo-weather-scheduler/quickstart.md` validation and update docs if needed

---

## Dependencies & Execution Order

- Phase 1 (Setup) -> Phase 2 (Foundational) -> Phase 3/4/5 (User Stories) -> Phase N (Polish)
- User stories require Foundational completion. After foundational tasks, US1/US2/US3 can progress in parallel where tasks marked `[P]` indicate safe parallel work.

## Parallel Execution Examples

- While `src/models/*.py` files are created (T008-T010) those tasks are `[P]` and can be implemented concurrently by different engineers.
- `src/services/date_parser.py`, `src/services/geocode.py`, `src/services/weather.py` (T012-T014) are independent and marked `[P]` for parallel work.
- User story level: `add`/`list`/`detail` (US1) can be implemented in parallel with scheduler service (US2) after foundational tasks.

## Implementation Strategy

- MVP scope: Implement Phase1 + Phase2 + Phase3 (US1) so CLI can `add`, `list`, `detail` with date parsing and geocoding (weather scheduling mocked). This yields a usable MVP quickly.
- Incremental delivery: After MVP, implement scheduler (US2) then calendar/update/complete (US3).
- Testing: Use mocking for external APIs (geocoding/weather) in unit/integration tests to make behavior deterministic.

---

## Generated Task Counts & Notes

- Total tasks generated: 38
- Tasks per story:
  - Phase 1 (Setup): 6
  - Phase 2 (Foundational): 10
  - US1 (Registration): 6
  - US2 (Scheduler): 6
  - US3 (List/Update/Delete/Calendar): 5
  - Polish & Cross-Cutting: 5

**Format Validation**: All tasks follow the checklist format `- [ ] TNNN [P?] [US?] Description with file path`.

**File path**: `specs/001-todo-weather-scheduler/tasks.md`
