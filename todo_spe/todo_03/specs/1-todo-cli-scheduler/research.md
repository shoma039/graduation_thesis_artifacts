# Research: Todo CLI Scheduler (Phase 0)

Decision: Implement as a local, single-user Python CLI tool using a JSON file for persistence.

Rationale:
- Python is widely available on user machines and has strong date/time and HTTP libraries, which speeds implementation.
- Single-file JSON persistence is simple, debuggable, and matches user's preference for a local CLI tool.
- Use of API-keyless services for geocoding and weather avoids requiring users to register API keys.
- Libraries chosen (`dateparser`, `zoneinfo`/stdlib, `requests`, `rich`) support Japanese outputs and human-friendly CLI UX.

Alternatives considered:
- SQLite: more robust indexing and transactions, but higher implementation complexity for this initial scope.
- Full cloud sync: out-of-scope for MVP due to auth and privacy concerns.

Technical Choices (short):
- Language: Python 3.11
- CLI UX: `rich` for display, `questionary` (optional) for prompts
- Date parsing: `dateparser` (supports natural language, incl. Japanese)
- Time zones: stdlib `zoneinfo` (Python 3.9+) and `pytz` if needed for portability
- HTTP: `requests` (synchronous) for simplicity
- Geocoding: Use an API-keyless public geocoding endpoint (e.g., Nominatim/OpenStreetMap) — respect rate limits and include a polite User-Agent
- Weather: Use an API-keyless weather API that supports hourly precipitation and temperature and accepts lat/lon + timezone parameters (e.g., Open-Meteo)
- Persistence: Local JSON file at `%APPDATA%\todo-cli-scheduler\tasks.json` (Windows) or `~/.local/share/todo-cli-scheduler/tasks.json` (cross-platform)

Risk & Mitigation:
- Public geocoding/weather endpoints have rate limits. Mitigation: cache geocoding results in the JSON file and back off on 429 responses.
- Natural language date parsing may be ambiguous. Mitigation: confirm parsed date with the user in the local timezone before saving.

Next steps (Phase 1):
- Generate `data-model.md` (entities + validation)
- Produce CLI contracts and a JSON Schema for tasks
- Create `quickstart.md` with install/run instructions
