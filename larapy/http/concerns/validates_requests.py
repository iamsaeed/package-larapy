"""Request validation trait for controllers"""

from typing import Dict, List, Any, Optional, Union
from flask import request
from ...validation.exceptions import ValidationException
from ...support.facades import Validator


class ValidatesRequests:
    """Mixin/trait for adding validation methods to controllers"""

    def validate(self, request_data: Optional[Dict[str, Any]] = None,
                 rules: Optional[Dict[str, Union[str, List]]] = None,
                 messages: Optional[Dict[str, str]] = None,
                 attributes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Validate the request data"""
        if request_data is None:
            request_data = self._get_request_data()

        if rules is None:
            raise ValueError("Validation rules are required")

        return Validator.validate(request_data, rules, messages, attributes)

    def validate_with(self, validator, request_data: Optional[Dict[str, Any]] = None):
        """Run the validation routine against the given validator"""
        if request_data is None:
            request_data = self._get_request_data()

        if isinstance(validator, dict):
            # If validator is a rules dictionary, create a validator instance
            return Validator.validate(request_data, validator)
        else:
            # Assume it's already a validator instance
            return validator.validate()

    def validate_with_bag(self, error_bag: str, request_data: Dict[str, Any],
                          rules: Dict[str, Union[str, List]],
                          messages: Optional[Dict[str, str]] = None,
                          attributes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Validate the request with a named error bag"""
        try:
            return self.validate(request_data, rules, messages, attributes)
        except ValidationException as e:
            e.error_bag = error_bag
            raise e
    
    def validateWithBag(self, error_bag: str, request_data: Dict[str, Any],
                        rules: Dict[str, Union[str, List]],
                        messages: Optional[Dict[str, str]] = None,
                        attributes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Validate the request with a named error bag (Laravel camelCase)"""
        return self.validate_with_bag(error_bag, request_data, rules, messages, attributes)

    def _get_request_data(self) -> Dict[str, Any]:
        """Get data from the current request"""
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

    def validation_factory(self):
        """Get the validation factory instance"""
        # This would typically resolve from the service container
        # For now, we'll use the facade
        return Validator.get_facade_root()


# Example base controller that includes validation
class Controller(ValidatesRequests):
    """Base controller class with validation capabilities"""

    def __init__(self):
        # Initialize any controller-specific setup
        pass

    def validate_request(self, rules: Dict[str, Union[str, List]],
                        messages: Optional[Dict[str, str]] = None,
                        attributes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Convenience method to validate the current request"""
        return self.validate(None, rules, messages, attributes)