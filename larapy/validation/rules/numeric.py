"""Numeric validation rule"""

from typing import Any, List
from .base_rule import BaseRule


class Numeric(BaseRule):
    """The field under validation must be numeric"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        # Check if it's already a number
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True

        # Check if it's a string that represents a number
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False

        return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be numeric."