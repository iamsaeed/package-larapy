"""URL validation rule"""

import re
from typing import Any, List
from .base_rule import BaseRule


class Url(BaseRule):
    """The field under validation must be a valid URL"""

    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        if not isinstance(value, str):
            return False

        return bool(self.URL_PATTERN.match(value))

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be a valid URL."