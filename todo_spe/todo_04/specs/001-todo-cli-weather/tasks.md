---
description: "Task list for Todo CLI — 天気連動スケジューリング"
---

# Tasks: Todo CLI — 天気連動スケジューリング

**Input**: Design documents from `specs/001-todo-cli-weather/` (`spec.md`, `plan.md`, `data-model.md`, `contracts/`, `research.md`)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: プロジェクト初期化と基本構造の作成

- [x] T001 Create project structure and placeholder files in `src/`, `tests/`, `docs/` (create `src/cli`, `src/models`, `src/services`, `src/storage`, `src/util`, `tests/unit`, `tests/integration`, `docs/`)
- [x] T002 Create `requirements.txt` and `pyproject.toml` at repository root (`requirements.txt`, `pyproject.toml`)
- [x] T003 [P] Add `README.md` and `specs/001-todo-cli-weather/quickstart.md` (update if needed) (`README.md`, `specs/001-todo-cli-weather/quickstart.md`)
- [x] T004 [P] Add basic CLI entrypoint `src/cli/__main__.py` and package `src/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 永続化・モデル・共通サービスなど、すべてのユーザーストーリーに必要な基盤

**⚠️ CRITICAL**: このフェーズ完了まではユーザーストーリー作業は開始できません

- [x] T005 Setup SQLite database schema and migration script `src/storage/migrations.py` and migration runner `src/storage/migrate.py`
- [x] T006 [P] Implement storage wrapper `src/storage/db.py` (connection, simple CRUD helpers)
 - [x] T007 [P] Create data models: `src/models/task.py` (Task model according to `data-model.md`)
 - [x] T008 [P] Create data models: `src/models/location.py` (Location model)
 - [x] T009 [P] Create data models: `src/models/forecast.py` (ForecastSample model / cache)
 - [x] T010 Implement timezone and date utilities `src/util/date_utils.py` (UTC/local conversion, ISO formatting)
 - [x] T011 Implement input validation and errors module `src/util/errors.py` (日本語エラーメッセージ)
- [x] T012 [P] Implement geocoding service `src/services/geocode.py` (Nominatim via `geopy` or direct HTTP; cache into Location table)
- [x] T013 [P] Implement weather service `src/services/weather.py` (Open-Meteo calls, returns precipitation probability and temperature per local date)
 - [x] T014 Implement forecast cache service `src/services/forecast_cache.py` (store `ForecastSample` rows and re-use to respect rate limits)

**Checkpoint**: Foundation complete — DB と基本サービスが使える状態

---

## Phase 3: User Story 1 - タスクの登録と自動候補日提案 (Priority: P1) 🎯 MVP

**Goal**: CLI から自然言語でタスクを登録し、ジオコーディング・天気を用いて期限内の最適候補日を自動で選定して保存する

**Independent Test**: `python -m src.cli add` でタスクを登録し、出力に候補日が含まれること（候補日は他タスクと重複しない）

### Tests (integration)

- [x] T015 [P] [US1] Integration test `tests/integration/test_add_and_schedule.py` (モック geocode/weather を用いた end-to-end)

### Implementation

- [x] T016 [P] [US1] Implement natural language date parsing wrapper `src/services/date_parser.py` (uses `dateparser` configured for Japanese)
- [x] T017 [P] [US1] Implement scheduling service `src/services/scheduler.py` (候補日選定ロジック: 降水確率最小化 → 気温で補正 → 衝突回避)
- [x] T018 [US1] Implement CLI `add` command handler `src/cli/commands/add.py` (validate inputs, call geocode/weather/scheduler, save task)
- [x] T019 [US1] Persist candidate date and chosen forecast metadata to DB (`src/models/task.py` save logic / `src/services/scheduler.py` persistence)
- [x] T020 [US1] Add user-friendly Japanese output and `--json` support for `add` (`src/cli/commands/add.py`)
- [x] T021 [US1] Implement conflict avoidance: when chosen date collides with existing tasks' candidate_date, scheduler must choose next-best date or propose a予備日 (implement in `src/services/scheduler.py`)

**Checkpoint**: User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - 一覧・詳細・更新・完了操作 (Priority: P1)

**Goal**: タスクの一覧、詳細、更新、完了（完了で削除）を CLI で操作できる

**Independent Test**: 登録→一覧→詳細→更新（候補日再計算）→完了の一連を手動・統合テストで確認可能

### Tests

- [x] T022 [P] [US2] Integration test `tests/integration/test_crud.py` (登録→更新→完了のシナリオ)

### Implementation

- [x] T023 [P] [US2] Implement CLI `list` command `src/cli/commands/list.py` (並び順: 期限順、`--month` フィルタ対応)
- [x] T024 [US2] Implement CLI `show` command `src/cli/commands/show.py` (詳細＋候補日の気温/降水確率を表示)
- [x] T025 [US2] Implement CLI `update` command `src/cli/commands/update.py` (期限/場所/優先度の変更、変更時に候補日を再計算)
- [x] T026 [US2] Implement CLI `complete` command `src/cli/commands/complete.py` (完了時にタスクを削除し確認メッセージを表示)
 - [x] T027 [US2] Ensure JSON output (`--json`) and proper non-zero exit codes on errors (`src/cli/commands/*.py`)

**Checkpoint**: US1 と US2 が独立して動作することを確認

---

## Phase 5: User Story 3 - カレンダー表示と月選択 (Priority: P2)

**Goal**: 月指定でカレンダー表示を行い、各日付にタスクと候補日の降水確率・気温を併記する

**Independent Test**: `python -m src.cli calendar --month YYYY-MM` で視覚的に確認できる

### Tests

 - [x] T028 [P] [US3] Integration test `tests/integration/test_calendar.py` (モック forecast を用いてカレンダー出力の主要要素を検証)

### Implementation

- [x] T029 [P] [US3] Implement calendar command `src/cli/commands/calendar.py` (レンダリングは `rich` を利用)
 - [x] T030 [US3] Integrate forecast display into calendar cells (precip% / temp)
- [x] T031 [US3] Implement month navigation and graceful handling of empty months (`src/cli/commands/calendar.py`)

**Checkpoint**: カレンダー機能が動作し、候補日と天気情報が表示される

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: ドキュメント、エラーハンドリング、ロギング、パッケージング等の横断的改善

- [ ] T032 [P] Documentation updates: `docs/README.md`, `docs/usage.md`, update `specs/001-todo-cli-weather/quickstart.md`
- [ ] T033 Logging and structured error messages `src/util/logging.py` / improve `src/util/errors.py`
- [ ] T034 [P] Add CI workflow for tests (create `.github/workflows/ci.yml` to run `pytest`)
- [ ] T035 Packaging and entrypoint: finalize `pyproject.toml` and expose `todo` CLI entry
- [ ] T036 [P] Add basic unit tests in `tests/unit/` for utility functions (date parsing, timezone conversion)

- [x] T032 [P] Documentation updates: `docs/README.md`, `docs/usage.md`, update `specs/001-todo-cli-weather/quickstart.md`
- [x] T033 Logging and structured error messages `src/util/logging.py` / improve `src/util/errors.py`
- [x] T034 [P] Add CI workflow for tests (create `.github/workflows/ci.yml` to run `pytest`)
- [x] T035 Packaging and entrypoint: finalize `pyproject.toml` and expose `todo` CLI entry
- [x] T036 [P] Add basic unit tests in `tests/unit/` for utility functions (date parsing, timezone conversion)

---

## Dependencies & Execution Order

- **Phase 1 (Setup)**: 開始可能（T001..T004）
- **Phase 2 (Foundational)**: Phase1 完了後開始（T005..T014） — すべてのユーザーストーリーをブロック
- **User Stories (Phase 3+)**: Phase2 完了後に開始可能。US1 (T016..T021) は MVP。US2 と US3 はそれぞれ独立して進められる。

### Story-level Dependencies

- **US1 (P1)**: 依存: T005..T014 の完了。出力の検証は `tests/integration/test_add_and_schedule.py` で行う。
- **US2 (P1)**: 依存: Foundation。US1 と独立して進められるが、共有モデルを利用する。
- **US3 (P2)**: 依存: Foundation。カレンダーは表示上の機能のため、US1/US2 完了前でも開発可能だがテストは実データで行う。

## Parallel Execution Examples

- モデル作成は並列化可能: `T007`, `T008`, `T009` は `[P]` として同時に進められます。
- サービス作成の一部は並列可能: `T012` (geocode) と `T013` (weather) は独立して実装できる。
- CLI コマンドは別々のファイルに実装するので `T018`, `T023`, `T024`, `T025`, `T026`, `T029` は並列で作業可能（ただし DB/サービスインターフェースは安定している必要あり）。

## Implementation Strategy

- MVP (優先): US1 (タスク登録 + 自動候補日) を最初に完成させ。
  1. Setup (Phase1)
  2. Foundational (Phase2)
  3. US1 実装 & 統合テスト (T015..T021)
  4. デモ／検証
- インクリメンタル配信:
  - 次に US2 を追加して CRUD を揃える
  - 最後に US3（カレンダー）とポリッシュ作業

## Validation: Each story has independent test criteria

- US1: `tests/integration/test_add_and_schedule.py` が成功すれば合格（候補日が期限内に選ばれ、他タスクと衝突しないこと）
- US2: `tests/integration/test_crud.py` が成功すれば合格（登録→更新→完了の流れ）
- US3: `tests/integration/test_calendar.py` が成功すれば合格（指定月のカレンダー表示に候補日・天気が含まれること）

---

## Files created/modified by these tasks (high-level)

- `src/cli/*`, `src/models/*`, `src/services/*`, `src/storage/*`, `src/util/*`
- `tests/integration/*`, `tests/unit/*`
- `requirements.txt`, `pyproject.toml`, `.github/workflows/ci.yml`

---

Implementation notes:
- Use API-key-free services: Nominatim (geocoding) and Open-Meteo (forecast). Cache results to respect rate limits.
- Convert all deadlines to UTC for storage and use `Location.timezone` for local calculations and display.
- Prefer small, testable functions in `src/services/scheduler.py` to allow deterministic unit tests (mock weather responses).
