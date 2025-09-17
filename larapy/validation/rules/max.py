"""Max validation rule"""

from typing import Any, List, Union
from .base_rule import BaseRule


class Max(BaseRule):
    """The field under validation must not exceed a maximum value"""

    def __init__(self, max_value: Union[int, float]):
        super().__init__()
        self.max_value = max_value

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        size = self._get_size(value)
        if size is None:
            return False

        return size <= self.max_value

    def _get_size(self, value: Any) -> Union[float, None]:
        """Get the size of a value for comparison"""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return float(len(value))

        if isinstance(value, (list, dict, tuple)):
            return float(len(value))

        return None

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field may not be greater than :max."

    def __str__(self) -> str:
        """String representation for rule serialization"""
        return f"max:{self.max_value}"