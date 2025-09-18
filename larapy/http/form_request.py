"""Form Request base class"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Any, Optional
from flask import request
from ..validation.exceptions import ValidationException
from ..support.facades import Validator


class FormRequest(ABC):
    """
    Base class for form request validation
    
    Provides Laravel-style form request functionality including
    validation rules, authorization, and data preparation.
    """
    
    def __init__(self):
        self._request_data = None
        self._validated_data = None
    
    @abstractmethod
    def authorize(self) -> bool:
        """
        Determine if the user is authorized to make this request
        
        Returns:
            True if the user is authorized, False otherwise
        """
        pass
    
    @abstractmethod
    def rules(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get the validation rules that apply to the request
        
        Returns:
            Dictionary of validation rules
        """
        pass
    
    def messages(self) -> Dict[str, str]:
        """
        Get custom validation messages
        
        Returns:
            Dictionary of custom validation messages
        """
        return {}
    
    def attributes(self) -> Dict[str, str]:
        """
        Get custom attribute names for validation errors
        
        Returns:
            Dictionary of custom attribute names
        """
        return {}
    
    def prepare_for_validation(self):
        """
        Prepare the data for validation
        
        This method is called before validation occurs.
        Use it to modify or clean the input data.
        """
        pass
    
    def with_validator(self, validator):
        """
        Configure the validator instance
        
        Args:
            validator: The validator instance
        """
        pass
    
    def failed_validation(self, validator):
        """
        Handle a failed validation attempt
        
        Args:
            validator: The validator instance that failed
        """
        pass
    
    def validate_request(self) -> Dict[str, Any]:
        """
        Validate the request
        
        Returns:
            Dictionary of validated data
            
        Raises:
            ValidationException: If validation fails
            PermissionError: If authorization fails
        """
        # Check authorization first
        if not self.authorize():
            raise PermissionError("This action is unauthorized.")
        
        # Get request data
        self._request_data = self._get_request_data()
        
        # Prepare data for validation
        self.prepare_for_validation()
        
        # Get validation rules
        rules = self.rules()
        messages = self.messages()
        attributes = self.attributes()
        
        try:
            # Validate the request data
            self._validated_data = Validator.validate(
                self._request_data, 
                rules, 
                messages, 
                attributes
            )
            
            return self._validated_data
            
        except ValidationException as e:
            self.failed_validation(e.validator if hasattr(e, 'validator') else None)
            raise e
    
    def validated(self) -> Dict[str, Any]:
        """
        Get the validated data
        
        Returns:
            Dictionary of validated data
        """
        if self._validated_data is None:
            self.validate_request()
        
        return self._validated_data
    
    def input(self, key: str = None, default: Any = None) -> Any:
        """
        Get input data from the request
        
        Args:
            key: The key to retrieve (None for all data)
            default: Default value if key not found
            
        Returns:
            The input value or all input data
        """
        if self._request_data is None:
            self._request_data = self._get_request_data()
        
        if key is None:
            return self._request_data
        
        return self._request_data.get(key, default)
    
    def all(self) -> Dict[str, Any]:
        """
        Get all input data
        
        Returns:
            Dictionary of all input data
        """
        return self.input()
    
    def only(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get only specified keys from input
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary with only the specified keys
        """
        all_input = self.all()
        return {key: all_input.get(key) for key in keys if key in all_input}
    
    def except_keys(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get all input except specified keys
        
        Args:
            keys: List of keys to exclude
            
        Returns:
            Dictionary with all input except the specified keys
        """
        all_input = self.all()
        return {key: value for key, value in all_input.items() if key not in keys}
    
    def has(self, key: str) -> bool:
        """
        Check if input has a key
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self.all()
    
    def merge(self, data: Dict[str, Any]):
        """
        Merge additional data into the request
        
        Args:
            data: Dictionary of data to merge
        """
        if self._request_data is None:
            self._request_data = self._get_request_data()
        
        self._request_data.update(data)
    
    def user(self):
        """
        Get the authenticated user (if available)
        
        Returns:
            The authenticated user or None
        """
        # This would typically integrate with your auth system
        # For now, return None as a placeholder
        return None
    
    def _get_request_data(self) -> Dict[str, Any]:
        """
        Get data from the current Flask request
        
        Returns:
            Dictionary of request data
        """
        if not request:
            return {}

        # Combine form data, JSON data, and files
        data = {}

        # Add form data
        if request.form:
            data.update(request.form.to_dict())

        # Add JSON data
        if request.is_json and request.json:
            data.update(request.json)

        # Add query parameters
        if request.args:
            data.update(request.args.to_dict())

        # Add file uploads
        if request.files:
            data.update(request.files.to_dict())

        return data