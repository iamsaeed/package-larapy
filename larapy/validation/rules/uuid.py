"""UUID validation rule"""

import uuid
from typing import Any, List
from .base_rule import BaseRule


class Uuid(BaseRule):
    """The field under validation must be a valid UUID"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        if not isinstance(value, str):
            return False

        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be a valid UUID."