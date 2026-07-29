import re
from typing import Optional

class InputSanitizer:
    # Common prompt injection signals
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+all\s+previous\s+instructions", re.IGNORECASE),
        re.compile(r"ignore\s+system\s+prompt", re.IGNORECASE),
        re.compile(r"system\s+override", re.IGNORECASE),
        re.compile(r"you\s+must\s+now\s+act\s+as", re.IGNORECASE),
        re.compile(r"new\s+role:", re.IGNORECASE),
        re.compile(r"forget\s+what\s+i\s+said\s+before", re.IGNORECASE),
        re.compile(r"dan\s+mode", re.IGNORECASE),
        re.compile(r"developer\s+mode", re.IGNORECASE)
    ]

    # Email pattern validation
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    
    # ISO date validation YYYY-MM-DD
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Removes control characters, scripts, and normalizes whitespaces."""
        if not text:
            return ""
        # Remove HTML tag injections
        cleaned = re.sub(r"<[^>]*>", "", text)
        # Strip potential SQL comments / basic injection cues
        cleaned = re.sub(r"--", "", cleaned)
        cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
        return cleaned.strip()

    @classmethod
    def check_prompt_injection(cls, text: str) -> bool:
        """Scans input strings against known prompt injection signature regexes."""
        if not text:
            return False
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(text):
                return True
        return False

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validates that a string matches standard email formatting constraints."""
        if not email:
            return False
        return bool(cls.EMAIL_PATTERN.match(email))

    @classmethod
    def validate_date(cls, date_str: str) -> bool:
        """Validates YYYY-MM-DD formatting."""
        if not date_str:
            return False
        return bool(cls.DATE_PATTERN.match(date_str))
