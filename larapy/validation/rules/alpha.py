"""Alpha validation rule"""

import re
from typing import Dict, Any, Optional, List
from .base_rule import BaseRule


class AlphaRule(BaseRule):
    """Validates that a field contains only alphabetic characters"""

    def __init__(self):
        super().__init__()
        self.name = 'alpha'

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if value contains only alphabetic characters"""
        if not isinstance(value, str):
            return False

        # Only alphabetic characters (a-z, A-Z) - no spaces, numbers, or special chars
        return bool(re.match(r'^[a-zA-Z]+$', value))

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute must only contain letters.'