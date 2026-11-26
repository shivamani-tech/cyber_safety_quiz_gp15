"""CSV, Markdown, text and optional Matplotlib chart exports."""
import csv
from pathlib import Path
from .analytics import summarize, markdown_report

def export_csv(records, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Record ID", "Name", "Score", "Total", "Percentage", "Passed", "Date"])
        for r in records:
            writer.writerow([r["record_id"], r["name"], r["score"], r["total"], r["percentage"], r["passed"], r["date"]])
    return path

def export_markdown(records, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_report(records, summarize(records)), encoding="utf-8")
    return path

def export_text(records, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    summary = summarize(records)
    lines = ["CYBER SAFETY QUIZ — AUDIT REPORT", "=" * 34,
             f"Attempts: {summary['total_attempts']}",
             f"Average: {summary['average']}%",
             f"Best: {summary['best']}%",
             f"Pass rate: {summary['pass_rate']}%", "", "RESULTS"]
    lines.extend(f"{r['date']} | {r['name']} | {r['score']}/{r['total']} | {r['percentage']}%" for r in records)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path

def export_chart(records, path):
    """Create a PNG chart when optional Matplotlib is installed; otherwise return False."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    summary = summarize(records)
    labels = [item["category"] for item in summary["category_trends"]]
    values = [item["average"] for item in summary["category_trends"]]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_ylim(0, 100); ax.set_ylabel("Average score (%)")
    ax.set_title("Cyber Safety Quiz — Category Performance")
    fig.tight_layout()
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140); plt.close(fig)
    return path
