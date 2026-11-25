import csv
import json
import tempfile
import unittest
from pathlib import Path
from cyberquiz.storage import JsonRepository, make_record
from cyberquiz.questions import QUESTIONS, grade
from cyberquiz.reports import export_csv, export_markdown, export_text

class StorageReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "records.json"
        self.repo = JsonRepository(self.path)
    def tearDown(self):
        self.temp.cleanup()
    def test_missing_file_initializes(self):
        self.assertEqual(self.repo.list_records(), [])
        self.assertTrue(self.path.exists())
    def test_add_and_reload_persists(self):
        result = grade([q["answer"] for q in QUESTIONS])
        record = make_record("Test User", result)
        self.repo.add(record)
        self.assertEqual(self.repo.list_records()[0]["name"], "Test User")
    def test_corrupt_file_is_backed_up(self):
        self.path.write_text("{broken", encoding="utf-8")
        self.assertEqual(self.repo.list_records(), [])
        self.assertTrue(self.repo.backup_path.exists())
        self.assertEqual(json.loads(self.path.read_text()), [])
    def test_invalid_schema_rows_are_ignored(self):
        self.path.write_text(json.dumps([{"name":"bad"}, {"record_id":"1","name":"ok","score":1,
            "total":1,"percentage":100,"date":"today","category_scores":{}}]), encoding="utf-8")
        self.assertEqual(len(self.repo.list_records()), 1)
    def test_batch_add_is_persisted_together(self):
        records = [{"record_id":"i1","name":"One","score":1,"total":1,"percentage":100,
                    "date":"today","category_scores":{}},
                   {"record_id":"i2","name":"Two","score":0,"total":1,"percentage":0,
                    "date":"today","category_scores":{}}]
        self.repo.add_many(records)
        self.assertEqual(self.repo.count(), 2)
    def test_csv_export_has_header_and_data(self):
        result = grade([q["answer"] for q in QUESTIONS])
        self.repo.add(make_record("Export User", result))
        target = export_csv(self.repo.list_records(), Path(self.temp.name)/"out.csv")
        with target.open(encoding="utf-8") as f: rows = list(csv.reader(f))
        self.assertEqual(len(rows), 2)
        self.assertIn("Export User", rows[1])
    def test_markdown_and_text_export(self):
        result = grade([q["answer"] for q in QUESTIONS])
        self.repo.add(make_record("Report User", result))
        md = export_markdown(self.repo.list_records(), Path(self.temp.name)/"out.md")
        txt = export_text(self.repo.list_records(), Path(self.temp.name)/"out.txt")
        self.assertIn("Executive Summary", md.read_text())
        self.assertIn("AUDIT REPORT", txt.read_text())

if __name__ == "__main__": unittest.main()
