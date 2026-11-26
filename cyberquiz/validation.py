"""Centralized validation and safe normalization."""
import re

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{0,39}$")
CATEGORIES = ("Password Safety", "Phishing", "Online Safety")

class ValidationError(ValueError):
    """Raised when submitted data violates the application schema."""

def validate_name(value):
    if not isinstance(value, str):
        raise ValidationError("Name must be text.")
    name = " ".join(value.strip().split())
    if not NAME_PATTERN.fullmatch(name):
        raise ValidationError("Enter 1–40 letters; spaces, apostrophes, dots and hyphens are allowed.")
    return name

def validate_answers(raw_answers, question_count):
    if not isinstance(raw_answers, (list, tuple)) or len(raw_answers) != question_count:
        raise ValidationError(f"Please answer all {question_count} questions.")
    answers = []
    for index, raw in enumerate(raw_answers, start=1):
        if isinstance(raw, bool):
            raise ValidationError(f"Invalid answer for question {index}.")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise ValidationError(f"Select an answer for question {index}.")
        if str(value) != str(raw) or not 0 <= value <= 3:
            raise ValidationError(f"Answer for question {index} is outside the allowed range.")
        answers.append(value)
    return answers

def validate_category(value):
    if value not in ("All",) + CATEGORIES:
        raise ValidationError("Choose a valid category.")
    return value
