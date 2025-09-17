"""Validation exceptions"""

from typing import Dict, List, Optional, Any
from ..exceptions.http import ValidationException as BaseValidationException
from .contracts import MessageBagContract


class ValidationException(BaseValidationException):
    """The validation exception"""

    def __init__(self, validator: 'ValidatorContract', response: Optional[Any] = None,
                 error_bag: str = 'default'):
        """Create a new validation exception instance"""
        self.validator = validator
        self.response = response
        self.error_bag = error_bag
        self.status = 422

        # Set the error messages
        self.errors = validator.errors().to_dict()

        # Get the first error message for the exception message
        messages = validator.errors()
        if messages.count() > 0:
            message = messages.first()
        else:
            message = 'The given data was invalid.'

        super().__init__(self.errors, message)

    def errors_for_bag(self) -> Dict[str, List[str]]:
        """Get the errors for the error bag"""
        return self.errors

    def get_response(self):
        """Get the underlying response instance"""
        return self.response

    def status_code(self) -> int:
        """Get the status code"""
        return self.status

    def redirect_to(self, url: str) -> 'ValidationException':
        """Set the redirect URL"""
        # This would be used in web context
        self._redirect_to = url
        return self

    def with_input(self, input_data: Dict[str, Any] = None) -> 'ValidationException':
        """Flash the input to the session"""
        # This would be used in web context
        self._with_input = input_data
        return self