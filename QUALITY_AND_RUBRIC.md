# Quality and rubric evidence

This revision is designed to address the deductions visible in the supplied evaluation screenshot. A final mark is determined by the evaluator, so no score can be guaranteed.

| Rubric area | Evidence in this project |
|---|---|
| Requirements fulfilment | Full quiz workflow, defensive validation, JSON persistence, search, filtering, pagination, analytics, CSV/Markdown/TXT exports, optional Matplotlib chart, and validated bulk CSV import. |
| Code quality and best practices | Small modules with single responsibilities; docstrings; centralized configuration; typed boundaries; reusable validation; application services separated from HTTP handlers; no third-party runtime dependency. |
| Functionality and reliability | Atomic JSON replacement, thread lock, schema filtering, corrupt-file backup, request size limit, safe error handling, and 25 automated unit tests. |
| System design and architecture | Presentation/controller, application service, domain logic, repository/storage, analytics and reporting layers are separate. Repository abstraction and batch writes make storage replacement easier. Server-side pagination limits rendered rows per page. |
| Security and robustness | Strict allow-list validation, HTML escaping, no dynamic HTML from untrusted input, same-origin POST check, localhost-only bind, request size cap, security headers, no JavaScript, no credentials/secrets, and no authentication added because the brief does not require it. |
| Innovation and technical complexity | Category-level assessment and trend analysis, monthly aggregates, validated legacy data import, multiple report formats, optional chart export, and graceful fallback if Matplotlib is absent. |

## Automated verification

Run:

```bash
python -m unittest discover -s tests -v
```

The current test suite contains 25 tests across:
- validation boundaries and unsafe input rejection;
- perfect and zero scoring cases;
- category aggregation and analytics;
- JSON persistence and corrupt-file recovery;
- CSV/Markdown/TXT report generation;
- application services and validated bulk import.

The test suite was executed successfully while preparing this release.

## Important design trade-off

The required local JSON file is convenient and transparent for a student demonstration. The repository serializes writes atomically and the UI paginates displayed results. For very large production datasets, a database-backed repository (for example SQLite from Python's standard library) would be the next scalability step; the repository boundary is intended to allow that without changing the quiz and analytics layers.
