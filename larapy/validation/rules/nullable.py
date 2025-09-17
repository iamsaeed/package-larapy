"""Nullable validation rule"""

from typing import Any, List
from .base_rule import ImplicitRule


class Nullable(ImplicitRule):
    """The field under validation may be null"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        # Nullable always passes, it just affects presence validation
        return True

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return ""  # Nullable doesn't generate error messages