# CLI Commands (Contracts)

Each command describes input, behavior, and expected output (human-readable + optional JSON flag).

- `todo add`  
  - Input: title (required), --deadline (natural language), --location (city name), --priority (高|中|低)
  - Behavior: validate inputs; geocode location; fetch forecast for deadline window; pick candidate date; save task
  - Output: success message with Task ID and chosen candidate date; on `--json` output JSON object of task

- `todo list`  
  - Input: optional `--month YYYY-MM` or `--all`
  - Behavior: list tasks sorted by deadline (or month view); show candidate date, precip probability, temp
  - Output: human table (rich). `--json` outputs array of tasks

- `todo show <id>`
  - Input: task id
  - Behavior: display full details including forecast samples for candidate date
  - Output: detailed human-readable block or JSON

- `todo update <id>`
  - Input: fields to update (--title, --deadline, --location, --priority)
  - Behavior: validate, re-run geocode/forecast logic if needed, recompute candidate date, save
  - Output: updated task info

- `todo complete <id>`
  - Input: task id
  - Behavior: mark complete and delete record
  - Output: confirmation

- `todo calendar --month YYYY-MM`
  - Input: month
  - Behavior: show calendar for month with task and candidate date details (precip/temp in day cells)
  - Output: calendar rendering in terminal

- `todo migrate` (optional)
  - Input: none
  - Behavior: apply DB migrations (create tables)
  - Output: result

Notes:
- All commands accept `--json` flag to output machine-readable JSON for scripting.
- Error handling: on invalid input return non-zero exit code and human-friendly Japanese error message. With `--json` include `{"error": "message"}` structure.
