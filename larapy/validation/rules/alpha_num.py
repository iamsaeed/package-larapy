"""Alpha numeric validation rule"""

import re
from typing import Dict, Any, Optional, List
from .base_rule import BaseRule


class AlphaNumRule(BaseRule):
    """Validates that a field contains only alphanumeric characters"""

    def __init__(self):
        super().__init__()
        self.name = 'alpha_num'

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if value contains only alphanumeric characters"""
        if not isinstance(value, str):
            return False

        # Only alphabetic and numeric characters (a-z, A-Z, 0-9)
        return bool(re.match(r'^[a-zA-Z0-9]+$', value))

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute must only contain letters and numbers.'