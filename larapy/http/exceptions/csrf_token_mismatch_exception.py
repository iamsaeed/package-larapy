"""
CSRF Token Mismatch Exception

Exception thrown when CSRF token validation fails.
"""

from flask import abort


class CSRFTokenMismatchException(Exception):
    """
    Exception raised when CSRF token validation fails
    """
    
    def __init__(self, message: str = "CSRF token mismatch"):
        self.message = message
        super().__init__(self.message)
        # Return 419 status code (Laravel's CSRF error code)
        abort(419, description=message)