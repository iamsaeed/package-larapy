"""Date validation rule"""

from datetime import datetime
from typing import Any, List, Optional
from .base_rule import BaseRule


class Date(BaseRule):
    """The field under validation must be a valid date"""

    def __init__(self, format_string: Optional[str] = None):
        super().__init__()
        self.format_string = format_string

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        if not isinstance(value, str):
            return False

        if self.format_string:
            try:
                datetime.strptime(value, self.format_string)
                return True
            except ValueError:
                return False
        else:
            # Try common date formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%d-%m-%Y',
                '%m-%d-%Y'
            ]
            
            for fmt in formats:
                try:
                    datetime.strptime(value, fmt)
                    return True
                except ValueError:
                    continue
                    
            return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        if self.format_string:
            return f"The :attribute field must match the format {self.format_string}."
        return "The :attribute field must be a valid date."