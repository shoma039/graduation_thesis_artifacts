# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (開発は Windows/macOS/Linux の CLI 向け)
**Primary Dependencies**:
- `dateparser` — 日本語を含む自然言語の日付パース
- `geopy` (Nominatim) または直接 Nominatim HTTP API — 都市名→緯度経度ジオコーディング（APIキー不要）
- `requests` — 天気/ジオコーディング API 呼び出し
- `open-meteo`（HTTP API） — API キー不要の天気予報（降水確率・気温）
- `rich` — CLI 表示（カラー、テーブル、カレンダー表示）
- `python-dateutil` / 標準 `zoneinfo` — タイムゾーンと日時処理
**Storage**: ローカル SQLite (`sqlite3` 組み込み) を初期選択。軽量で ACID 性能あり。将来的に移行可能。
**Testing**: `pytest` を想定。単体テスト + 統合テスト（外部 API はモック）
**Target Platform**: クロスプラットフォーム CLI（Windows PowerShell/コマンドプロンプト、macOS/Linux ターミナル）
**Project Type**: 単一 Python パッケージ（`src/` 配下に CLI 実行ファイル）
**Performance Goals**: ローカル CLI ツールのため厳密な RPS 指標は不要。応答は対話で数秒以内を目指す（API 呼び出し待ち時間に依存）。
**Constraints**:
- 天気とジオコーディングは API キー不要の公開サービスを利用する（例: Open-Meteo, Nominatim）。ただし利用規約（レート制限）に注意。
- 日付/時刻の計算は `location.timezone` を正しく用いて行うこと。
**Scale/Scope**: 個人または小規模チーム向けローカル CLI。データ量は数千タスク程度を想定。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution ファイルの内容がテンプレートのまま（項目が未定義）であるため、いくつかのガード項目は現在 "NEEDS CLARIFICATION" として扱います。以下は確認結果です。

- **Principles present**: NO — `.specify/memory/constitution.md` はテンプレートで具体化が必要 → **NEEDS CLARIFICATION**
- **CLI I/O ガイドライン**: NO — 期待される入出力フォーマット（JSON vs human-readable）が明確でない → **NEEDS CLARIFICATION**
- **テスト / 品質ゲート**: NO — TDD/統合テストの必須度が未定義 → **NEEDS CLARIFICATION**

GATE 結果: 現状は「CONSTITUTION による必須ゲートが未定義」であるため、Phase 0 の研究で「Constitution に合致する運用方針（最小セット）」を提案し、Gate を満たす予定です。未解決のまま進める場合は記録と承認が必要。

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

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]
**Structure Decision**: シンプルな単一パッケージ構成を採用します。

``text
src/
├── cli/                # CLI entrypoints and command handlers
├── models/             # DB model / data classes
├── services/           # geocoding, weather, scheduling logic
├── storage/            # sqlite wrapper and migration
└── util/               # date parsing, timezone helpers

tests/
├── unit/
└── integration/

docs/
├── quickstart.md
└── data-model.md
``

理由: 単一リポジトリで完結・導入が容易。CLI ツールとして配布しやすく、テストもローカルで容易に実行可能。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
