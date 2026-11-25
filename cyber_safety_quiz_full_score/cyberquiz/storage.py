"""Thread-safe JSON persistence with schema checks and atomic replacement."""
import json
import threading
from datetime import datetime
from pathlib import Path

_LOCK = threading.RLock()
_REQUIRED = {"record_id", "name", "score", "total", "percentage", "date", "category_scores"}

class StorageError(RuntimeError):
    pass

def _valid_record(item):
    if not isinstance(item, dict) or not _REQUIRED.issubset(item):
        return False
    score, total = item.get("score"), item.get("total")
    return (isinstance(score, int) and not isinstance(score, bool) and
            isinstance(total, int) and not isinstance(total, bool) and
            total > 0 and 0 <= score <= total and
            isinstance(item.get("name"), str) and isinstance(item.get("date"), str) and
            isinstance(item.get("category_scores"), dict))

class JsonRepository:
    def __init__(self, path):
        self.path = Path(path)
        self.backup_path = self.path.with_name(self.path.stem + ".corrupt-backup" + self.path.suffix)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list_records(self):
        with _LOCK:
            if not self.path.exists():
                self._write_unlocked([])
                return []
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    raise ValueError("Root JSON value must be a list.")
                return [item for item in data if _valid_record(item)]
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                try:
                    if self.path.exists() and not self.backup_path.exists():
                        self.path.replace(self.backup_path)
                except OSError as exc:
                    raise StorageError(f"Could not preserve damaged data: {exc}") from exc
                self._write_unlocked([])
                return []
            except OSError as exc:
                raise StorageError(f"Could not read records: {exc}") from exc

    def _write_unlocked(self, records):
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self.path)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise StorageError(f"Could not save records: {exc}") from exc

    def add(self, record):
        with _LOCK:
            records = self.list_records()
            records.append(record)
            self._write_unlocked(records)
            return record

    def add_many(self, new_records):
        """Commit a validated batch with one atomic replacement."""
        with _LOCK:
            records = self.list_records()
            records.extend(new_records)
            self._write_unlocked(records)
            return len(new_records)

    def count(self):
        return len(self.list_records())

def make_record(name, result):
    now = datetime.now().astimezone()
    return {
        "record_id": now.strftime("%Y%m%d%H%M%S%f"),
        "name": name, "score": result["score"], "total": result["total"],
        "percentage": result["percentage"], "passed": result["passed"],
        "date": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "category_scores": result["category_scores"]
    }
