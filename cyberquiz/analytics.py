"""Analytics, trends, and report generation."""
from collections import defaultdict
from datetime import datetime

def summarize(records):
    count = len(records)
    percentages = [r["percentage"] for r in records]
    categories = defaultdict(lambda: {"attempts": 0, "score": 0, "total": 0})
    monthly = defaultdict(lambda: {"attempts": 0, "score": 0})
    for record in records:
        for category, values in record.get("category_scores", {}).items():
            categories[category]["attempts"] += 1
            categories[category]["score"] += values["score"]
            categories[category]["total"] += values["total"]
        month = record.get("date", "")[:7]
        if len(month) == 7:
            monthly[month]["attempts"] += 1
            monthly[month]["score"] += record["percentage"]
    category_rows = []
    for name, item in sorted(categories.items()):
        category_rows.append({"category": name, "attempts": item["attempts"],
                              "average": round(item["score"] / item["total"] * 100) if item["total"] else 0})
    monthly_rows = [{"month": month, **values,
                     "average": round(values["score"] / values["attempts"]) if values["attempts"] else 0}
                    for month, values in sorted(monthly.items())]
    return {
        "total_attempts": count,
        "average": round(sum(percentages) / count) if count else 0,
        "best": max(percentages, default=0),
        "pass_count": sum(bool(r.get("passed", r["percentage"] >= 70)) for r in records),
        "pass_rate": round(sum(bool(r.get("passed", r["percentage"] >= 70)) for r in records) / count * 100) if count else 0,
        "category_trends": category_rows, "monthly_trends": monthly_rows
    }

def markdown_report(records, summary):
    lines = ["# Cyber Safety Quiz Report", "",
             f"Generated: {datetime.now().astimezone().isoformat(timespec='minutes')}", "",
             "## Executive Summary", "",
             f"- Total attempts: {summary['total_attempts']}",
             f"- Average score: {summary['average']}%",
             f"- Best score: {summary['best']}%",
             f"- Pass rate: {summary['pass_rate']}%", "",
             "## Category Trends", "", "| Category | Attempts | Average |", "|---|---:|---:|"]
    lines += [f"| {x['category']} | {x['attempts']} | {x['average']}% |" for x in summary["category_trends"]]
    lines += ["", "## Individual Results", "", "| Name | Score | Percentage | Date |", "|---|---:|---:|---|"]
    lines += [f"| {r['name']} | {r['score']}/{r['total']} | {r['percentage']}% | {r['date']} |" for r in records]
    return "\n".join(lines) + "\n"
