"""Required validation rule"""

from typing import Any, List
from .base_rule import ImplicitRule


class Required(ImplicitRule):
    """The field under validation must be present and not empty"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None:
            return False

        if isinstance(value, str):
            return value.strip() != ""

        if isinstance(value, (list, dict, tuple)):
            return len(value) > 0

        # For numbers, False is considered empty but 0 is not
        if isinstance(value, bool):
            return True

        return True

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field is required."