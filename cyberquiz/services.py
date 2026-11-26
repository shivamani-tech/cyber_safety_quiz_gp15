"""Application use cases, independent of the HTTP transport."""
import csv
import io
from .questions import QUESTIONS, grade
from .storage import make_record
from .validation import validate_name, validate_answers, ValidationError

def submit_attempt(repository, raw_name, raw_answers):
    """Validate, grade, persist, and return one completed quiz attempt."""
    name = validate_name(raw_name)
    answers = validate_answers(raw_answers, len(QUESTIONS))
    result = grade(answers)
    record = make_record(name, result)
    repository.add(record)
    return name, result, record

def search_attempts(records, keyword="", category="All"):
    """Filter records without mutating the repository's source collection."""
    from .validation import validate_category
    validate_category(category)
    matches = list(records)
    if category != "All":
        matches = [r for r in matches if category in r.get("category_scores", {})]
    if keyword:
        needle = keyword.casefold()
        matches = [r for r in matches if needle in r.get("name", "").casefold()]
    return matches

def parse_legacy_csv(file_bytes, maximum_rows=500):
    """Validate legacy CSV rows before any persistence operation occurs."""
    try:
        content = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError("CSV must use UTF-8 encoding.") from exc
    reader = csv.DictReader(io.StringIO(content))
    required = {"name", "score", "total", "date"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise ValidationError("CSV headers must include name, score, total and date.")
    rows = []
    for line, row in enumerate(reader, start=2):
        if len(rows) >= maximum_rows:
            raise ValidationError(f"A maximum of {maximum_rows} rows can be imported at once.")
        name = validate_name(row.get("name", ""))
        try:
            score, total = int(row.get("score", "")), int(row.get("total", ""))
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid numeric score or total on CSV row {line}.") from exc
        if total <= 0 or not 0 <= score <= total:
            raise ValidationError(f"Invalid score or total on CSV row {line}.")
        percentage = round(score / total * 100)
        rows.append({"name": name, "score": score, "total": total,
                     "percentage": percentage, "passed": percentage >= 70,
                     "date": str(row.get("date", ""))[:40], "category_scores": {}})
    return rows
