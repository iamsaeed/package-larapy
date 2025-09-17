"""IP address validation rule"""

import ipaddress
from typing import Any, List
from .base_rule import BaseRule


class Ip(BaseRule):
    """The field under validation must be an IP address"""

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        if value is None or value == "":
            return True  # Let required rule handle empty values

        if not isinstance(value, str):
            return False

        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return "The :attribute field must be a valid IP address."