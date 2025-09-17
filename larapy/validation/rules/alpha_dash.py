"""Alpha dash validation rule"""

import re
from typing import Dict, Any, Optional, List
from .base_rule import BaseRule


class AlphaDashRule(BaseRule):
    """Validates that a field contains only alphanumeric characters, dashes, and underscores"""

    def __init__(self):
        super().__init__()
        self.name = 'alpha_dash'

    def passes(self, attribute: str, value: Any, parameters: Optional[List[str]] = None) -> bool:
        """Check if value contains only alphanumeric characters, dashes, and underscores"""
        if not isinstance(value, str):
            return False

        # Only alphabetic, numeric, dash, and underscore characters (a-z, A-Z, 0-9, -, _)
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', value))

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return 'The :attribute must only contain letters, numbers, dashes and underscores.'