# Implementation Plan: todo-weather-cli

**Branch**: `1-todo-weather-cli` | **Date**: 2025-12-10 | **Spec**: `spec.md`
**Input**: Feature specification from `specs/1-todo-weather-cli/spec.md`

## Summary

CLIベースのローカルTodo管理ツール。日本語で対話的にタスクを登録・更新・表示・削除でき、場所に基づく天気予報（降水確率・気温）を用いて期限内の最適な候補日を自動提案する。永続化は単一JSONファイルを用い、候補日は既存の候補日と重複しないように割り当てる（FIFO競合解決）。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- `click` (CLI)
- `prompt-toolkit` (対話入力、任意)
- `requests` (HTTP)
- `geopy` (Nominatim 経由のジオコーディング)
- `dateparser` (日本語含む自然言語日時パース)
- `timezonefinder` (緯度経度→IANAタイムゾーン)
- `filelock` (JSON書き込みの排他制御)
**Storage**: 単一JSONファイル（デフォルト: `%USERPROFILE%\.todo_weather_cli\tasks.json`）
**Testing**: `pytest` を想定（ユニット/統合）
**Target Platform**: ローカルPC（Windows/Mac/Linux）、PowerShell ターミナル想定
**Project Type**: Single CLI project
**Performance Goals**: 候補日選定はタスク単位で10秒以内（ネットワーク遅延を含む目安）
**Constraints**: APIキー不要の外部サービスを利用する（Nominatim, Open-Meteo 等）
**Scale/Scope**: 単一ユーザーのローカル利用を想定（数百〜数千件のタスク想定だが大量データは非想定）

## Constitution Check

GATE: 本プロジェクトはリポジトリの憲章に対して重要な違反を持たないことを確認する必要があります。

- **CLI Interface**: 準拠 — 全機能がCLIで提供される設計。
- **Test-First**: 準拠（計画内で`pytest`テストケースの作成を必須とする）。
- **Simplicity / YAGNI**: 準拠 — 機能はローカル単一ユーザー向けに限定。
- **Observability / Logging**: 準拠 — エラーメッセージは日本語で明確に提示し、内部ログはデバッグ向けに保管する方針。

注: リポジトリの `constitution.md` はテンプレート的なプレースホルダが含まれているため、一部のガバナンス要件が曖昧です。現時点で致命的な違反は見当たりませんが、組織固有の規則がある場合は追加確認が必要です（NEEDS CLARIFICATION）。

## Project Structure

```
src/
├── cli/                # CLI entrypoints (click commands)
├── models/             # dataclasses / schema
├── services/           # geocoding, weather, timezone services
├── storage/            # JSON read/write + locking
├── scheduler/          # 候補日選定アルゴリズム
└── utils/              # common utilities (parsing, formatting)

tests/
├── unit/
└── integration/

docs/
```

## Phase 0: Research (completed)

- `research.md` を作成し、`dateparser`, `geopy(Nominatim)`, `Open-Meteo`, `timezonefinder`, `filelock` を推奨とする決定を行いました。APIキーが不要な外部サービスを前提とします。

## Phase 1: Design & Contracts (completed)

- `data-model.md`, `contracts/cli-commands.md`, `quickstart.md` を作成済み。エッジケースと受け入れ基準を明確化しました。

## Phase 2: Implementation (plan)

1. リポジトリの雛形作成
   - `src/` 構造を作成し、`cli` エントリポイントを追加
   - `pyproject.toml` または `requirements.txt` を作成
2. ストレージ層実装
   - JSON ストア、`filelock` を用いた排他制御、ID発行ロジック
   - 単体テスト
3. サービス層実装
   - ジオコーディング（`geopy` + Nominatim） + キャッシュ
   - タイムゾーン決定（`timezonefinder`）
   - 天気取得（Open-Meteo）と日別集計ロジック
4. 候補日選定アルゴリズム実装
   - 期限内の日別降水確率・気温取得 → スコアリング → 候補日決定
   - 候補日の重複チェック（FIFOポリシーに従う）
5. CLI 実装
   - `追加`, `一覧`, `詳細`, `更新`, `完了`, `削除`, `カレンダー` コマンド
6. テスト作成
   - 50件の日本語日時テストケース（`dateparser`の検証）
   - サービスのモックによる統合テスト
7. ドキュメントと Quickstart の最終化

## Acceptance Criteria

- 既定の受け入れ基準（`spec.md`）を満たすこと。特に日付パースの正確性、候補日の重複回避、カレンダー表示の可読性をテストで担保する。

## Risks & Mitigations

- Nominatim の利用制限: キャッシュとユーザーの選択UIを実装。商用/高頻度は別サービスを推奨。
- 日付パースの不完全性: テストで代表ケースを網羅し、必要に応じて補助ルールを追加。
- タイムゾーン/夏時間の誤差: `timezonefinder` と APIのtimezoneを二重チェックする。

## Complexity Tracking

None required at this stage.

---

Plan prepared by: speckit plan generator
