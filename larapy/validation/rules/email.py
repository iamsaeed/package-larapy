"""Email validation rule"""

import re
from typing import Any, List
from .base_rule import BaseRule


class Email(BaseRule):
    """The field under validation must be a valid email address"""

    # Simple email regex pattern (more comprehensive than basic, less than RFC 5322)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        if not isinstance(value, str):
            return False

        return bool(self.EMAIL_PATTERN.match(value))

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be a valid email address."