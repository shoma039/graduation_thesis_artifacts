---
description: "Tasks for Todo CLI Scheduler feature"
---

# Tasks: Todo CLI Scheduler

**Input**: Design documents from `/specs/1-todo-cli-scheduler/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: プロジェクト初期化と最低限の実行可能な骨組みを作る

- [x] T001 Create project skeleton directories and initial files: `src/todo_cli/`, `src/models/`, `src/services/`, `tests/`, `requirements.txt`, `README.md`
- [x] T002 Create Python package entrypoint `src/todo_cli/__main__.py` and CLI module `src/todo_cli/cli.py`
- [x] T003 Create `requirements.txt` with initial dependencies (`dateparser`, `rich`, `requests`, `questionary`, `tzdata`)
- [x] T004 Add `specs/1-todo-cli-scheduler/quickstart.md` reference to root `README.md` at `README.md`
- [x] T005 Add `pyproject.toml` (minimal) and `pytest.ini` for tests at project root
- [x] T006 Add config helper `src/todo_cli/config.py` to determine data path (`%APPDATA%\todo-cli-scheduler\tasks.json` on Windows)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: すべてのユーザーストーリーが依存するコア機能（データモデル、永続化、外部APIクライアント）を実装する

- [x] T007 Implement `Task` model in `src/models/task.py` (fields per `data-model.md`)
- [x] T008 Implement `Location` model in `src/models/location.py`
- [x] T009 Implement `CandidateDate` model in `src/models/candidate_date.py`
- [x] T010 Implement atomic JSON storage service `src/services/storage.py` with functions: `load_all()`, `save_all()`, `add_task()`, `update_task()`, `delete_task()`; use atomic write (temp file + move)
- [x] T011 Implement date parsing service `src/services/date_parser.py` using `dateparser`, accept natural language and a target timezone, and provide a confirmation string for users
- [x] T012 Implement geocoding service `src/services/geocode.py` that resolves a city name to `latitude`, `longitude`, and `timezone`, and caches results in storage
- [x] T013 Implement weather client `src/services/weather.py` that fetches precipitation probability and temperature for a given `latitude, longitude, date range` (API-keyless public endpoint) and normalizes results to percent/°C
- [x] T014 Implement scheduler service `src/services/scheduler.py` that, given a `due_date`, finds optimal `CandidateDate` based on weather and existing `candidate_dates` (avoid conflicts)
- [x] T015 Implement basic CLI command routing in `src/todo_cli/cli.py` with stubs for `add, list, show, update, complete, delete, calendar`
- [x] T016 Implement utilities `src/services/utils.py` for timezone conversions and atomic file operations

**Checkpoint**: Foundational tasks complete → ここまで完了すればストーリー実装を開始できる

---

## Phase 3: User Story 1 - タスクの登録と自然言語日付入力 (Priority: P1) 🎯 MVP

**Goal**: CLIで新規タスクを対話的に登録できる。自然言語の日付入力を場所のタイムゾーンで解釈して保存する。

**Independent Test**: `python -m todo_cli add` を実行して「明日」「来週の月曜」等を入力し、`src/services/storage.py` に正しい `due_date` と `location` が保存されていることを確認する。

- [x] T017 [US1] Implement `add` command interaction in `src/todo_cli/cli.py`: prompt for `title`, `due` (natural language), `priority`, `location`; call `date_parser` and show parsed date for confirmation before saving
- [x] T018 [US1] Validate parsed `due_date` vs `location.timezone` in `src/models/validation.py` (reject past dates)
- [x] T019 [US1] Persist new Task to storage via `src/services/storage.py` and return created `id`
- [x] T020 [US1] Show success message and the stored task summary in Japanese (implement in `src/todo_cli/formatters.py`)

**Checkpoint**: US1 は単独で実行・検証可能で、MVP の主要流れを実現する

---

## Phase 4: User Story 2 - 天気に基づく候補日の自動選定 (Priority: P1)

**Goal**: タスク登録時（または更新時）に、期限内で降水確率が最小かつ他タスクの候補日と重複しない日を候補日として選定し保存する。最適日がなければ期限外の空き日を提案する。

**Independent Test**: 既存タスクの候補日と衝突しない状態で新規タスクを登録し、`candidate_dates` に最適日が1件以上保存されていることを確認する。

- [x] T021 [US2] Integrate `scheduler` in `src/services/scheduler.py` into `add` and `update` flows so candidate日が生成される
- [x] T022 [US2] Implement conflict-avoidance in `src/services/scheduler.py`: query storage for existing `candidate_dates` and skip occupied dates
- [x] T023 [US2] Implement fallback proposal logic in `src/services/scheduler.py` to find the next available date outside the deadline and include precipitation/temperature in the candidate entry
- [x] T024 [US2] Persist `candidate_dates` to the Task record via `src/services/storage.py` and display chosen candidate to the user in Japanese

---

## Phase 5: User Story 3 - タスク一覧・詳細・更新・削除（完了時自動削除） (Priority: P2)

**Goal**: タスクの一覧・詳細・更新・削除を提供し、タスクを完了に更新すると自動的に記録から削除する。

**Independent Test**: タスクを `complete` コマンドで完了にした際、`src/services/storage.py` から当該タスクが消えていることを確認する。

- [x] T025 [US3] Implement `list` command in `src/todo_cli/cli.py` to show pending tasks sorted by date (use `src/todo_cli/formatters.py`)
- [x] T026 [US3] Implement `show <id>` command in `src/todo_cli/cli.py` to display task details including `candidate_dates` and weather info
- [x] T027 [US3] Implement `update <id>` command in `src/todo_cli/cli.py` to edit title/priority/location/due_date and re-run scheduler as needed
- [x] T028 [US3] Implement `complete <id>` command in `src/todo_cli/cli.py` that removes task from storage (prompt for confirmation)
- [x] T029 [US3] Implement `delete <id>` command in `src/todo_cli/cli.py` with confirmation

---

## Phase 6: User Story 4 - カレンダー表示 (Priority: P2)

**Goal**: 月単位でカレンダービューを提供し、日付順でタスク候補日と期限を見やすく表示できる（月切替可）。

**Independent Test**: `python -m todo_cli calendar 2025-12` を実行し、その月のタスクが日付順で表示されることを確認する。

- [P] T030 [US4] Implement calendar view module `src/todo_cli/calendar_view.py` using `rich` to render a monthly calendar with tasks marked on dates
- [x] T031 [US4] Integrate `calendar` command in `src/todo_cli/cli.py` to accept `YYYY-MM` and default to current month
- [x] T032 [US4] Ensure calendar sorts multi-task dates and shows candidate vs due-date markers (implement in `src/todo_cli/formatters.py`)

---

## Phase Final: Polish & Cross-Cutting Concerns

- [P] T033 [P] Add robust error handling and user-friendly Japanese messages in `src/todo_cli/errors.py` and integrate across CLI
- [P] T034 [P] Add logging and diagnostics in `src/todo_cli/logging.py` (ensure logs are human-readable and optional debug mode)
-- [P] T035 [P] Add caching for geocoding results in `src/services/storage.py` and implement exponential backoff/retry for external calls in `src/services/http_retry.py`
- [x] T036 Update `specs/1-todo-cli-scheduler/quickstart.md` and top-level `README.md` with real install/run steps and examples
- [x] T037 Validate all user-facing strings are Japanese and consistent (search/replace under `src/todo_cli/`)

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → 完了後に **Phase 2 (Foundational)** を開始してください。Foundational が完了するまではユーザーストーリーを開始しないでください。
- **User Stories** は Foundational 完了後に並行実装可能です。優先順は P1 (US1, US2) → P2 (US3, US4)

### Story Dependencies (簡略)
- US1 (T017-T020) depends on: T007-T016
- US2 (T021-T024) depends on: T010-T013, T014
- US3 (T025-T029) depends on: T010, T007
- US4 (T030-T032) depends on: T010, T007

---

## Parallel Execution Examples

- Parallelize file creation and small helpers in Phase 1: `T002`, `T003`, `T005` can run concurrently (marked [P]).
- During Foundational phase, create model files `T007/T008/T009` in parallel, then implement `T010` storage before integration steps.
- After Foundational phase, work streams:
  - Stream A: US1 (T017-T020)
  - Stream B: US2 (T021-T024)
  - Stream C: US3 (T025-T029) and US4 (T030-T032)

---

## Implementation Strategy

- MVP First: Complete Phase 1 + Phase 2, then implement US1 (T017-T020) and stop to validate (this yields a usable MVP: add tasks with natural-language dates and persistence).
- Incremental Delivery: After MVP, implement US2 to add weather-based scheduling, then US3 and US4.
- Keep tasks small and file-scoped so LLMs or individual contributors can implement tasks independently.

---

## Files Referenced by Tasks

- `src/todo_cli/cli.py` — CLI entry and command routing
- `src/todo_cli/__main__.py` — module entry for `python -m todo_cli`
- `src/todo_cli/calendar_view.py` — calendar rendering code
- `src/todo_cli/formatters.py` — display helpers for Japanese output
- `src/models/task.py`, `src/models/location.py`, `src/models/candidate_date.py` — data models
- `src/services/storage.py`, `src/services/date_parser.py`, `src/services/geocode.py`, `src/services/weather.py`, `src/services/scheduler.py` — core services
- `requirements.txt`, `pyproject.toml`, `README.md`, `specs/1-todo-cli-scheduler/quickstart.md`

---

## Validation Checklist

- All tasks follow the required checklist format with Task IDs and file paths.
- Each user story is independently testable after its phase tasks are complete.
