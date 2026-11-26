"""NiceGUI web interface for Cyber Safety Quiz."""
from pathlib import Path
from nicegui import ui, app
from cyberquiz.config import APP_NAME, RECORDS_FILE, EXPORT_DIR
from cyberquiz.questions import QUESTIONS
from cyberquiz.storage import JsonRepository
from cyberquiz.services import submit_attempt, search_attempts, parse_legacy_csv
from cyberquiz.validation import ValidationError
from cyberquiz.analytics import summarize
from cyberquiz.reports import export_csv, export_markdown, export_text, export_chart

REPO = JsonRepository(RECORDS_FILE)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Configure the theme only while a page is being built. NiceGUI does not allow
# UI setup calls at module scope in a multi-page script.
def setup_page():
    ui.colors(primary="#2563eb", secondary="#0f766e", accent="#7c3aed",
              positive="#16a34a", negative="#dc2626", warning="#d97706")
    ui.add_head_html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<style>
body { background: #f3f6fc; font-family: 'DM Sans', sans-serif; }
.q-page { background: #f3f6fc; }
h1,h2,h3,.brand { font-family: 'Space Grotesk', sans-serif; }
.hero { background: linear-gradient(120deg,#101d3b,#174a76); color:#fff;
  padding:28px 32px; border-radius:20px; box-shadow:0 12px 30px #142d501c; }
.hero h1 { color:white; font-size:2.15rem; font-weight:700; margin:5px 0; }
.hero p { color:#dce9f8; margin:0; }
.eyebrow { color:#8bd7ff; letter-spacing:2px; font-size:11px; font-weight:800; }
.metric-card { background:white; border:1px solid #dce5f1; border-radius:15px;
  padding:17px 20px; min-height:94px; box-shadow:0 4px 14px #19365c09; }
.metric-label { color:#64748b; font-size:12px; font-weight:700; text-transform:uppercase; }
.metric-value { color:#17233c; font:700 30px 'Space Grotesk'; margin-top:5px; }
.panel { background:white; border:1px solid #dce5f1; border-radius:16px; padding:18px; }
.section-title { font:700 21px 'Space Grotesk'; color:#17233c; }
.q-card { background:white; border:1px solid #dce5f1; border-radius:14px; padding:16px; }
</style>
""")

def records():
    return REPO.list_records()

def metric_card(label, value, icon):
    with ui.card().classes("metric-card").props("flat"):
        ui.label(f"{icon}  {label}").classes("metric-label")
        ui.label(str(value)).classes("metric-value")

def refresh_page():
    ui.navigate.to("/")

@ui.page("/")
def home():
    setup_page()
    all_records = records()
    summary = summarize(all_records)
    with ui.column().classes("w-full max-w-7xl mx-auto p-4 md:p-7 gap-5"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("shield", size="32px").classes("text-blue-700")
                ui.label("CyberShield").classes("brand text-2xl font-bold text-slate-900")
            ui.badge("SMART COMMUNITY · PROJECT #75", color="blue")
        with ui.element("div").classes("hero w-full"):
            ui.label("CYBER AWARENESS · LEARN · IDENTIFY · PROTECT").classes("eyebrow")
            ui.html("<h1>Cyber Safety Quiz</h1><p>Test your knowledge, track progress, and build safer digital habits.</p>")
        with ui.grid(columns=4).classes("w-full"):
            metric_card("Total attempts", summary["total_attempts"], "📝")
            metric_card("Average score", f'{summary["average"]}%', "📊")
            metric_card("Pass rate", f'{summary["pass_rate"]}%', "✅")
            metric_card("Best score", f'{summary["best"]}%', "🏆")
        with ui.row().classes("w-full items-center gap-2"):
            ui.button("Take a Quiz", icon="quiz", on_click=lambda: ui.navigate.to("/quiz")).props("unelevated color=primary")
            ui.button("Records & Search", icon="manage_search", on_click=lambda: ui.navigate.to("/records")).props("outline color=primary")
            ui.button("Analytics & Reports", icon="analytics", on_click=lambda: ui.navigate.to("/analytics")).props("outline color=primary")
            ui.button("Import CSV", icon="upload_file", on_click=lambda: ui.navigate.to("/import")).props("outline color=primary")
        with ui.row().classes("w-full items-start gap-4"):
            with ui.card().classes("panel grow"):
                ui.label("Recent quiz attempts").classes("section-title")
                if all_records:
                    columns = [
                        {"name":"name","label":"Participant","field":"name","align":"left"},
                        {"name":"score","label":"Score","field":"score"},
                        {"name":"percentage","label":"Percentage","field":"percentage"},
                        {"name":"passed","label":"Status","field":"status"},
                        {"name":"date","label":"Date","field":"date"},
                    ]
                    rows = [{"name":r["name"],"score":f'{r["score"]}/{r["total"]}',
                             "percentage":f'{r["percentage"]}%',"status":"PASS" if r.get("passed",False) else "PRACTICE",
                             "date":r["date"]} for r in sorted(all_records,key=lambda x:x["date"],reverse=True)[:7]]
                    ui.table(columns=columns, rows=rows, row_key="name").classes("w-full")
                else:
                    ui.label("No attempts yet. Start your first quiz to populate the dashboard.").classes("text-slate-500")
            with ui.card().classes("panel w-72"):
                ui.label("Quiz categories").classes("section-title")
                ui.label("🔐 Password Safety")
                ui.label("🎣 Phishing Detection")
                ui.label("🌐 Online Safety")
                ui.separator()
                ui.label("Local JSON storage · Search · Analytics · Export").classes("text-sm text-slate-500")
        ui.label("Educational awareness tool. Never enter real passwords, OTPs or sensitive personal data.").classes("text-xs text-slate-500")

@ui.page("/quiz")
def quiz_page():
    setup_page()
    answers = []
    with ui.column().classes("w-full max-w-4xl mx-auto p-4 md:p-7 gap-4"):
        ui.button("← Dashboard", on_click=lambda: ui.navigate.to("/")).props("flat")
        ui.label("New cyber safety assessment").classes("section-title")
        name = ui.input("Participant name", placeholder="Enter your name").classes("w-full")
        for idx, question in enumerate(QUESTIONS):
            with ui.card().classes("q-card w-full"):
                ui.label(f'{idx+1}. {question["prompt"]}').classes("font-semibold text-slate-800")
                choice = ui.radio({i: option for i, option in enumerate(question["options"])}, value=None).props("inline=false")
                answers.append(choice)
                ui.label(question["category"]).classes("text-xs text-slate-500")
        result_box = ui.column().classes("w-full")
        def submit():
            try:
                selected = [
                    choice.value if isinstance(choice.value, int) and 0 <= choice.value < len(question["options"])
                    else None
                    for choice, question in zip(answers, QUESTIONS)
                ]
                clean_name, result, record = submit_attempt(REPO, name.value or "", selected)
                result_box.clear()
                with result_box:
                    ui.notify("Quiz result saved successfully.", type="positive")
                    with ui.card().classes("panel w-full"):
                        ui.label(f"Result for {clean_name}").classes("section-title")
                        with ui.row().classes("gap-8"):
                            ui.label(f'Score: {result["score"]}/{result["total"]}').classes("text-xl font-bold")
                            ui.label(f'{result["percentage"]}%').classes("text-xl font-bold text-blue-700")
                            ui.badge("PASS" if result["passed"] else "NEEDS PRACTICE",
                                     color="positive" if result["passed"] else "warning")
                        ui.separator()
                        for item, question in zip(result["review"], QUESTIONS):
                            with ui.expansion(f'{"Correct" if item["correct"] else "Review"} · {question["id"]}'):
                                ui.label(f'Correct answer: {item["correct_answer"]}')
                                ui.label(item["explanation"]).classes("text-slate-600")
                    ui.button("View dashboard", on_click=lambda: ui.navigate.to("/")).props("unelevated")
            except ValidationError as exc:
                ui.notify(str(exc), type="negative")
        ui.button("Submit answers & save result", on_click=submit, icon="check_circle").props("unelevated color=primary")

@ui.page("/records")
def records_page():
    setup_page()
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 md:p-7 gap-4"):
        ui.button("← Dashboard", on_click=lambda: ui.navigate.to("/")).props("flat")
        ui.label("Participant records & search").classes("section-title")
        keyword = ui.input("Search participant name", placeholder="Type a name").classes("w-full")
        category = ui.select(["All","Password Safety","Phishing","Online Safety"], value="All", label="Category").classes("w-full")
        table_slot = ui.column().classes("w-full")
        def show():
            table_slot.clear()
            found = search_attempts(records(), keyword.value or "", category.value or "All")
            with table_slot:
                ui.label(f"{len(found)} matching record(s)").classes("text-sm text-slate-500")
                cols=[{"name":"name","label":"Name","field":"name","align":"left"},
                      {"name":"score","label":"Score","field":"score"},
                      {"name":"percentage","label":"Percentage","field":"percentage"},
                      {"name":"status","label":"Status","field":"status"},
                      {"name":"date","label":"Date","field":"date"}]
                rows=[{"name":r["name"],"score":f'{r["score"]}/{r["total"]}',
                       "percentage":f'{r["percentage"]}%',"status":"PASS" if r.get("passed",False) else "NEEDS PRACTICE",
                       "date":r["date"]} for r in found]
                if rows: ui.table(columns=cols, rows=rows, row_key="name").classes("w-full")
                else: ui.label("No matching records found.").classes("text-slate-500")
                if found:
                    path=export_csv(found, EXPORT_DIR/"filtered_records.csv")
                    ui.button("Download filtered CSV", on_click=lambda: ui.download(path)).props("outline")
        ui.button("Search records", on_click=show).props("unelevated color=primary")
        show()

@ui.page("/analytics")
def analytics_page():
    setup_page()
    data = records()
    summary = summarize(data)
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 md:p-7 gap-4"):
        ui.button("← Dashboard", on_click=lambda: ui.navigate.to("/")).props("flat")
        ui.label("Analytics & executive reports").classes("section-title")
        with ui.grid(columns=4).classes("w-full"):
            metric_card("Attempts", summary["total_attempts"], "📝")
            metric_card("Average", f'{summary["average"]}%', "📊")
            metric_card("Pass rate", f'{summary["pass_rate"]}%', "✅")
            metric_card("Best score", f'{summary["best"]}%', "🏆")
        if data:
            ui.label("Category performance").classes("text-lg font-bold")
            trends=summary["category_trends"]
            ui.echart({"xAxis":{"type":"category","data":[x["category"] for x in trends]},
                       "yAxis":{"type":"value","max":100,"name":"Average (%)"},
                       "series":[{"type":"bar","data":[x["average"] for x in trends],
                                  "itemStyle":{"color":"#2563eb"},"label":{"show":True,"position":"top"}}],
                       "tooltip":{"trigger":"axis"}}).classes("w-full h-80")
            ui.label("Monthly attempts").classes("text-lg font-bold")
            monthly=summary["monthly_trends"]
            ui.echart({"xAxis":{"type":"category","data":[x["month"] for x in monthly]},
                       "yAxis":{"type":"value","name":"Attempts"},
                       "series":[{"type":"line","smooth":True,"data":[x["attempts"] for x in monthly],
                                  "areaStyle":{}}],"tooltip":{"trigger":"axis"}}).classes("w-full h-72")
            with ui.row().classes("gap-2"):
                csv_path=export_csv(data,EXPORT_DIR/"cyber_safety_report.csv")
                md_path=export_markdown(data,EXPORT_DIR/"cyber_safety_report.md")
                txt_path=export_text(data,EXPORT_DIR/"cyber_safety_audit.txt")
                ui.button("Download CSV",on_click=lambda:ui.download(csv_path),icon="download").props("outline")
                ui.button("Download Markdown",on_click=lambda:ui.download(md_path),icon="download").props("outline")
                ui.button("Download TXT",on_click=lambda:ui.download(txt_path),icon="download").props("outline")
                chart_path=export_chart(data,EXPORT_DIR/"cyber_safety_chart.png")
                if chart_path:
                    ui.button("Download PNG chart",on_click=lambda:ui.download(chart_path),icon="image").props("outline")
        else:
            ui.label("Analytics will appear after the first quiz attempt.").classes("text-slate-500")

@ui.page("/import")
def import_page():
    setup_page()
    with ui.column().classes("w-full max-w-4xl mx-auto p-4 md:p-7 gap-4"):
        ui.button("← Dashboard", on_click=lambda: ui.navigate.to("/")).props("flat")
        ui.label("Bulk CSV import").classes("section-title")
        ui.label("CSV headers required: name, score, total, date. The file is validated before saving.")
        def handle_upload(e):
            try:
                content=e.content.read()
                imported=parse_legacy_csv(content)
                REPO.add_many(imported)
                ui.notify(f"Imported {len(imported)} validated record(s).",type="positive")
            except (ValidationError, Exception) as exc:
                ui.notify(f"Import failed: {exc}",type="negative")
        ui.upload(on_upload=handle_upload, auto_upload=True).props('accept=".csv"').classes("w-full")
        ui.label("Invalid rows reject the import rather than silently saving partial data.").classes("text-sm text-slate-500")

@ui.page("/about")
def about_page():
    setup_page()
    with ui.column().classes("w-full max-w-4xl mx-auto p-4 md:p-7 gap-3"):
        ui.button("← Dashboard", on_click=lambda: ui.navigate.to("/")).props("flat")
        ui.label("About this project").classes("section-title")
        ui.markdown("""
**Cyber Safety Quiz** is a local-first learning application covering:

- Password Safety
- Phishing
- Online Safety

**Core engineering features:** Python modular services, centralized input validation, JSON schema checks, persistent local records, search, analytics, CSV/Markdown/TXT/PNG reporting, and validated CSV import.

**Demo sequence:** start the app → attempt invalid inputs → complete a quiz → search records → view analytics → export reports → restart and verify persistence.
""")
        ui.label("Never enter real passwords, OTPs or sensitive personal information.").classes("text-orange-800")

# Shared navigation header on all pages.
@ui.page("/nav")
def nav_page():
    ui.navigate.to("/")

ui.run(title=APP_NAME, host="127.0.0.1", port=8080, reload=False, show=False)
