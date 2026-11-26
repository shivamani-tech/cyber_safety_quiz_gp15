import unittest
from cyberquiz.validation import validate_name, validate_answers, validate_category, ValidationError

class ValidationTests(unittest.TestCase):
    def test_valid_name_is_normalized(self):
        self.assertEqual(validate_name("  Asha   Rao "), "Asha Rao")
    def test_blank_name_rejected(self):
        with self.assertRaises(ValidationError): validate_name(" ")
    def test_overlong_name_rejected(self):
        with self.assertRaises(ValidationError): validate_name("A" * 41)
    def test_markup_in_name_rejected(self):
        with self.assertRaises(ValidationError): validate_name("<script>")
    def test_answer_count_checked(self):
        with self.assertRaises(ValidationError): validate_answers([0], 2)
    def test_answer_range_checked(self):
        with self.assertRaises(ValidationError): validate_answers([0, 4], 2)
    def test_boolean_is_not_integer_answer(self):
        with self.assertRaises(ValidationError): validate_answers([True], 1)
    def test_category_checked(self):
        self.assertEqual(validate_category("Phishing"), "Phishing")
        with self.assertRaises(ValidationError): validate_category("Other")

if __name__ == "__main__": unittest.main()
