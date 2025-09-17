"""Sometimes validation rule"""

from typing import Any, List
from .base_rule import ImplicitRule


class Sometimes(ImplicitRule):
    """The field under validation will be validated only if it is present"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        # Sometimes always passes, it just affects when validation occurs
        return True

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return ""  # Sometimes doesn't generate error messages