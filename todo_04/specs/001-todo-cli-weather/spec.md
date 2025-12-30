```markdown
# Feature Specification: Todo CLI — 天気連動スケジューリング

**Feature Branch**: `001-todo-cli-weather`  
**Created**: 2025-12-10  
**Status**: Draft  
**Input**: User description: "Pythonで、CLI上で対話的に実行できるTodoリストアプリを作成したい。基本的な機能として登録・一覧・詳細・更新・削除の設定を入れる。タスクにはIDとタイトルと完了の有無、優先度（三段階）、場所、期限の情報を持たせる。日付入力時、「明日」「来週の月曜」といった言葉でも正確に登録できるようにする。外部の天気予報を使用し、登録した場所の降水確率によって、期限内で最適な日を天気で選択する。選択した日はタスクに候補日として登録する。候補日はほかのタスク候補日と被らないようにする。期限内で最適な日がない場合、空いている日に予備の日程を提案するまた気温も表示する。タスクを更新して完了となったらそのタスクは削除すること。カレンダー機能を追加して、登録したものを日付順で見やすくして月も選べるようにする。期限の扱い、天気APIの日時の処理などは、場所のタイムゾーンを用いて正しく変換すること。天気予報を正確に取得するために都市名を入力したら自動でGPS（緯度・経度）に変換して保存すること。外部APIには、APIキー登録不要なものを使用する。不正入力時はエラー表示する。出力は日本語で分かりやすいようにする."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - タスクの登録と自動候補日提案 (Priority: P1)

ユーザーは CLI で自然言語（日付表現：例「明日」「来週の月曜」「12/25」など）を使ってタスクを登録できる。登録時に場所（都市名）を入力すると自動で緯度経度が保存され、期限内で降水確率と気温を考慮して最適な候補日が1つ自動で提案され、タスクに候補日として登録される。

**Why this priority**: 本機能は天気連動スケジューリングのコアであり、ユーザーが価値を得る主要な流れであるため最優先。

**Independent Test**: CLI でタスクを登録し、出力に候補日（期限内・降水確率低い日）が含まれることを確認する。候補日は他タスクと重複しない。

**Acceptance Scenarios**:

1. **Given** 新規タスク登録フォーム、**When** ユーザーが「締切: 来週の月曜」「場所: 東京」と入力、**Then** 期限内で降水確率が低い日を候補日として表示・保存する。
2. **Given** 候補日が別タスクとぶつかる場合、**When** 自動選択処理が行われる、**Then** 衝突を避ける別の最適日を選ぶ（存在しない場合は予備日を提案する）。

---

### User Story 2 - 一覧・詳細・更新・完了操作 (Priority: P1)

ユーザーは登録済みタスクの一覧表示、タスク詳細確認、タスク内容の更新、タスク完了（完了時にタスクは削除される）の操作を行える。更新により候補日が再計算される。

**Why this priority**: 基本 CRUD は CLI アプリとして必須であり、運用上の要件。

**Independent Test**: タスクを登録→一覧で確認→詳細表示→更新で候補日が再計算される→完了で一覧から消える一連の流れを手動で実行して確認する。

**Acceptance Scenarios**:

1. **Given** タスクが存在、**When** `update` で期限または場所を変更、**Then** 新しい条件に基づいて候補日が更新される。
2. **Given** タスクが完了、**When** `complete` コマンドを実行、**Then** タスクは削除され一覧に表示されない。

---

### User Story 3 - カレンダー表示と月選択 (Priority: P2)

ユーザーはカレンダー表示を開き、指定月のタスクを日付順で見やすく確認できる。候補日はハイライト表示され、気温と降水確率も併記される。

**Why this priority**: スケジュール確認の利便性を高め、候補日の視認性を向上するため。

**Independent Test**: `calendar --month YYYY-MM` コマンドで指定月の一覧が日付順で表示され、各日付にタスクと候補日の情報（降水確率・気温）が含まれることを目視で確認する。

**Acceptance Scenarios**:

1. **Given** 複数タスクが同月に存在、**When** 指定月でカレンダー表示、**Then** 日付順にタスクが並び、候補日は明確に表示される。

---

### Edge Cases

- ユーザーが認識不能な日付表現を入力した場合 → 明確なエラーメッセージを返し再入力を促す。
- 指定した都市名が曖昧で複数候補が返る場合 → 候補リストを表示してユーザーに選ばせる。
- 期限が短すぎて候補日が存在しない場合 → 空いている最短日（期限後にならない範囲で最も近い空き日）を「予備日」として提案する。
- 天気 API のデータが取得できない/一部欠損している場合 → ユーザーに通知し、候補日ロジックは降水データがある日を優先、ない場合は気温または空き日を基準に提案する。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI でタスクの作成（タイトル、期限、場所、優先度(高/中/低)）ができること。期限は自然言語で入力可能。
- **FR-002**: 作成時に指定した都市名をジオコーディングして緯度・経度・タイムゾーン情報を保存できること。
- **FR-003**: 保存した位置情報を用い、期限内の各日について当該地点の降水確率と気温を取得して候補日を1つ選定しタスクに保存すること。
- **FR-004**: 選ばれた候補日は既存タスクの候補日と被らないように調整すること（衝突が発生する場合は次善の候補日を選ぶ）。
- **FR-005**: 期限内に天候条件を満たす日が存在しない場合、ユーザーに対して「予備日」を提示する機能を持つこと。
- **FR-006**: タスクの一覧表示、詳細表示、編集（期限/場所/優先度の変更）、削除（完了時の削除を含む）ができること。編集時は候補日の再計算を行う。
- **FR-007**: カレンダー表示で月単位を選択し、日付順にタスクと候補日（降水確率・気温）を表示できること。
- **FR-008**: 日付・場所入力に不正があれば明確なエラーメッセージを表示すること。

### Key Entities *(include if feature involves data)*

- **Task**: id, title, priority (高/中/低), location_id, deadline (UTC 保存だがローカル変換可), candidate_date, status (open/complete)
- **Location**: id, user_input_name, latitude, longitude, timezone
- **ForecastSample**: date (local), precipitation_probability (%), temperature_celsius

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 日付の自然言語入力（主要な日本語表現 50 ケース想定）のうち、95%以上を正しく解釈して内部期限に変換できること（自動テストで検証可能）。
- **SC-002**: 新規登録タスクのうち、期限内に候補日が自動提案される割合が >= 90%（天候データが入手可能な場合に限定して測定）。
- **SC-003**: 候補日提案で他タスクと重複する割合が <= 5%（衝突回避ロジックで解消されることを期待）。
- **SC-004**: カレンダー表示で指定月のタスク一覧を読みやすく表示でき、主要操作（登録→一覧→詳細→完了）がユーザーテストで平均 3 分以内に完了すること。

## Assumptions

- 天気とジオコーディングは「APIキー不要で利用可能な公開 API」を利用する（例: 実装候補として Open-Meteo 等を推奨するが、実装選定は開発チームに委ねる）。
- タイムゾーンの扱いは保存時に明示的に location のタイムゾーンを紐付け、表示/計算時にローカルに変換することで行う。
- 優先度のデフォルトは「中」とする。
- 候補日の選定基準は「降水確率を最小化」→同率の場合は「気温が適度（極端な低/高でない）」→それでも同じならユーザーに選択肢を提示する、という優先順位を採る。

## Test Cases / Acceptance Tests

- 日付入力テスト: 50 個の日本語表現を用意し、正しく内部期限に変換されることを自動テストで確認する。
- ジオコーディングテスト: 都市名の曖昧性（同名複数候補）に対する候補表示・選択フローを手動テストで確認する。
- 候補日選定テスト: モック天気データを用いて複数ケース（候補あり・候補なし・衝突発生）を検証する。
- カレンダーテスト: 複数タスクを登録して月表示が正しく日付順に並ぶことを確認する。

## Notes

- 本仕様は WHAT（ユーザーの要望と受け取る入力、期待する振る舞い）に重点を置き、具体的な実装言語やフレームワーク、永続化方式は含めない。
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
