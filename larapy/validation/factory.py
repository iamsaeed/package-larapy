"""Validation factory implementation"""

from typing import Dict, List, Any, Optional, Union, Callable
from .contracts import ValidationFactory as ValidationFactoryContract, ValidatorContract
from .validator import Validator


class ValidationFactory(ValidationFactoryContract):
    """Factory for creating validator instances"""

    def __init__(self):
        """Create a new validation factory instance"""
        self.extensions: Dict[str, Callable] = {}
        self.implicit_extensions: Dict[str, Callable] = {}
        self.replacers: Dict[str, Callable] = {}

    def make(self, data: Dict[str, Any], rules: Dict[str, Union[str, List]],
             messages: Optional[Dict[str, str]] = None,
             attributes: Optional[Dict[str, str]] = None) -> ValidatorContract:
        """Create a new validator instance"""
        validator = Validator(data, rules, messages, attributes)

        # Apply any custom extensions
        validator.extensions.update(self.extensions)
        validator.implicit_extensions.update(self.implicit_extensions)
        validator.replacers.update(self.replacers)

        return validator

    def extend(self, rule: str, extension: Callable, message: Optional[str] = None) -> None:
        """Register a custom validator extension"""
        self.extensions[rule] = extension

        # Add default message if provided
        if message and hasattr(extension, '_default_message'):
            extension._default_message = message

    def extend_implicit(self, rule: str, extension: Callable, message: Optional[str] = None) -> None:
        """Register a custom implicit validator extension"""
        self.implicit_extensions[rule] = extension

        # Add default message if provided
        if message and hasattr(extension, '_default_message'):
            extension._default_message = message

    def replacer(self, rule: str, replacer: Callable) -> None:
        """Register a custom message replacer"""
        self.replacers[rule] = replacer

    def validate(self, data: Dict[str, Any], rules: Dict[str, Union[str, List]],
                 messages: Optional[Dict[str, str]] = None,
                 attributes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Validate data and return validated attributes"""
        validator = self.make(data, rules, messages, attributes)
        return validator.validate()

    def make_partial(self, data: Dict[str, Any], rules: Dict[str, Union[str, List]],
                     messages: Optional[Dict[str, str]] = None,
                     attributes: Optional[Dict[str, str]] = None) -> ValidatorContract:
        """Create a validator that only validates present fields"""
        # Add 'sometimes' rule to all fields that don't already have it
        processed_rules = {}
        for field, field_rules in rules.items():
            if isinstance(field_rules, str):
                field_rules = field_rules.split('|')
            elif not isinstance(field_rules, list):
                field_rules = [field_rules]

            # Check if 'sometimes' is already present
            has_sometimes = any(
                (isinstance(rule, str) and rule == 'sometimes') or
                (hasattr(rule, '__class__') and rule.__class__.__name__ == 'Sometimes')
                for rule in field_rules
            )

            if not has_sometimes:
                field_rules = ['sometimes'] + field_rules

            processed_rules[field] = field_rules

        return self.make(data, processed_rules, messages, attributes)