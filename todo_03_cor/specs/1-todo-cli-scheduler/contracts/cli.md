# CLI Contract: Todo CLI Scheduler

Commands (human-friendly):

- `todo add` — 新しいタスクを対話的に登録
  - Flags: `--title <text>` `--due "<natural date>"` `--priority {high,medium,low}` `--location "Tokyo"`
  - Behavior: 期限は自然言語で入力可能。保存前に解析結果を表示し、ユーザーに確認を求める。

- `todo list` — タスクを一覧表示（デフォルトは未完了）
  - Flags: `--all` (完了も含める), `--sort {due,priority,created}`

- `todo show <id>` — タスク詳細を表示（候補日、天気情報含む）

- `todo update <id>` — タスクを更新（タイトル・期限・優先度・場所など）

- `todo complete <id>` — タスクを完了にする（完了時に削除されるため一覧から消える）

- `todo delete <id>` — タスクを削除（確認プロンプトあり）

- `todo calendar [YYYY-MM]` — 指定月のカレンダー表示。省略時は当月。
  - Behavior: 日付セルに該当タスクの候補日/期限を表示。月切替可能。

Behavior Contracts

- Geocoding: When user provides `--location`, tool must resolve to `latitude`, `longitude`, and `timezone`. On failure, return clear Japanese error and ask to re-enter.
- Weather-based candidate selection: On `add`/`update`, after geocoding, fetch weather for the date range (today..due_date) and pick the date with minimal precipitation probability that doesn't conflict with other tasks' candidate dates. If none found, propose next available empty date and present precipitation and temperature.
- Timezone: All date calculations must use the resolved location's IANA timezone.
