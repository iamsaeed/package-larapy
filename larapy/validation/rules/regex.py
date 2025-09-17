"""Regex validation rule"""

import re
from typing import Dict, Any, Optional, List
from .base_rule import BaseRule


class RegexRule(BaseRule):
    """Validates that a field matches a regular expression pattern"""

    def __init__(self, pattern: str):
        super().__init__()
        self.name = 'regex'
        self.pattern = pattern

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if value matches the regex pattern"""
        if not isinstance(value, str):
            return False

        try:
            return bool(re.match(self.pattern, value))
        except re.error:
            # Invalid regex pattern
            return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute format is invalid.'