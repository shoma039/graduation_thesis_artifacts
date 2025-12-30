# Feature Specification: Todo リスト（天気連動スケジューラ）

**Feature Branch**: `001-todo-weather-scheduler`  
**Created**: 2025-12-10  
**Status**: Draft  
**Input**: User description: "Pythonで、CLI上で対話的に実行できるTodoリストアプリを作成したい。基本的な機能として登録・一覧・詳細・更新・削除の設定を入れる。タスクにはIDとタイトルと完了の有無、優先度（三段階）、場所、期限の情報を持たせる。日付入力時、「明日」「来週の月曜」といった言葉でも正確に登録できるようにする。外部の天気予報を使用し、登録した場所の降水確率によって、期限内で最適な日を天気で選択する。選択した日はタスクに候補日として登録する。候補日はほかのタスク候補日と被らないようにする。期限内で最適な日がない場合、空いている日に予備の日程を提案するまた気温も表示する。タスクを更新して完了となったらそのタスクは削除すること。カレンダー機能を追加して、登録したものを日付順で見やすくして月も選べるようにする。期限の扱い、天気APIの日時の処理などは、場所のタイムゾーンを用いて正しく変換すること。天気予報を正確に取得するために都市名を入力したら自動でGPS（緯度・経度）に変換して保存すること。外部APIには、APIキー登録不要なものを使用する。不正入力時はエラー表示する。出力は日本語で分かりやすいようにする。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - タスク登録（優先度・場所・期限付き）（Priority: P1）

ユーザーはCLIで新しいタスクを登録できる。タスクにはID、タイトル、優先度（低/中/高）、場所（都市名）、期限を持つ。期限は自然言語（例：「明日」「来週の月曜」「来月の10日」）で入力でき、正確に日付へ変換される。

**Why this priority**: 基本操作であり、本機能全体の基礎となるため。

**Independent Test**: 新規登録コマンドを実行し、一覧で該当タスクが表示され、詳細でフィールドが正しく保存されていることを確認する。

**Acceptance Scenarios**:
1. **Given** CLIが起動している、**When** `add` コマンドでタイトル・期限・場所を入力、**Then** タスクが作成されIDが返り、一覧に表示される。
2. **Given** 期限に自然言語を入力、**When** 保存、**Then** タスクの期限フィールドがその都市のタイムゾーンに基づく正しい日付に変換される。

---

### User Story 2 - 天気をもとに候補日を自動選択（Priority: P1）

ユーザーがタスク登録時または登録後に「天気で候補日を決める」を選択すると、期限内で降水確率が最も低い日（かつ空き日の優先）を候補日として提案する。候補日は他タスクと被らないように調整される。

**Why this priority**: ユーザーが天候を考慮した実行日を欲しているため、コア機能。

**Independent Test**: テスト用の都市と期限範囲を与え、天気データ（モック可）で最適日が候補として登録され、重複が避けられていることを確認する。

**Acceptance Scenarios**:
1. **Given** タスクAとタスクBがあり、両方未割当の候補日が同じ暦日で最適な場合、**When** 候補日生成を行う、**Then** タスク同士で候補日衝突がないよう自動で振り分ける。
2. **Given** 期限内に降水確率が低い日が存在しない場合、**When** 候補日生成を行う、**Then** 空いている別日を予備候補として提示し、その日の期待気温も表示する。

---

### User Story 3 - タスクの一覧・詳細・更新・削除（Priority: P1）

ユーザーはタスクの一覧（カレンダー表示含む）、詳細確認、編集、削除（完了時に自動削除）を行える。

**Why this priority**: CRUD操作は不可欠。

**Independent Test**: 既存タスクを更新して完了にすると一覧から消えることを確認する。カレンダー表示で日付順に並び、月指定で閲覧できることを確認する。

**Acceptance Scenarios**:
1. **Given** タスクが存在、**When** `complete` コマンドで完了にする、**Then** タスクは削除され一覧に表示されない。
2. **Given** 複数タスクがある、**When** カレンダーを月表示で指定、**Then** その月のタスクが日付順で見やすく表示される。

---

### Edge Cases

- 無効な日付入力（例：存在しない日、曖昧な表現）はエラー表示され、再入力を促す。
- 都市名が曖昧（例：「東京」以外に複数候補がある場合）は候補リストを提示して選択させる。
- 同一日の複数タスク候補が膨大になったときの調整（優先度・期限の近さで分配）を行う。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI上でタスクを作成できる（ID, タイトル, 完了フラグ, 優先度(低/中/高), 場所(都市名), 期限）。
- **FR-002**: 期限は自然言語（例：「明日」「来週の月曜」）入力を受け付け、正確な日付に変換する。
- **FR-003**: 都市名を入力すると自動で緯度/経度（GPS）とタイムゾーン情報を取得して保存する。
- **FR-004**: 外部天気データ（APIキー不要のサービス）を用いて、期限内で降水確率が最も低い日を候補日として提示・登録する。
- **FR-005**: 候補日は他のタスクの候補日と被らないように調整される（自動再配置ルールを適用）。
- **FR-006**: 期限内に最適日が無い場合、空き日を候補として提示し、当日の予想気温も表示する。
- **FR-007**: タスクが完了に更新されたら、そのタスクは一覧から削除される（履歴保持は別機能）。
- **FR-008**: カレンダー表示機能を提供し、月指定で日付順にタスクを表示する。
- **FR-009**: 外部APIの日時や予報は、タスクの登録地点のタイムゾーンを用いて正しく解釈・表示する。
- **FR-010**: 入力検証を行い、不正入力時は日本語でわかりやすいエラーメッセージを表示する。

### Key Entities *(include if feature involves data)*

- **Task**: id, title, completed:boolean, priority:{low,medium,high}, place:{name,lat,lon,timezone}, deadline:datetime, candidate_dates:[date], created_at, updated_at
- **CandidateDate**: date, associated_task_id, is_confirmed:boolean, expected_precipitation_rate, expected_temperature
- **Location**: display_name, lat, lon, timezone

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ユーザーがタスク登録を開始してから登録完了までの操作が3ステップ以内で完了できること。
- **SC-002**: 期限の自然言語入力のうち少なくとも95%が期待通りのカレンダー日付に正しく解釈される（テストケースで検証）。
- **SC-003**: 候補日生成において、候補日の重複が生じない（自動調整ロジックで衝突を解消できる）こと。
- **SC-004**: カレンダー表示で月指定した際に、該当月のタスクが日付順で表示されること（視認性の確認）。
- **SC-005**: 不正入力に対して、意味のある日本語のエラーメッセージが返されること（テストケースで網羅率80%以上）。

## Assumptions

- 自然言語の期限解釈はローカルの言語（日本語）に最適化される。曖昧な表現は最も自然な解釈を採る。
- 外部の天気およびジオコーディングAPIはAPIキー不要のサービスを利用する想定（具体的なプロバイダ名は実装注記に移動）。ただし仕様自体はAPIプロバイダ非依存で記述する。
- 履歴保存（完了タスクのアーカイブ）は本仕様に含めない（別機能）。

## Implementation Notes (非必須・参考)

- 候補日調整ルールの優先順位例：1) 降水確率低い 2) 空き日 3) 優先度/期限の近さ
- 都市名の曖昧さがある場合はユーザーに候補を選ばせるUIを実装する。

### 実装注記（例）

- 実装時の参考プロバイダ（仕様上は必須ではない、実装注記として記載）: Open-Meteo（天気）, OpenStreetMap/Nominatim（ジオコーディング）。いずれもAPIキー不要で利用可能だが、利用規約やレート制限に注意すること。

### 候補日衝突解消ルール（受け入れ基準）

- 目的: 候補日が複数タスクで重複しないよう自動で調整する。以下は明確な受け入れ基準で、テスト可能であること。

1. 初期割当: 候補日生成アルゴリズムは期限範囲内のカレンダー日ごとに降水確率の低い順で日をソートする。各日について、その日を候補とするタスクが複数ある場合は「先に登録された（作成日時が古い）タスクを優先」して割り当てを行う。
2. タイブレーク（同等条件）: 上記の登録順で解決できない場合（例: 作成日時が一致する特殊ケース）は、次の順で判断する: 1) 優先度（高→低）、2) 期限の近さ（近いものを優先）。
3. 再配置上限: 割当で衝突が発生した場合、システムは最大3回まで別の日に再配置を試みる（期限範囲内）。3回試行しても割当不能な場合は、ユーザーに手動選択を促す通知を表示する（エラーメッセージ/提案）。
4. 代替候補表示: 期限内に降水確率が十分に低い日が存在しない場合、最大3つの空き日を降水確率の低い順に提示し、それぞれの期待気温を表示する。
5. 再現性: 同じ入力データ（タスク一覧・天気データ）に対しては常に同じ割当結果を返すこと（決定論的アルゴリズム）。

これらのルールは `FR-005` のテストケースとして直接検証可能である。

---

**Prepared By**: specify-automation
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
