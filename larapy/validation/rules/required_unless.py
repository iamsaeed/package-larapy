"""Required unless validation rule"""

from typing import Dict, Any, Optional, List
from .base_rule import ImplicitRule, DataAwareRule


class RequiredUnlessRule(ImplicitRule, DataAwareRule):
    """Validates that a field is required unless another field has a specific value"""

    def __init__(self, field: str, *values):
        super().__init__()
        self.name = 'required_unless'
        self.field = field
        self.values = list(values)

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if field is required unless another field has specific value"""
        other_value = self.data.get(self.field)

        # Convert other_value to string for comparison
        other_value_str = str(other_value) if other_value is not None else None

        # Check if the other field has one of the specified values
        has_exception_value = any(str(val) == other_value_str for val in self.values)

        if has_exception_value:
            return True  # Field is not required due to exception, so it passes

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
        if len(self.values) == 1:
            return f'The :attribute field is required unless {self.field} is {self.values[0]}.'
        else:
            value_list = ', '.join(str(v) for v in self.values[:-1]) + f' or {self.values[-1]}'
            return f'The :attribute field is required unless {self.field} is {value_list}.'

    def __str__(self) -> str:
        """String representation for debugging"""
        return f"required_unless:{self.field},{','.join(str(v) for v in self.values)}"