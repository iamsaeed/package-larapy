"""Validation exceptions"""

from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
from ..exceptions.http import ValidationException as BaseValidationException
from .contracts import MessageBagContract
from .message_bag import MessageBag

if TYPE_CHECKING:
    from .contracts import ValidatorContract


class ValidationException(BaseValidationException):
    """Laravel-compatible validation exception with enhanced features."""

    def __init__(self, validator: 'ValidatorContract' = None, response: Optional[Any] = None,
                 error_bag: str = 'default', redirect_to: str = None):
        """Create a new validation exception instance"""
        self.validator = validator
        self.response = response
        self.error_bag = error_bag
        self.redirect_to = redirect_to
        self.status = 422
        self._with_input = None

        # Set the error messages
        if validator:
            self.errors = validator.errors().to_dict()
            
            # Get the first error message for the exception message
            messages = validator.errors()
            if messages.count() > 0:
                message = messages.first()
            else:
                message = 'The given data was invalid.'
        else:
            self.errors = {}
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

    def redirectTo(self, url: str) -> 'ValidationException':
        """Set the redirect URL (Laravel camelCase)"""
        self.redirect_to = url
        return self

    def redirect_to_url(self, url: str) -> 'ValidationException':
        """Set the redirect URL (Python snake_case)"""
        self.redirect_to = url
        return self

    def with_input(self, input_data: Dict[str, Any] = None) -> 'ValidationException':
        """Flash the input to the session"""
        self._with_input = input_data
        return self
    
    def withInput(self, input_data: Dict[str, Any] = None) -> 'ValidationException':
        """Flash the input to the session (Laravel camelCase)"""
        return self.with_input(input_data)
    
    def errorBag(self, bag: str) -> 'ValidationException':
        """Set the error bag name (Laravel camelCase)"""
        self.error_bag = bag
        return self
    
    def error_bag_name(self, bag: str) -> 'ValidationException':
        """Set the error bag name (Python snake_case)"""
        self.error_bag = bag
        return self
    
    @classmethod
    def withMessages(cls, messages: Dict[str, Union[str, List[str]]], 
                     error_bag: str = 'default', 
                     redirect_to: str = None) -> 'ValidationException':
        """
        Create ValidationException from message dictionary.
        
        Args:
            messages: Dictionary of field->message(s)
            error_bag: The error bag name
            redirect_to: URL to redirect to
            
        Returns:
            ValidationException: New exception instance
        """
        instance = cls(error_bag=error_bag, redirect_to=redirect_to)
        
        # Convert messages to the expected format
        errors = {}
        for field, field_messages in messages.items():
            if isinstance(field_messages, list):
                errors[field] = field_messages
            else:
                errors[field] = [field_messages]
        
        instance.errors = errors
        
        # Set exception message to first error
        if errors:
            first_field = next(iter(errors))
            first_message = errors[first_field][0]
            instance.args = (first_message,)
        
        return instance
    
    @classmethod
    def with_messages(cls, messages: Dict[str, Union[str, List[str]]], 
                      error_bag: str = 'default', 
                      redirect_to: str = None) -> 'ValidationException':
        """
        Create ValidationException from message dictionary (Python snake_case).
        
        Args:
            messages: Dictionary of field->message(s)
            error_bag: The error bag name
            redirect_to: URL to redirect to
            
        Returns:
            ValidationException: New exception instance
        """
        return cls.withMessages(messages, error_bag, redirect_to)
    
    def errors(self) -> Dict[str, List[str]]:
        """
        Get the error messages.
        
        Returns:
            Dict[str, List[str]]: Error messages grouped by field
        """
        return self.errors
    
    def get_errors(self) -> Dict[str, List[str]]:
        """
        Get the error messages (alternative method).
        
        Returns:
            Dict[str, List[str]]: Error messages grouped by field
        """
        return self.errors
    
    def getMessageBag(self) -> MessageBag:
        """
        Get errors as MessageBag instance.
        
        Returns:
            MessageBag: Message bag with all errors
        """
        bag = MessageBag()
        for field, messages in self.errors.items():
            for message in messages:
                bag.add(field, message)
        return bag
    
    def get_message_bag(self) -> MessageBag:
        """
        Get errors as MessageBag instance (Python snake_case).
        
        Returns:
            MessageBag: Message bag with all errors
        """
        return self.getMessageBag()