---

description: "Tasks for todo-weather-cli feature"

---

# Tasks: Todo 天気連携CLI (todo-weather-cli)

**Input**: Design documents from `specs/1-todo-weather-cli/`
**Prerequisites**: `plan.md`, `spec.md` (user stories), `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: プロジェクト初期化と基本構造の作成

- [x] T001 Create project directories `src/`, `tests/`, `docs/` and subfolders as per plan (`src/cli`, `src/models`, `src/services`, `src/storage`, `src/scheduler`, `src/utils`, `tests/unit`, `tests/integration`, `docs/`)
- [x] T002 Create `requirements.txt` in project root with pinned dependencies (`click`, `requests`, `geopy`, `dateparser`, `timezonefinder`, `filelock`, `prompt-toolkit`, `pytest`)
- [x] T003 Create `README.md` with Quickstart based on `specs/1-todo-weather-cli/quickstart.md`
- [x] T004 Create minimal `pyproject.toml` or `setup.cfg` in project root for packaging (`pyproject.toml`)
- [x] T005 [P] Create CLI entrypoint files `src/cli/cli.py` and `src/cli/__init__.py` (basic `click` command scaffold)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: コアインフラ（これが完了するまでユーザーストーリーは実装できない）

- [x] T006 Implement Task dataclass in `src/models/task.py` (fields: id,title,completed,priority,location,due_date,candidate_dates,created_at,updated_at)
- [x] T007 Implement JSON storage with file locking in `src/storage/store.py` (read/write/ID generation, default path: `%USERPROFILE%\\.todo_weather_cli\\tasks.json`)
- [x] T008 [P] Implement geocoding service interface in `src/services/geocoding.py` (Nominatim via `geopy`, with caching and candidate selection UI)
- [x] T009 [P] Implement timezone helper in `src/services/timezone.py` (wrap `timezonefinder` and normalization)
- [x] T010 [P] Implement weather service interface in `src/services/weather.py` (Open-Meteo wrapper: daily/hourly precipitation and temperature retrieval)
 - [x] T011 Implement date parsing utility in `src/utils/parse_date.py` (wrap `dateparser` and ensure tz-aware parsing using location timezone)
 - [x] T012 Implement basic logging and error classes in `src/utils/logging.py` and `src/utils/errors.py`


**Checkpoint**: Phase 2 完了後、個別のユーザーストーリー作業へ移行できます。

---

## Phase 3: User Story 1 - タスク登録（自然言語日付） (Priority: P1) 🎯 MVP

**Goal**: 日本語の自然表現で期限・場所を指定してタスクを追加し、天気に基づく候補日をタスクに保存する。

**Independent Test**: `todo add --title "公園清掃" --due "明日" --priority 高 --location "東京"` を実行すると、タスクが作成され、候補日が1件以上 `candidate_dates` に保存される（`src/storage/store.py` を直接確認できること）。

### Tests

- [x] T013 [P] [US1] Add unit tests for Japanese date parsing in `tests/unit/test_parse_date.py` (include examples: 明日, 来週の月曜, 来月第2金曜)
- [x] T014 [P] [US1] Add integration test for `add` command in `tests/integration/test_add_command.py` (mock geocoding & weather)

### Implementation

- [x] T015 [P] [US1] Implement `add` command handler in `src/cli/cli.py` calling services: geocoding, timezone, parse_date, weather, storage
- [x] T016 [US1] Implement candidate selection orchestration in `src/scheduler/candidate_selector.py` (scoring by precipitation then temperature)
- [x] T017 [US1] Persist created Task to `src/storage/store.py` and verify `candidate_dates` saved
- [x] T018 [US1] Add input validation and user-friendly Japanese error messages in `src/cli/cli.py` and `src/utils/errors.py`

**Checkpoint**: `add` コマンドが動作し、タスクと候補日がストレージに保存されること。

---

## Phase 4: User Story 2 - タスク一覧表示 (Priority: P1)

**Goal**: 期限順に整列したタスク一覧を日本語で表示し、各タスクに候補日（降水確率・気温）を含める。

**Independent Test**: `todo list` が返す出力に、保存済みタスクのタイトル・期限・候補日が含まれること（`src/storage/store.py` と CLI 出力の比較で確認可能）。

### Tests

- [x] T019 [P] [US2] Unit tests for storage listing in `tests/unit/test_store_list.py`
- [x] T020 [P] [US2] Integration test for `list` command in `tests/integration/test_list_command.py`

### Implementation

- [x] T021 [P] [US2] Implement `list` command handler in `src/cli/cli.py` and output formatter in `src/utils/formatters.py`
- [x] - [ ] T022 [US2] Implement sorting by due_date in `src/storage/store.py` or util and include candidate summary

**Checkpoint**: `todo list` が期待どおり情報を表示する。

---

## Phase 5: User Story 3 - タスク詳細表示 (Priority: P1)

**Goal**: タスクIDを指定してタスクの全項目（位置情報含む）と候補日の天気情報・選定理由を表示する。

**Independent Test**: `todo show <id>` 実行で `candidate_dates` の詳細（降水確率・気温・reason）が表示されること。

### Tests

- [x] T023 [P] [US3] Unit tests for formatter of detailed view in `tests/unit/test_formatters.py`

### Implementation

- [x] T024 [US3] Implement `show` command handler in `src/cli/cli.py` and detailed formatter in `src/utils/formatters.py`

**Checkpoint**: `todo show <id>` が全フィールドを表示する。

---

## Phase 6: User Story 4 - タスク更新（完了） (Priority: P1)

**Goal**: タスクを更新でき、完了にマークされたタスクは自動的に削除される。

**Independent Test**: `todo complete <id>` 実行後に `src/storage/store.py` に当該タスクが存在しないこと。

### Tests

- [x] T025 [P] [US4] Unit tests for update/delete flows in `tests/unit/test_store_update.py`

### Implementation

- [x] - [x] T026 [US4] Implement `update` and `complete` handlers in `src/cli/cli.py` (if `complete`, remove from store)
- [x] - [x] T027 [US4] Ensure backups/undo logging in `src/storage/store.py` (optional safety)

**Checkpoint**: `todo complete <id>` でタスクがストレージから削除される。

---

## Phase 7: User Story 5 - タスク削除 (Priority: P2)

**Goal**: 指定IDのタスクを削除できる（削除確認のプロンプトを表示）。

**Independent Test**: `todo delete <id>` 実行で確認プロンプトが出て、`yes` で削除されること。

### Implementation

- [x] T028 [US5] Implement `delete` handler in `src/cli/cli.py` with confirmation prompt (use `prompt-toolkit` or `click.confirm`)

**Checkpoint**: 削除がユーザー確認を要求して正しく行われる。

---

## Phase 8: User Story 6 - カレンダービュー (Priority: P2)

**Goal**: 指定月のカレンダー形式でタスクを日付順に表示し、候補日をハイライトして気温・降水確率を表示する。

**Independent Test**: `todo calendar 2026-01` でカレンダー表示を返すこと。表示は日本語で見やすいこと。

### Tests

- [x] T029 [P] [US6] Integration test for `calendar` command in `tests/integration/test_calendar_command.py` (mocked store and weather)

### Implementation

- [x] - [x] T030 [US6] Implement `calendar` command in `src/cli/cli.py` and renderer in `src/utils/calendar_renderer.py`
- [x] - [x] T031 [US6] Ensure timezone-aware date rendering using `src/services/timezone.py`

**Checkpoint**: 月表示が視認可能であること。

---

## Phase 9: Cross-cutting / Date Parsing Robustness (Priority: P1)

**Goal**: 日本語の多様な日時表現に対応するためのテストと補助ルールを提供する。

**(注)**: `T032` と `T033` はこのリポジトリのタスクチェックリストから削除されました。

**Checkpoint**: 日付パースに関する今後の改善は個別タスクとして再追加してください。

---

## Final Phase: Polish & Cross-Cutting Concerns

- [x] T034 [P] Documentation updates in `docs/` and `README.md` to reflect implemented commands and Quickstart
- [x] T035 Code cleanup and refactoring (across `src/`)
- [x] T036 [P] Add more unit tests in `tests/unit/` for uncovered logic
- [x] T037 Security and error handling hardening (`src/utils/errors.py`) and input validation
- [x] T038 Run `specs/1-todo-weather-cli/quickstart.md` end-to-end validation and update docs accordingly

---

## Dependencies

- **Setup (Phase 1)**: T001 → T002/T003/T004/T005 (can be done in parallel)
- **Foundational (Phase 2)**: T006..T012 (blocker for all user stories)
- **User Stories**: Start after Phase 2 completes. Recommended order: US1, US2, US3, US4 (P1), then US5/US6 (P2). US7 tests are cross-cutting and should be executed early.

## Parallel Execution Examples

- While Phase 2 is being implemented, the following can be parallelized:
  - `T008` (geocoding) and `T010` (weather) can be implemented in parallel by different engineers — both expose service interfaces.
  - `T011` (date parsing) and `T009` (timezone helper) are independent and can be implemented in parallel.

- After Phase 2, multiple user stories can be implemented simultaneously (different CLI commands, different files). Example:
  - Dev A: US1 (`T015`, `T016`, `T017`)
  - Dev B: US2 (`T021`, `T022`)
  - Dev C: US6 (`T030`, `T031`)

## Implementation Strategy

- MVP: Phase 1 + Phase 2 + US1 (登録) → validate `add` end-to-end (this yields a usable MVP)
- Incremental Delivery: After MVP, implement US2/US3/US4 to reach full P1 coverage, then US5/US6 and polish.

## Validation

- All tasks follow the checklist format required: checkbox, TaskID (sequential), optional `[P]`, story label for user story tasks, and file paths included where applicable.

---

Generated by speckit.tasks based on `specs/1-todo-weather-cli` documents.
