"""Base exception classes for Larapy"""

class LarapyException(Exception):
    """Base exception class for all Larapy exceptions"""
    status_code = 500
    message = "An error occurred"

    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return self.message