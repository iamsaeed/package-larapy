"""Required with validation rule"""

from typing import Dict, Any, Optional, List
from .base_rule import ImplicitRule, DataAwareRule


class RequiredWithRule(ImplicitRule, DataAwareRule):
    """Validates that a field is required if any of the other specified fields are present"""

    def __init__(self, fields):
        super().__init__()
        self.name = 'required_with'
        # Handle both list and string input
        if isinstance(fields, list):
            # If it's a list, flatten it and split comma-separated values
            flattened = []
            for field in fields:
                if isinstance(field, str) and ',' in field:
                    flattened.extend(field.split(','))
                else:
                    flattened.append(str(field))
            self.fields = flattened
        elif isinstance(fields, str):
            self.fields = [f.strip() for f in fields.split(',')]
        else:
            self.fields = [str(fields)]

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if field is required based on presence of other fields"""
        # Check if any of the specified fields are present in the data
        any_field_present = any(self._is_field_present(field) for field in self.fields)

        if not any_field_present:
            return True  # Field is not required, so it passes

        # Field is required, check if it has a value
        return self._has_value(value)

    def _is_field_present(self, field: str) -> bool:
        """Check if a field is present in the data"""
        return field in self.data and self._has_value(self.data[field])

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
        if len(self.fields) == 1:
            return f'The :attribute field is required when {self.fields[0]} is present.'
        else:
            field_list = ', '.join(self.fields[:-1]) + f' or {self.fields[-1]}'
            return f'The :attribute field is required when {field_list} is present.'

    def __str__(self) -> str:
        """String representation for debugging"""
        return f"required_with:{','.join(self.fields)}"