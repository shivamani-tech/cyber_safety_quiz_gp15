"""HTTP presentation/controller layer. HTML forms submit directly to Python; no JS/CSS."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
import csv, io, html, secrets
from .config import HOST, PORT, RECORDS_FILE, EXPORT_DIR, MAX_REQUEST_BYTES, PAGE_SIZE, APP_NAME
from .questions import QUESTIONS, grade
from .validation import validate_name, validate_answers, validate_category, ValidationError
from .storage import JsonRepository, make_record, StorageError
from .analytics import summarize, markdown_report
from .reports import export_csv, export_markdown, export_text, export_chart
from .services import submit_attempt, search_attempts, parse_legacy_csv

REPO = JsonRepository(RECORDS_FILE)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def e(value):
    return html.escape(str(value), quote=True)

def layout(title, body):
    # Pure semantic HTML: no CSS, JavaScript, remote assets or inline event handlers.
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Local cyber awareness quiz and analytics">
<title>{e(title)} | {APP_NAME}</title></head>
<body>
<header><h1>🛡️ {APP_NAME}</h1><p><strong>LEARN · IDENTIFY · PROTECT</strong></p>
<nav><a href="/">Home</a> | <a href="/quiz">Take Quiz</a> | <a href="/records">Records</a> | <a href="/analytics">Analytics</a> | <a href="/reports">Reports</a></nav></header>
<hr><main>{body}</main><hr>
<footer><p>Local educational demo · Never enter real passwords or OTPs.</p></footer>
</body></html>"""

def home_page():
    return layout("Home", """
<h2>Welcome to Cyber Safety Quiz</h2>
<p>Build awareness of password safety, phishing attacks and safe online habits.</p>
<h3>Learning categories</h3><ul>
<li><strong>Password Safety:</strong> Create and protect unique credentials.</li>
<li><strong>Phishing:</strong> Recognize suspicious messages and links.</li>
<li><strong>Online Safety:</strong> Make safer choices on the internet.</li></ul>
<h3>How it works</h3><ol><li>Enter your name.</li><li>Answer the quiz questions.</li>
<li>Review explanations and your score.</li><li>Track trends and export reports.</li></ol>
<p><a href="/quiz">Start the quiz</a></p>
<p>Records are stored locally in a validated JSON file and preserved between restarts.</p>
""")

def quiz_page(error=""):
    parts = ['<h2>Cyber Safety Quiz</h2><p>All questions are required. Select one option for each.</p>']
    if error: parts.append(f'<p><strong>Error: {e(error)}</strong></p>')
    parts.append('<form method="post" action="/submit"><p><label>Your name (1–40 letters): <input name="name" maxlength="40" required></label></p>')
    for index, q in enumerate(QUESTIONS):
        parts.append(f'<fieldset><legend>Question {index+1} — {e(q["category"])}</legend><p>{e(q["prompt"])}</p>')
        for option_index, option in enumerate(q["options"]):
            parts.append(f'<label><input type="radio" name="q{index}" value="{option_index}" required> {e(option)}</label><br>')
        parts.append('</fieldset><br>')
    parts.append('<button type="submit">Submit quiz</button></form>')
    return layout("Take Quiz", "".join(parts))

def result_page(name, result):
    review = "".join(f'<li><strong>{"Correct" if item["correct"] else "Incorrect"}</strong> — '
                     f'Correct answer: {e(item["correct_answer"])}<br>{e(item["explanation"])}</li>'
                     for item in result["review"])
    status = "Passed — great work!" if result["passed"] else "Keep practising and try again."
    body = f"""<h2>Quiz result</h2><h3>{e(name)}: {result['score']} / {result['total']} ({result['percentage']}%)</h3>
<p><strong>{status}</strong></p><p>Your result has been saved successfully.</p>
<h3>Category breakdown</h3><ul>{''.join(f'<li>{e(k)}: {v["score"]}/{v["total"]}</li>' for k,v in result['category_scores'].items())}</ul>
<h3>Answer review</h3><ol>{review}</ol>
<p><a href="/quiz">Try again</a> | <a href="/records">View records</a> | <a href="/analytics">View analytics</a></p>"""
    return layout("Result", body)

def records_page(query="", category="All", page_number=1):
    validate_category(category)
    records = list(reversed(search_attempts(REPO.list_records(), query, category)))
    total = len(records)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page_number = max(1, min(page_number, pages))
    shown = records[(page_number-1)*PAGE_SIZE:page_number*PAGE_SIZE]
    rows = "".join(f'<tr><td>{e(r["name"])}</td><td>{r["score"]}/{r["total"]}</td><td>{r["percentage"]}%</td><td>{e(r["date"])}</td></tr>' for r in shown)
    if not rows: rows = '<tr><td colspan="4">No matching attempts yet.</td></tr>'
    category_options = "".join(f'<option value="{e(c)}" {"selected" if c==category else ""}>{e(c)}</option>' for c in ("All","Password Safety","Phishing","Online Safety"))
    previous = f'<a href="/records?q={e(query)}&category={e(category)}&page={page_number-1}">Previous</a>' if page_number > 1 else "Previous"
    following = f'<a href="/records?q={e(query)}&category={e(category)}&page={page_number+1}">Next</a>' if page_number < pages else "Next"
    body = f"""<h2>Saved quiz records</h2><form method="get" action="/records">
<label>Search name: <input name="q" maxlength="40" value="{e(query)}"></label>
<label>Category: <select name="category">{category_options}</select></label>
<button type="submit">Filter</button></form>
<p>{total} matching attempt(s) · Page {page_number} of {pages}</p>
<table border="1" cellpadding="8"><thead><tr><th>Name</th><th>Score</th><th>Percentage</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table>
<p>{previous} | {following}</p><p><a href="/export/csv">Export all records as CSV</a></p>"""
    return layout("Records", body)

def analytics_page():
    summary = summarize(REPO.list_records())
    cat_rows = "".join(f'<tr><td>{e(x["category"])}</td><td>{x["attempts"]}</td><td>{x["average"]}%</td></tr>' for x in summary["category_trends"])
    month_rows = "".join(f'<tr><td>{e(x["month"])}</td><td>{x["attempts"]}</td><td>{x["average"]}%</td></tr>' for x in summary["monthly_trends"])
    if not cat_rows: cat_rows = '<tr><td colspan="3">No quiz data yet.</td></tr>'
    if not month_rows: month_rows = '<tr><td colspan="3">No monthly data yet.</td></tr>'
    body = f"""<h2>Executive analytics</h2>
<table border="1" cellpadding="10"><tr><th>Total attempts</th><th>Average</th><th>Best</th><th>Pass count</th><th>Pass rate</th></tr>
<tr><td>{summary["total_attempts"]}</td><td>{summary["average"]}%</td><td>{summary["best"]}%</td><td>{summary["pass_count"]}</td><td>{summary["pass_rate"]}%</td></tr></table>
<h3>Category performance</h3><table border="1" cellpadding="8"><tr><th>Category</th><th>Attempts</th><th>Average</th></tr>{cat_rows}</table>
<h3>Monthly trend</h3><table border="1" cellpadding="8"><tr><th>Month</th><th>Attempts</th><th>Average</th></tr>{month_rows}</table>
<p>Pass threshold: 70%. Monthly averages and category averages are calculated from stored attempts.</p>
<p><a href="/reports">Open report exports</a></p>"""
    return layout("Analytics", body)

def reports_page(message=""):
    body = f"""<h2>Export centre</h2>{f'<p>{e(message)}</p>' if message else ''}
<ul><li><a href="/export/csv">Download CSV results</a></li>
<li><a href="/export/markdown">Download Markdown executive report</a></li>
<li><a href="/export/text">Download plain-text audit report</a></li>
<li><a href="/export/chart">Download optional Matplotlib PNG chart</a> (requires Matplotlib to be installed)</li></ul>
<h3>Bulk CSV import</h3><p>Import a CSV containing columns: name, score, total, date. Imported rows are validated and added to the local JSON store.</p>
<form method="post" action="/import" enctype="multipart/form-data"><input type="file" name="dataset" accept=".csv" required><button type="submit">Validate and import CSV</button></form>"""
    return layout("Reports", body)

class QuizHandler(BaseHTTPRequestHandler):
    server_version = "CyberSafetyLocal/1.0"
    sys_version = ""

    def _headers(self, content_type, length, status=200, extra=()):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'none'; script-src 'none'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Cache-Control", "no-store")
        for key, value in extra: self.send_header(key, value)
        self.end_headers()

    def html(self, document, status=200):
        raw = document.encode("utf-8")
        self._headers("text/html; charset=utf-8", len(raw), status)
        self.wfile.write(raw)

    def download(self, path, filename, content_type):
        path = Path(path)
        data = path.read_bytes()
        self._headers(content_type, len(data), extra=(("Content-Disposition", f'attachment; filename="{filename}"'),))
        self.wfile.write(data)

    def _read_body(self):
        try: length = int(self.headers.get("Content-Length", "0"))
        except ValueError: raise ValidationError("Invalid request length.")
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise ValidationError("Request is empty or exceeds the size limit.")
        return self.rfile.read(length)

    def _local_origin_ok(self):
        origin = self.headers.get("Origin")
        if not origin: return True
        return origin in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}")

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/": self.html(home_page())
            elif parsed.path == "/quiz": self.html(quiz_page())
            elif parsed.path == "/records":
                params = parse_qs(parsed.query)
                page_value = params.get("page", ["1"])[0]
                if not page_value.isdigit(): raise ValidationError("Page must be a positive number.")
                self.html(records_page(params.get("q", [""])[0], params.get("category", ["All"])[0], int(page_value)))
            elif parsed.path == "/analytics": self.html(analytics_page())
            elif parsed.path == "/reports": self.html(reports_page())
            elif parsed.path == "/export/csv":
                path = export_csv(REPO.list_records(), EXPORT_DIR / "cyber_safety_results.csv")
                self.download(path, "cyber_safety_results.csv", "text/csv; charset=utf-8")
            elif parsed.path == "/export/markdown":
                path = export_markdown(REPO.list_records(), EXPORT_DIR / "cyber_safety_report.md")
                self.download(path, "cyber_safety_report.md", "text/markdown; charset=utf-8")
            elif parsed.path == "/export/text":
                path = export_text(REPO.list_records(), EXPORT_DIR / "cyber_safety_audit.txt")
                self.download(path, "cyber_safety_audit.txt", "text/plain; charset=utf-8")
            elif parsed.path == "/export/chart":
                path = export_chart(REPO.list_records(), EXPORT_DIR / "cyber_safety_chart.png")
                if not path: self.html(reports_page("Matplotlib is not installed. Install it optionally with: python -m pip install matplotlib"), 200)
                else: self.download(path, "cyber_safety_chart.png", "image/png")
            else: self.html(layout("Not found", "<h2>404 — Page not found</h2><p><a href='/'>Home</a></p>"), 404)
        except (ValidationError, StorageError, OSError) as exc:
            self.html(layout("Request error", f"<h2>Unable to complete request</h2><p>{e(exc)}</p><p><a href='/'>Home</a></p>"), 400)

    def do_POST(self):
        try:
            if not self._local_origin_ok():
                raise ValidationError("Cross-origin form submission rejected.")
            body = self._read_body()
            parsed = urlparse(self.path)
            if parsed.path == "/submit":
                from urllib.parse import parse_qs
                form = parse_qs(body.decode("utf-8"), keep_blank_values=True, max_num_fields=30)
                raw_answers = [form.get(f"q{i}", [""])[0] for i in range(len(QUESTIONS))]
                name, result, record = submit_attempt(REPO, form.get("name", [""])[0], raw_answers)
                self.html(result_page(name, result), 201)
            elif parsed.path == "/import":
                from email.parser import BytesParser
                from email import policy
                content_type = self.headers.get("Content-Type", "")
                if "multipart/form-data" not in content_type:
                    raise ValidationError("Upload must use a CSV file.")
                message = BytesParser(policy=policy.default).parsebytes(
                    b"Content-Type: " + content_type.encode() + b"\\r\\nMIME-Version: 1.0\\r\\n\\r\\n" + body)
                uploaded = None
                for part in message.iter_parts():
                    if part.get_param("name", header="content-disposition") == "dataset":
                        uploaded = part.get_payload(decode=True)
                        break
                if uploaded is None or len(uploaded) > MAX_REQUEST_BYTES:
                    raise ValidationError("CSV file is missing or too large.")
                imported = parse_legacy_csv(uploaded)
                for item in imported:
                    item["record_id"] = "IMPORT-" + secrets.token_hex(8)
                # The complete file is validated before one atomic batch commit.
                REPO.add_many(imported)
                self.html(reports_page(f"Successfully imported {len(imported)} validated row(s)."))
            else:
                self.html(layout("Not found", "<h2>404 — Page not found</h2>"), 404)
        except (ValidationError, ValueError, UnicodeDecodeError, StorageError) as exc:
            self.html(quiz_page(str(exc)), 400)
        except Exception:
            # Avoid exposing internal paths, stack traces or submitted data to the browser.
            self.log_error("Unexpected request failure")
            self.html(layout("Server error", "<h2>Unexpected server error</h2><p>Please retry or inspect the local terminal log.</p>"), 500)

    def log_message(self, fmt, *args):
        print("[CyberSafety] " + fmt % args)

def run_server():
    print("=" * 58)
    print(" CYBER SAFETY QUIZ — LOCAL PYTHON WEB APPLICATION")
    print("=" * 58)
    print(f"Open http://{HOST}:{PORT} in your browser.")
    print("No JavaScript or CSS is used. Press Ctrl+C to stop.")
    server = ThreadingHTTPServer((HOST, PORT), QuizHandler)
    server.daemon_threads = True
    try: server.serve_forever()
    except KeyboardInterrupt: print("\\nServer stopped.")
    finally: server.server_close()
