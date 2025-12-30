# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

対話的な Python 製 CLI Todo アプリを実装する。主要要求は「期限内に天候の良い日を自動で候補日として提案する」ことで、都市名から緯度経度とタイムゾーンを取得し、期限内の降水確率と気温を評価して最適日を選定する。データはローカルに保持し、完了したタスクは削除する。優先度競合は作成日時の先着順で解決する。

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (または 3.10+)  
**Primary Dependencies**: `requests`, `dateparser`, `typer`（CLI 補助）, `python-dateutil`（補助）, 標準 `zoneinfo` でタイムゾーン処理  
**Storage**: SQLite（組み込み `sqlite3`）をメイン、軽量な JSON バックアップをオプションで提供  
**Testing**: `pytest`（単体・統合テスト）  
**Target Platform**: クロスプラットフォーム CLI（Windows PowerShell / macOS / Linux）  
**Project Type**: 単一 Python パッケージ（`src/` 配下に CLI とサービス層）  
**Performance Goals**: 単一ユーザー向けローカルツール。レスポンスは対話的に 1 秒未満を目指す（API呼び出しを除く）。  
**Constraints**: 外部 API は API キー不要の公開 API のみを使用（例: Open-Meteo のジオコーディング/天気）。  
**Scale/Scope**: 個人利用・小規模チームのデスクトップ利用を想定（同時ユーザーは想定しない）。

## Constitution Check

憲法テンプレートがプロジェクトに存在するがプレースホルダのままのため、本機能は以下の原則に従うことを仮定して進める: ローカル中心、ユーザーデータは外部に送らない、テストカバレッジを重視する。憲法ファイル自体は将来的な承認が必要だが、現段階での設計上の重大な違反は見られないため Phase 0 を進める（要改善: ` .specify/memory/constitution.md` を正式化すること）。

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

**Structure Decision**: 単一プロジェクト構成を採用。

src/
- models/            # データモデル定義
- services/          # ジオコーディング、天気取得、候補日ロジック
- cli/               # Typer ベースの CLI エントリポイント
- db/                # DB ラッパー（SQLite）

tests/
- unit/
- integration/

（詳細は Phase1 の `data-model.md` と `contracts/cli_contract.md` に記載）

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
