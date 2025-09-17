"""Boolean validation rule"""

from typing import Any, List
from .base_rule import BaseRule


class Boolean(BaseRule):
    """The field under validation must be a boolean value"""

    BOOLEAN_VALUES = {
        True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False',
        'yes', 'no', 'Yes', 'No', 'on', 'off', 'On', 'Off'
    }

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        return value in self.BOOLEAN_VALUES

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be true or false."