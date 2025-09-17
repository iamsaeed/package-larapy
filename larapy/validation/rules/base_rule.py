"""Base validation rule implementation"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from ..contracts import ValidationRule, DataAwareRule, ValidatorAwareRule


class BaseRule(ValidationRule):
    """Base implementation for validation rules"""

    def __init__(self):
        self.parameters: List[str] = []
        self.data: Optional[Dict[str, Any]] = None
        self.validator = None
        self._message: Optional[str] = None

    @abstractmethod
    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        pass

    def message(self) -> str:
        """Get the validation error message"""
        if self._message:
            return self._message
        return self.get_default_message()

    @abstractmethod
    def get_default_message(self) -> str:
        """Get the default validation error message"""
        pass

    def set_message(self, message: str) -> 'BaseRule':
        """Set a custom validation message"""
        self._message = message
        return self

    def get_attribute_value(self, data: Dict[str, Any], attribute: str) -> Any:
        """Get an attribute value from the data"""
        # Support dot notation for nested attributes
        keys = attribute.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def replace_placeholders(self, message: str, attribute: str, rule: str,
                           parameters: List[str] = None) -> str:
        """Replace placeholders in the validation message"""
        replacements = {
            ':attribute': attribute.replace('_', ' '),
            ':rule': rule,
        }

        # Add parameter replacements
        if parameters:
            for i, param in enumerate(parameters):
                replacements[f':value{i}'] = str(param)
                # Common parameter names
                if i == 0:
                    replacements[':value'] = str(param)
                    replacements[':min'] = str(param)
                    replacements[':max'] = str(param)
                    replacements[':size'] = str(param)
                elif i == 1:
                    replacements[':max'] = str(param)

        # Apply replacements
        for placeholder, replacement in replacements.items():
            message = message.replace(placeholder, replacement)

        return message

    def __str__(self) -> str:
        """String representation of the rule"""
        return self.__class__.__name__.lower()


class DataAwareRule(BaseRule, DataAwareRule):
    """Base rule that needs access to all validation data"""

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set the data under validation"""
        self.data = data


class ValidatorAwareRule(BaseRule, ValidatorAwareRule):
    """Base rule that needs access to the validator instance"""

    def set_validator(self, validator) -> None:
        """Set the current validator instance"""
        self.validator = validator


class ImplicitRule(BaseRule):
    """Base class for implicit rules that affect presence validation"""
    pass