# Usage

Quick examples for the Todo CLI (Japanese output):

- Add a task with natural-language due date (parsed in the location timezone):

```bash
python -m src.cli.main todo add --title "買い物" --location "札幌" --due "明日 10時"
```

- List tasks:

```bash
python -m src.cli.main todo list
```

- Show a task by ID:

```bash
python -m src.cli.main todo show 1
```

- Calendar view for December 2025:

```bash
python -m src.cli.main todo calendar --month 2025-12
```

Notes:
- Geocoding and weather use Open-Meteo APIs (no API key required).
- Due date parsing is done using `dateparser` and interpreted in the resolved location timezone when available.
- Forecasts are cached in the local SQLite DB (`forecasts` table) to avoid excessive network calls.
