"""Integer validation rule"""

from typing import Any, List
from .base_rule import BaseRule


class Integer(BaseRule):
    """The field under validation must be an integer"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        # Check if it's already an integer
        if isinstance(value, int) and not isinstance(value, bool):
            return True

        # Check if it's a string that represents an integer
        if isinstance(value, str):
            try:
                int(value)
                return True
            except ValueError:
                return False

        # Check if it's a float that's actually a whole number
        if isinstance(value, float):
            return value.is_integer()

        return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be an integer."