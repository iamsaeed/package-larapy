"""Validation contracts and interfaces"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union


class ValidationFactory(ABC):
    """Validation factory contract"""

    @abstractmethod
    def make(self, data: Dict[str, Any], rules: Dict[str, Union[str, List]],
             messages: Optional[Dict[str, str]] = None,
             attributes: Optional[Dict[str, str]] = None) -> 'ValidatorContract':
        """Create a new validator instance"""
        pass

    @abstractmethod
    def extend(self, rule: str, extension: Callable, message: Optional[str] = None) -> None:
        """Register a custom validator extension"""
        pass

    @abstractmethod
    def extend_implicit(self, rule: str, extension: Callable, message: Optional[str] = None) -> None:
        """Register a custom implicit validator extension"""
        pass

    @abstractmethod
    def replacer(self, rule: str, replacer: Callable) -> None:
        """Register a custom message replacer"""
        pass


class ValidatorContract(ABC):
    """Validator contract"""

    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """Run the validator's rules against its data"""
        pass

    @abstractmethod
    def validated(self) -> Dict[str, Any]:
        """Get the attributes and values that were validated"""
        pass

    @abstractmethod
    def fails(self) -> bool:
        """Determine if the data fails the validation rules"""
        pass

    @abstractmethod
    def failed(self) -> Dict[str, List[str]]:
        """Get the failed validation rules"""
        pass

    @abstractmethod
    def sometimes(self, attribute: Union[str, List[str]], rules: Union[str, List],
                  callback: Callable) -> 'ValidatorContract':
        """Add conditions to a given field based on a callback"""
        pass

    @abstractmethod
    def after(self, callback: Union[Callable, str]) -> 'ValidatorContract':
        """Add an after validation callback"""
        pass

    @abstractmethod
    def errors(self) -> 'MessageBagContract':
        """Get all of the validation error messages"""
        pass


class MessageBagContract(ABC):
    """Message bag contract"""

    @abstractmethod
    def add(self, key: str, message: str) -> None:
        """Add a message to the bag"""
        pass

    @abstractmethod
    def merge(self, messages: Union['MessageBagContract', Dict[str, List[str]]]) -> None:
        """Merge another message bag or dictionary into this bag"""
        pass

    @abstractmethod
    def has(self, key: Optional[str] = None) -> bool:
        """Check if the bag has any messages for a key"""
        pass

    @abstractmethod
    def first(self, key: Optional[str] = None, format_string: Optional[str] = None) -> Optional[str]:
        """Get the first message from the bag for a key"""
        pass

    @abstractmethod
    def get(self, key: str, format_string: Optional[str] = None) -> List[str]:
        """Get all messages for a key"""
        pass

    @abstractmethod
    def all(self, format_string: Optional[str] = None) -> Dict[str, List[str]]:
        """Get all messages"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get the number of messages in the bag"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, List[str]]:
        """Convert the message bag to a dictionary"""
        pass


class ValidationRule(ABC):
    """Base validation rule contract"""

    @abstractmethod
    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        pass

    @abstractmethod
    def message(self) -> str:
        """Get the validation error message"""
        pass


class ImplicitRule(ValidationRule):
    """Contract for implicit validation rules (affect presence validation)"""
    pass


class DataAwareRule(ValidationRule):
    """Contract for rules that need access to all validation data"""

    @abstractmethod
    def set_data(self, data: Dict[str, Any]) -> None:
        """Set the data under validation"""
        pass


class ValidatorAwareRule(ValidationRule):
    """Contract for rules that need access to the validator instance"""

    @abstractmethod
    def set_validator(self, validator: ValidatorContract) -> None:
        """Set the current validator instance"""
        pass