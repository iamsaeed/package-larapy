"""Between validation rule"""

from typing import Any, List, Union
from .base_rule import BaseRule


class Between(BaseRule):
    """The field under validation must have a size between the given min and max"""

    def __init__(self, min_value: Union[int, float], max_value: Union[int, float]):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        size = self._get_size(value)
        if size is None:
            return False

        return self.min_value <= size <= self.max_value

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
        return "The :attribute field must be between :min and :max."

    def __str__(self) -> str:
        """String representation for rule serialization"""
        return f"between:{self.min_value},{self.max_value}"