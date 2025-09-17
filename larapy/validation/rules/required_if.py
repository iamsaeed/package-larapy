"""Required if validation rule"""

from typing import Dict, Any, Optional, List
from .base_rule import ImplicitRule, DataAwareRule


class RequiredIfRule(ImplicitRule, DataAwareRule):
    """Validates that a field is required if another field has a specific value"""

    def __init__(self, field: str, *values):
        super().__init__()
        self.name = 'required_if'
        self.field = field
        self.values = list(values)

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if field is required based on another field's value"""
        other_value = self.data.get(self.field)

        # Convert other_value to string for comparison
        other_value_str = str(other_value) if other_value is not None else None

        # Check if the other field has one of the specified values
        is_required = any(str(val) == other_value_str for val in self.values)

        if not is_required:
            return True  # Field is not required, so it passes

        # Field is required, check if it has a value
        return self._has_value(value)

    def _has_value(self, value: Any) -> bool:
        """Check if a value is considered present"""
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == '':
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute field is required when :field is :value.'