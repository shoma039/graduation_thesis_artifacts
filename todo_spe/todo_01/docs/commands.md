# コマンド参照

このCLIの主要コマンド一覧です。

- `todo add --title <タイトル> [--due <期限>] [--priority <高|中|低>] [--location <場所>]`
  - タスクを追加します。`--due` は日本語表現や ISO 形式を受け付けます。

- `todo list`
  - 期限順にタスクを一覧表示します。

- `todo show <id>`
  - 指定IDのタスク詳細を表示します。

- `todo update <id> [--title <タイトル>] [--due <期限>] [--priority <高|中|低>]`
  - タスクの一部フィールドを更新します。

- `todo complete <id>`
  - タスクを完了として削除します（バックアップは保存されます）。

- `todo delete <id>`
  - タスクを削除します。

- `todo calendar [YYYY-MM]`
  - 指定月のカレンダーを表示します（省略時は今月）。

ドキュメント: README.md と quickstart を参照してください。
