"""Array validation rule"""

from typing import Any, List
from .base_rule import BaseRule


class Array(BaseRule):
    """The field under validation must be an array"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        return isinstance(value, (list, tuple, dict))

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be an array."