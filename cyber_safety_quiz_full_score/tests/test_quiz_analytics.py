import unittest
from cyberquiz.questions import QUESTIONS, grade
from cyberquiz.analytics import summarize

class QuizAnalyticsTests(unittest.TestCase):
    def test_perfect_score(self):
        result = grade([q["answer"] for q in QUESTIONS])
        self.assertEqual(result["score"], len(QUESTIONS))
        self.assertEqual(result["percentage"], 100)
        self.assertTrue(result["passed"])
    def test_zero_score(self):
        answers = [(q["answer"] + 1) % 4 for q in QUESTIONS]
        result = grade(answers)
        self.assertEqual(result["score"], 0)
        self.assertFalse(result["passed"])
    def test_category_totals(self):
        result = grade([q["answer"] for q in QUESTIONS])
        self.assertEqual(sum(v["total"] for v in result["category_scores"].values()), len(QUESTIONS))
    def test_analytics_empty_dataset(self):
        summary = summarize([])
        self.assertEqual(summary["total_attempts"], 0)
        self.assertEqual(summary["average"], 0)
        self.assertEqual(summary["pass_rate"], 0)
    def test_analytics_calculation(self):
        records = [
            {"percentage": 100, "passed": True, "date": "2026-11-24",
             "category_scores": {"Phishing": {"score": 2, "total": 2}}},
            {"percentage": 50, "passed": False, "date": "2026-11-24",
             "category_scores": {"Phishing": {"score": 1, "total": 2}}}
        ]
        result = summarize(records)
        self.assertEqual(result["average"], 75)
        self.assertEqual(result["best"], 100)
        self.assertEqual(result["pass_rate"], 50)
        self.assertEqual(result["category_trends"][0]["average"], 75)

if __name__ == "__main__": unittest.main()
