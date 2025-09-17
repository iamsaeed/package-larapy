"""Different validation rule"""

from typing import Dict, Any, Optional, List
from .base_rule import DataAwareRule


class DifferentRule(DataAwareRule):
    """Validates that a field has a different value from another field"""

    def __init__(self, field: str):
        super().__init__()
        self.name = 'different'
        self.field = field

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if field has different value from another field"""
        other_value = self.data.get(self.field)

        # Convert both values to strings for comparison
        value_str = str(value) if value is not None else None
        other_value_str = str(other_value) if other_value is not None else None

        return value_str != other_value_str

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute and :field must be different.'