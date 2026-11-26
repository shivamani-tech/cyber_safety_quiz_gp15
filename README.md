# Cyber Safety Quiz — Python + HTML + NiceGUI

This project now has a **NiceGUI-powered webpage** backed by the existing Python modules and local JSON storage.

## Run in VS Code

1. Extract the ZIP and open the `CyberSafetyQuiz_NiceGUI` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Start the NiceGUI website (the page theme is initialized inside each page, as required by NiceGUI multi-page apps):

```bash
python nicegui_app.py
```

5. Open **http://127.0.0.1:8080** in your browser.

## Optional: run the original standard-library HTML version

```bash
python app.py
```

Open **http://127.0.0.1:8000**.

Do not run both servers on the same port; they use separate ports by default.

## NiceGUI features

- Responsive CyberShield dashboard and summary cards
- Password Safety, Phishing and Online Safety quiz
- Defensive validation and immediate result review
- Local JSON persistence using the existing repository
- Participant search and category filtering
- Analytics charts and performance trends
- CSV, Markdown, TXT and PNG report downloads
- Bulk CSV import with validation
- Shared backend modules and data file with the original HTML application

## Project structure

```text
CyberSafetyQuiz_NiceGUI/
├── app.py                  # Original HTML server
├── nicegui_app.py          # NiceGUI website entry point
├── requirements.txt
├── cyberquiz/              # Shared Python logic
├── data/                   # Local JSON records
├── exports/                # Generated reports
└── tests/                  # Automated tests
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

The project includes automated tests for validation, scoring, persistence, analytics and reports.

**Scoring note:** The implementation is designed to demonstrate the project requirements, but no exact rubric score can be guaranteed; marks depend on the evaluator's review and your live demonstration.
