# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

軽量なPython製CLI Todoアプリを実装する。自然言語（日英含む）で期限を入力でき、都市名から自動で緯度経度とタイムゾーンを取得して保存する。期限内の降水確率と期待気温を外部天気APIから取得し、降水確率が低い日を候補日として自動割当する（候補重複は先に登録されたタスクを優先）。永続化はSQLiteを使い、テストはpytestで行う。外部APIはAPIキー不要なものを想定（実装注記に記載）。

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: `dateparser` (自然言語日付解析, 日本語対応), `httpx` (HTTPクライアント), `pytz`/`zoneinfo`（タイムゾーン処理）, `python-dateutil`（補助）  
**Storage**: SQLite（`sqlite3`）単一ファイル永続化  
**Testing**: `pytest`（ユニット/統合テスト）、簡易モックで天気/ジオコーディングを置換  
**Target Platform**: CLI（Windows PowerShell, Linux, macOSのターミナル）  
**Project Type**: single (CLI application)  
**Performance Goals**: ローカルCLIで小規模（数百〜数千タスク想定）、レスポンスは数秒以内  
**Constraints**: ネットワーク依存箇所（天気/ジオコーディング）はオフライン時にエラーハンドリングを行う  
**Scale/Scope**: 個人/小規模チーム向け（データ量は軽量）

## Constitution Check

GATE: Constitution ファイルはプレースホルダのため、明示的なガイドライン違反は無いと判断しました。よってフェーズ0に進行可能です。もし組織固有の要件（TDD必須等）があれば追記してください。

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: シンプルな単一プロジェクト構造を採用します（`src/` + `tests/`）。CLIエントリポイントは `src/cli/main.py`、モデルは `src/models/`、サービス（天気/ジオコーディング/スケジューラ）は `src/services/` に配置します。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
