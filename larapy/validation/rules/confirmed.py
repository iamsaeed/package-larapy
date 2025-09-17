"""Confirmed validation rule"""

from typing import Dict, Any, Optional, List
from .base_rule import DataAwareRule


class ConfirmedRule(DataAwareRule):
    """Validates that a field has a matching confirmation field"""

    def __init__(self):
        super().__init__()
        self.name = 'confirmed'

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if field has matching confirmation field"""
        if value is None:
            return True

        # Look for confirmation field (e.g., password_confirmation for password field)
        confirmation_field = f"{attribute}_confirmation"
        confirmation_value = self.data.get(confirmation_field)

        # Both values must exist and be equal
        return confirmation_value is not None and str(value) == str(confirmation_value)

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute confirmation does not match.'