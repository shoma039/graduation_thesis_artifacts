# Tasks for: Todo CLI — todo-weather-scheduler

Phase 1: Setup

 - [x] T001 Create project skeleton and folders `src/`, `src/cli/`, `src/models/`, `src/services/`, `src/db/`, `tests/` (`specs/001-todo-weather-scheduler`)
 - [x] T002 [P] Create `requirements.txt` with `requests`, `dateparser`, `typer`, `python-dateutil` (`requirements.txt`)
 - [x] T003 [P] Create `pyproject.toml` or `setup.cfg` minimal packaging file (`pyproject.toml`)
 - [x] T004 Create `README.md` and `specs/001-todo-weather-scheduler/quickstart.md` reference (`README.md`)

Phase 2: Foundational (blocking prerequisites)

 - [x] T005 Implement SQLite DB wrapper in `src/db/db.py` (connect, migrations, simple query helpers)
 - [x] T006 Implement data models in `src/models/task_model.py` and `src/models/location_model.py` (fields, validation) 
 - [x] T007 Implement date parsing service in `src/services/parser.py` (日本語自然言語 → timezone-aware datetime)
 - [x] T008 Implement geocoding service in `src/services/geocode.py` (都市名 → latitude, longitude, timezone) using APIキー不要のジオコーディング
 - [x] T009 Implement weather fetcher in `src/services/weather.py` (given lat/lon+tz → daily precipitation probability and temps, with caching) 
 - [x] T010 Implement timezone utilities in `src/services/timezone_utils.py` (resolve IANA tz from lat/lon, convert datetimes)
 - [x] T011 [P] Add basic logging and error classes in `src/lib/errors.py` and `src/lib/logging.py`

Phase 3: User Story Phases (priority order)

US1 (P1) — タスク登録 + 候補日算出（自然言語期限パース + ジオコーディング + 天気取得）

 - [x] T012 [US1] Implement `todo add` CLI command entry in `src/cli/commands/add.py` (args: `--title`, `--location`, `--due`, `--priority`)
 - [x] T013 [US1] In `src/cli/commands/add.py`, call `src/services/parser.py` to parse `--due` to timezone-aware `due_date`
 - [x] T014 [US1] In `src/cli/commands/add.py`, call `src/services/geocode.py` to resolve location and persist `src/models/location_model.py`
 - [x] T015 [US1] Implement candidate selection logic in `src/services/scheduler.py` (fetch forecasts from `src/services/weather.py`, pick lowest precipitation day within due date range)
 - [x] T016 [US1] Persist Task with assigned `candidate_date` via `src/db/db.py` and models in `src/models/task_model.py`
 - [x] T017 [US1] CLI output: show created task summary in Japanese in `src/cli/commands/add.py` (ID, candidate date, precipitation, temp)
 - [x] T018 [P] [US1] Add unit tests for parser + scheduler in `tests/unit/test_parser.py` and `tests/unit/test_scheduler.py`

Independent test criteria (US1):

- タスクを `todo add --title "X" --location "札幌" --due "明日"` で作成すると、`show <id>` で `candidate_date` が存在し、期限内で降水確率が低い日が割り当てられていること。

US2 (P2) — 一覧 / 詳細 / 更新 / 削除（完了は削除）

 - [x] T019 [US2] Implement `todo list` CLI in `src/cli/commands/list.py` (supports `--sort`)
 - [x] T020 [US2] Implement `todo show <id>` in `src/cli/commands/show.py` (detailed Japanese output)
 - [x] T021 [US2] Implement `todo update <id>` in `src/cli/commands/update.py` (supports `--title`, `--location`, `--due`, `--priority`, `--complete`)
 - [x] T022 [US2] Implement `todo delete <id>` in `src/cli/commands/delete.py`
 - [x] T023 [US2] Implement completion behavior in update handler: if `--complete true`, delete task from DB and print confirmation in Japanese (update logic in `src/cli/commands/update.py`)
- [ ] T024 [P] [US2] Add integration tests for CRUD flows in `tests/integration/test_crud.py`
 - [x] T024 [P] [US2] Add integration tests for CRUD flows in `tests/integration/test_crud.py`

Independent test criteria (US2):

- `todo add` で作成したタスクを `todo list` と `todo show <id>` で確認でき、`todo update <id> --complete true` 実行後に `todo show <id>` が存在しない（エラー）こと。

US3 (P3) — 候補日競合回避（先着順） & 代替日提案

 - [x] T025 [US3] Implement candidate conflict resolver in `src/services/scheduler.py` (先着順: 既存タスクの作成日時を確認し、後続は次善の空き日に割り当てる)
 - [x] T026 [US3] Implement alternative date proposer in `src/services/scheduler.py` (期限内に最適日が無い場合、期限後の最初の空き日を提案; show as "予備日")
 - [x] T027 [US3] Add tests for conflict and alternative proposal in `tests/unit/test_scheduler_conflict.py`

Independent test criteria (US3):

- 2つのタスクが同じ最適日を算出する条件で作成した際、先に作成したタスクがその日を保持し、後続タスクは別日に割り当てられること。
- 期限内に最適日が無い場合、期限後の予備日が提示されること（提案に気温表示含む）。

US4 (P4) — カレンダー表示（月選択）

- [ ] T028 [US4] Implement `todo calendar --month YYYY-MM` in `src/cli/commands/calendar.py` (month view, date-sorted list)
- [ ] T029 [US4] Add unit/integration tests for calendar output in `tests/integration/test_calendar.py`
 - [x] T028 [US4] Implement `todo calendar --month YYYY-MM` in `src/cli/commands/calendar.py` (month view, date-sorted list)
 - [x] T029 [US4] Add unit/integration tests for calendar output in `tests/integration/test_calendar.py`

Independent test criteria (US4):

- `todo calendar --month 2025-12` でその月のタスク候補日と期限日が日付順で見やすく表示されること。

Final Phase: Polish & Cross-Cutting Concerns

- [ ] T030 Implement robust error handling and Japanese messages in `src/lib/errors.py` (validation, API errors, DB errors)
 - [x] T030 Implement robust error handling and Japanese messages in `src/lib/errors.py` (validation, API errors, DB errors)
 - [x] T031 Ensure all datetime handling uses location timezone in `src/services/timezone_utils.py` and update all services to use it (`src/services/*.py`)
 - [x] T032 Add caching/TTL for forecast data in `src/services/weather.py` (cache file or DB table) and tests in `tests/unit/test_weather_cache.py`
 - [x] T033 Documentation: update `README.md`, add `docs/usage.md` and examples (`docs/`) 
 - [x] T034 Add CI job skeleton for `pytest` and linting (GitHub Actions workflow `.github/workflows/ci.yml`)
 - [x] T035 Finalize `specs/001-todo-weather-scheduler/tasks.md` and validate checklist format (this file) (`specs/001-todo-weather-scheduler/tasks.md`)

Dependencies (story completion order)

- Phase 1 → Phase 2 → US1 → US2 → US3 → US4 → Final Phase
- Notes:
  - `T005`..`T011` must be completed before `T012`..`T018` (US1) can fully run.
  - `T012`..`T017` provide inputs required by US2 commands.

Parallel execution examples (per story)

- US1 parallelizable tasks: `T013` (parser), `T014` (geocode), `T015` (scheduler algorithm) and `T018` (unit tests) can be developed in parallel once models and DB wrappers (`T005`,`T006`) exist — mark each with `[P]` where safe.
- US2 parallelizable tasks: `T019`, `T020`, `T021`, `T022` can be implemented in parallel after DB/models are ready.
- Cross-cutting parallel work: `T011` (logging/errors), `T030` (error messages) and `T031` (timezone) can be implemented alongside features but require coordination.

Validation: Task completeness

- Each user story maps to a set of model/service/CLI tasks. Each story is independently testable by the provided independent test criteria. Foundational tasks exist to unblock story implementation.

Implementation strategy (MVP first, incremental delivery)

- MVP scope: **US1 only** (タスク登録 + 候補日算出 + 最小限の表示)。 Implement `T005`..`T017` and `T030` minimal error messages. This gives a working CLI that creates tasks and assigns candidate dates.
- Incremental steps after MVP: Implement US2 CRUD, then US3 conflict avoidance & alternatives, then US4 calendar, then polish and docs.

Notes & assumptions

- All file paths are relative to project root. Replace placeholders with actual module names if needed.
- Tests are included for critical components; full TDD not required by spec but recommended.
