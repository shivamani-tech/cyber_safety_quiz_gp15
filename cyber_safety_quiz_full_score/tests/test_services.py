import unittest
from cyberquiz.services import submit_attempt, search_attempts, parse_legacy_csv
from cyberquiz.storage import JsonRepository
from cyberquiz.questions import QUESTIONS
from cyberquiz.validation import ValidationError
import tempfile
from pathlib import Path

class ServiceTests(unittest.TestCase):
    def test_submit_attempt_validates_grades_and_saves(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = JsonRepository(Path(folder) / "records.json")
            answers = [str(q["answer"]) for q in QUESTIONS]
            name, result, record = submit_attempt(repo, "Demo Student", answers)
            self.assertEqual(name, "Demo Student")
            self.assertEqual(result["percentage"], 100)
            self.assertEqual(repo.count(), 1)
    def test_submit_attempt_rejects_invalid_before_save(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = JsonRepository(Path(folder) / "records.json")
            with self.assertRaises(ValidationError):
                submit_attempt(repo, "", ["0"] * len(QUESTIONS))
            self.assertEqual(repo.count(), 0)
    def test_legacy_csv_validated(self):
        rows = parse_legacy_csv(b"name,score,total,date\nDemo Student,7,8,2026-11-24\n")
        self.assertEqual(rows[0]["percentage"], 88)
    def test_legacy_csv_rejects_bad_row(self):
        with self.assertRaises(ValidationError):
            parse_legacy_csv(b"name,score,total,date\n<script>,9,8,today\n")
    def test_search_is_case_insensitive(self):
        records = [{"name":"Demo Student","category_scores":{"Phishing":{}}}]
        self.assertEqual(len(search_attempts(records, "demo")), 1)
        self.assertEqual(len(search_attempts(records, "demo", "Online Safety")), 0)

if __name__ == "__main__": unittest.main()
