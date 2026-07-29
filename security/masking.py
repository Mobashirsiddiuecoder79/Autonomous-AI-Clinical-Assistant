import re

class PIIMasker:
    # Regex configurations for standard PII properties
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")

    @classmethod
    def mask_text(cls, text: str) -> str:
        """
        Scans and redacts sensitive patient attributes (SSN, Phone, Email) 
        from message inputs before saving to standard logs.
        """
        if not text:
            return ""
        
        masked = text
        # Redact SSN
        masked = cls.SSN_PATTERN.sub("[SSN_REDACTED]", masked)
        # Redact Email
        masked = cls.EMAIL_PATTERN.sub("[EMAIL_REDACTED]", masked)
        # Redact Phone numbers
        masked = cls.PHONE_PATTERN.sub("[PHONE_REDACTED]", masked)
        
        return masked
