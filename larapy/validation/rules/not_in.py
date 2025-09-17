"""Not In validation rule"""

from typing import Any, List
from .base_rule import BaseRule


class NotIn(BaseRule):
    """The field under validation must not be included in the given list of values"""

    def __init__(self, values: List[Any]):
        super().__init__()
        self.values = values

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        return value not in self.values

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The selected :attribute is invalid."

    def __str__(self) -> str:
        """String representation for rule serialization"""
        # Convert values to strings and escape quotes
        escaped_values = []
        for value in self.values:
            str_value = str(value)
            if '"' in str_value:
                str_value = str_value.replace('"', '""')
            escaped_values.append(f'"{str_value}"')

        return f"not_in:{','.join(escaped_values)}"