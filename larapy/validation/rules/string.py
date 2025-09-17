"""String validation rule"""

from typing import Any, List
from .base_rule import BaseRule


class String(BaseRule):
    """The field under validation must be a string"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        return isinstance(value, str)

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be a string."