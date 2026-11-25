# Cyber Safety Quiz — HTML + Python only

A modular, zero-required-dependency local web application. The browser interface is plain semantic HTML forms and tables. **There is no JavaScript and no CSS**. Python handles every interaction, calculation, validation, storage operation and report.

## Requirements

- Python 3.10 or newer
- No mandatory third-party packages
- Optional: Matplotlib for PNG chart export (`python -m pip install matplotlib`)

## Run

1. Extract the ZIP.
2. Open a terminal in the extracted project directory.
3. Run `python app.py`.
4. Open `http://127.0.0.1:8000`.
5. Keep the terminal open. Press `Ctrl+C` to stop.

## Test

From the project directory run:

```bash
python -m unittest discover -s tests -v
```

The tests cover input validation, scoring, analytics, JSON persistence, corrupted-file recovery and report exports.

## Architecture

```text
Browser (plain HTML forms)
        |
        v
cyberquiz/webapp.py       HTTP routing and HTML presentation\n        services.py         application use cases and validated bulk import
        |
        +--> validation.py  central validation rules
        +--> questions.py   question bank and deterministic grading
        +--> analytics.py   aggregate metrics and trends
        +--> reports.py     CSV / Markdown / TXT / optional PNG
        +--> storage.py     repository and atomic JSON persistence
        +--> config.py      paths and operational limits
```

The HTTP layer is intentionally thin. Application use cases are in `services.py`; business rules do not depend on HTTP request objects. The storage layer is replaceable behind `JsonRepository`.

## Implemented capabilities

- Three knowledge areas: Password Safety, Phishing and Online Safety.
- Eight questions with answer explanations and category breakdown.
- Central validation for names, category values, answer count and answer ranges.
- JSON schema checks, malformed-file backup, thread lock and atomic temp-file replacement.
- Search, category filtering and server-side pagination.
- Executive metrics: attempts, average, best score, pass count/rate.
- Category and monthly trends.
- CSV, Markdown and plain-text report exports.
- Optional Matplotlib PNG chart export with graceful message when unavailable.
- Validated bulk CSV import (maximum 500 rows per upload).
- Defensive HTTP request size limit, same-origin check for form submissions, HTML escaping and security response headers.
- Localhost-only binding; no login/authentication is added because authentication is outside the project brief.

## Data and privacy

Results are stored in `data/records.json`; generated exports are placed in `exports/`. These folders are created automatically. This is a local educational demonstration, not a production security product. Do not enter real passwords, OTPs or sensitive personal information.

## Demo script

1. Start the server and open the home page.
2. Open Take Quiz. Submit with a blank name or missing answers to demonstrate server-side validation.
3. Complete the quiz. Review score, category breakdown and explanations.
4. Open Records. Search by name, filter category and navigate pages.
5. Open Analytics. Show aggregate metrics, category averages and monthly trends.
6. Open Reports and download CSV, Markdown and TXT reports.
7. Optionally install Matplotlib and download the PNG chart.
8. Import a small CSV with the documented headers; also try an invalid row to show row validation.
9. Stop and restart the server. Confirm the JSON-backed results remain available.

## CSV import format

```csv
name,score,total,date
Demo Student,6,8,2026-11-24
```

Imported legacy rows are validated and stored with a separate imported record identifier. Imported rows without category breakdown do not affect category averages.
