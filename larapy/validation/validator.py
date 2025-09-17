"""Core validator implementation"""

import re
from typing import Dict, List, Any, Optional, Union, Callable, Type
from .contracts import ValidatorContract, ValidationRule, DataAwareRule, ValidatorAwareRule
from .message_bag import MessageBag
from .exceptions import ValidationException
from .rules.base_rule import BaseRule, ImplicitRule


class Validator(ValidatorContract):
    """Core validation engine"""

    def __init__(self, data: Dict[str, Any], rules: Dict[str, Union[str, List]],
                 messages: Optional[Dict[str, str]] = None,
                 attributes: Optional[Dict[str, str]] = None):
        """Create a new validator instance"""
        self.data = data
        self.initial_rules = rules
        self.custom_messages = messages or {}
        self.custom_attributes = attributes or {}

        # Internal state
        self.message_bag = MessageBag()
        self.failed_rules: Dict[str, List[str]] = {}
        self.valid_data: Dict[str, Any] = {}
        self.after_callbacks: List[Callable] = []

        # Parse rules
        self.rules = self._parse_rules(rules)

        # Custom rule extensions
        self.extensions: Dict[str, Callable] = {}
        self.implicit_extensions: Dict[str, Callable] = {}
        self.replacers: Dict[str, Callable] = {}

        # Default validation messages
        self.default_messages = self._get_default_messages()

    def validate(self) -> Dict[str, Any]:
        """Run the validator's rules against its data"""
        if self.fails():
            raise ValidationException(self)

        return self.validated()

    def validated(self) -> Dict[str, Any]:
        """Get the attributes and values that were validated"""
        if self.fails():
            raise ValidationException(self)

        return self.valid_data.copy()

    def fails(self) -> bool:
        """Determine if the data fails the validation rules"""
        return not self.passes()

    def passes(self) -> bool:
        """Determine if the data passes the validation rules"""
        self.message_bag = MessageBag()
        self.failed_rules = {}
        self.valid_data = {}

        # Validate each field
        for attribute, rules in self.rules.items():
            self._validate_attribute(attribute, rules)

        # Run after callbacks
        for callback in self.after_callbacks:
            callback(self)

        return self.message_bag.is_empty()

    def failed(self) -> Dict[str, List[str]]:
        """Get the failed validation rules"""
        return self.failed_rules.copy()

    def sometimes(self, attribute: Union[str, List[str]], rules: Union[str, List],
                  callback: Callable) -> 'Validator':
        """Add conditions to a given field based on a callback"""
        if isinstance(attribute, str):
            attributes = [attribute]
        else:
            attributes = attribute

        for attr in attributes:
            if callback(self.data):
                if attr not in self.rules:
                    self.rules[attr] = []

                parsed_rules = self._parse_rules_for_attribute(rules)
                self.rules[attr].extend(parsed_rules)

        return self

    def after(self, callback: Union[Callable, str]) -> 'Validator':
        """Add an after validation callback"""
        if isinstance(callback, str):
            # Convert string callback to actual callable if needed
            # This could be expanded to support class@method syntax
            pass

        if callable(callback):
            self.after_callbacks.append(callback)

        return self

    def errors(self) -> MessageBag:
        """Get all of the validation error messages"""
        return self.message_bag

    def _validate_attribute(self, attribute: str, rules: List[Union[str, ValidationRule]]):
        """Validate a single attribute"""
        value = self._get_attribute_value(attribute)

        # Track if the attribute is present
        present = self._is_present(attribute, value)

        # Check if validation should stop early
        if not present and not self._has_implicit_rule(rules):
            return

        for rule in rules:
            if isinstance(rule, str):
                rule_instance = self._parse_string_rule(rule)
            else:
                rule_instance = rule

            if not self._validate_rule(attribute, value, rule_instance, present):
                # Add to failed rules
                rule_name = str(rule_instance)
                if attribute not in self.failed_rules:
                    self.failed_rules[attribute] = []
                self.failed_rules[attribute].append(rule_name)

                # Check if we should stop validating this attribute
                if self._should_stop_validating(rule_instance):
                    break
            else:
                # Rule passed, add to valid data if present
                if present:
                    self.valid_data[attribute] = value

    def _validate_rule(self, attribute: str, value: Any, rule: ValidationRule, present: bool) -> bool:
        """Validate a single rule"""
        # Set up rule context if needed
        if isinstance(rule, DataAwareRule):
            rule.set_data(self.data)

        if isinstance(rule, ValidatorAwareRule):
            rule.set_validator(self)

        # Check if rule passes
        try:
            passes = rule.passes(attribute, value)
        except Exception:
            passes = False

        if not passes:
            # Add error message
            message = self._get_error_message(attribute, rule)
            self.message_bag.add(attribute, message)

        return passes

    def _get_attribute_value(self, attribute: str) -> Any:
        """Get the value of an attribute from the data"""
        # Support dot notation
        keys = attribute.split('.')
        value = self.data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def _is_present(self, attribute: str, value: Any) -> bool:
        """Determine if an attribute is present"""
        # Check if the attribute exists in the data
        keys = attribute.split('.')
        current = self.data

        for key in keys[:-1]:
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]

        if not isinstance(current, dict):
            return False

        final_key = keys[-1]
        return final_key in current

    def _has_implicit_rule(self, rules: List[Union[str, ValidationRule]]) -> bool:
        """Check if the rules contain an implicit rule"""
        for rule in rules:
            if isinstance(rule, str):
                rule_name = rule.split(':')[0]
                if rule_name in ['required', 'required_if', 'required_unless', 'required_with', 'required_without']:
                    return True
            elif isinstance(rule, ImplicitRule):
                return True
        return False

    def _should_stop_validating(self, rule: ValidationRule) -> bool:
        """Determine if validation should stop after this rule fails"""
        # Stop after required, nullable, or sometimes rules fail
        rule_name = str(rule)
        return rule_name in ['required', 'nullable', 'sometimes']

    def _parse_rules(self, rules: Dict[str, Union[str, List]]) -> Dict[str, List[ValidationRule]]:
        """Parse validation rules into rule instances"""
        parsed = {}

        for attribute, rule_set in rules.items():
            parsed[attribute] = self._parse_rules_for_attribute(rule_set)

        return parsed

    def _parse_rules_for_attribute(self, rule_set: Union[str, List]) -> List[ValidationRule]:
        """Parse rules for a single attribute"""
        if isinstance(rule_set, str):
            rule_set = rule_set.split('|')
        elif not isinstance(rule_set, list):
            rule_set = [rule_set]

        parsed_rules = []
        for rule in rule_set:
            if isinstance(rule, str):
                parsed_rules.append(self._parse_string_rule(rule))
            elif isinstance(rule, ValidationRule):
                parsed_rules.append(rule)
            else:
                # Convert to string and parse
                parsed_rules.append(self._parse_string_rule(str(rule)))

        return parsed_rules

    def _parse_string_rule(self, rule_string: str) -> ValidationRule:
        """Parse a string rule into a rule instance"""
        # Split rule name and parameters
        parts = rule_string.split(':', 1)
        rule_name = parts[0]
        parameters = parts[1].split(',') if len(parts) > 1 else []

        # Handle built-in rules
        rule_class = self._get_rule_class(rule_name)
        if rule_class:
            return self._instantiate_rule(rule_class, parameters)

        # Handle custom extensions
        if rule_name in self.extensions:
            return CustomRule(rule_name, self.extensions[rule_name], parameters)

        # Unknown rule - create a generic rule that always fails
        return UnknownRule(rule_name)

    def _get_rule_class(self, rule_name: str) -> Optional[Type[ValidationRule]]:
        """Get the rule class for a rule name"""
        # Map rule names to classes
        rule_map = {
            'required': 'Required',
            'nullable': 'Nullable',
            'sometimes': 'Sometimes',
            'email': 'Email',
            'string': 'String',
            'integer': 'Integer',
            'numeric': 'Numeric',
            'boolean': 'Boolean',
            'array': 'Array',
            'url': 'Url',
            'ip': 'Ip',
            'uuid': 'Uuid',
            'date': 'Date',
            'in': 'In',
            'not_in': 'NotIn',
            'min': 'Min',
            'max': 'Max',
            'between': 'Between',
            'size': 'Size',
            'confirmed': 'ConfirmedRule',
            'required_if': 'RequiredIfRule',
            'same': 'SameRule',
            'different': 'DifferentRule',
            'alpha': 'AlphaRule',
            'alpha_num': 'AlphaNumRule',
            'alpha_dash': 'AlphaDashRule',
            'regex': 'RegexRule',
        }

        if rule_name in rule_map:
            try:
                module_name = f"larapy.validation.rules.{rule_name}" if rule_name not in ['in', 'not_in'] else f"larapy.validation.rules.{rule_name}_rule" if rule_name == 'in' else "larapy.validation.rules.not_in"
                module = __import__(module_name, fromlist=[rule_map[rule_name]])
                return getattr(module, rule_map[rule_name])
            except (ImportError, AttributeError):
                pass

        return None

    def _instantiate_rule(self, rule_class: Type[ValidationRule], parameters: List[str]) -> ValidationRule:
        """Instantiate a rule with its parameters"""
        try:
            # Handle rules that need parameters
            if rule_class.__name__ in ['Min', 'Max', 'Size']:
                if parameters:
                    return rule_class(float(parameters[0]))
                return rule_class(0)
            elif rule_class.__name__ == 'Between':
                if len(parameters) >= 2:
                    return rule_class(float(parameters[0]), float(parameters[1]))
                return rule_class(0, 0)
            elif rule_class.__name__ in ['In', 'NotIn']:
                return rule_class(parameters)
            elif rule_class.__name__ == 'Date':
                format_str = parameters[0] if parameters else None
                return rule_class(format_str)
            elif rule_class.__name__ == 'RequiredIfRule':
                if len(parameters) >= 2:
                    field = parameters[0]
                    values = parameters[1:]
                    return rule_class(field, *values)
                elif parameters:
                    return rule_class(parameters[0], None)
                return rule_class('', None)
            elif rule_class.__name__ in ['SameRule', 'DifferentRule']:
                if parameters:
                    return rule_class(parameters[0])
                return rule_class('')
            elif rule_class.__name__ == 'RegexRule':
                if parameters:
                    return rule_class(parameters[0])
                return rule_class('')
            else:
                return rule_class()
        except Exception:
            return rule_class()

    def _get_error_message(self, attribute: str, rule: ValidationRule) -> str:
        """Get the error message for a failed rule"""
        rule_name = str(rule)

        # Check for custom message
        message_key = f"{attribute}.{rule_name}"
        if message_key in self.custom_messages:
            message = self.custom_messages[message_key]
        elif rule_name in self.custom_messages:
            message = self.custom_messages[rule_name]
        elif hasattr(rule, 'message') and rule.message():
            message = rule.message()
        else:
            message = f"The {attribute} field is invalid."

        # Replace placeholders
        return self._replace_message_placeholders(message, attribute, rule)

    def _replace_message_placeholders(self, message: str, attribute: str, rule: ValidationRule) -> str:
        """Replace placeholders in error messages"""
        # Get display name for attribute
        display_name = self.custom_attributes.get(attribute, attribute.replace('_', ' '))

        message = message.replace(':attribute', display_name)
        message = message.replace(':rule', str(rule))

        # Handle rule-specific replacements
        if hasattr(rule, 'min_value'):
            message = message.replace(':min', str(rule.min_value))
        if hasattr(rule, 'max_value'):
            message = message.replace(':max', str(rule.max_value))
        if hasattr(rule, 'size_value'):
            message = message.replace(':size', str(rule.size_value))
        if hasattr(rule, 'values'):
            message = message.replace(':values', ', '.join(map(str, rule.values)))

        return message

    def _get_default_messages(self) -> Dict[str, str]:
        """Get default validation messages"""
        return {
            'required': 'The :attribute field is required.',
            'email': 'The :attribute field must be a valid email address.',
            'string': 'The :attribute field must be a string.',
            'integer': 'The :attribute field must be an integer.',
            'numeric': 'The :attribute field must be numeric.',
            'boolean': 'The :attribute field must be true or false.',
            'array': 'The :attribute field must be an array.',
            'url': 'The :attribute field must be a valid URL.',
            'ip': 'The :attribute field must be a valid IP address.',
            'uuid': 'The :attribute field must be a valid UUID.',
            'date': 'The :attribute field must be a valid date.',
            'in': 'The selected :attribute is invalid.',
            'not_in': 'The selected :attribute is invalid.',
            'min': 'The :attribute field must be at least :min.',
            'max': 'The :attribute field may not be greater than :max.',
            'between': 'The :attribute field must be between :min and :max.',
            'size': 'The :attribute field must be :size.',
        }


class CustomRule(BaseRule):
    """Wrapper for custom validation rules"""

    def __init__(self, name: str, extension: Callable, parameters: List[str]):
        super().__init__()
        self.name = name
        self.extension = extension
        self.parameters = parameters

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Determine if the validation rule passes"""
        return self.extension(attribute, value, self.parameters)

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return f"The :attribute field is invalid."

    def __str__(self) -> str:
        """String representation"""
        return self.name


class UnknownRule(BaseRule):
    """Placeholder for unknown validation rules"""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def passes(self, attribute: str, value: Any, parameters: List[str] = None) -> bool:
        """Unknown rules always fail"""
        return False

    def get_default_message(self) -> str:
        """Get the default validation error message"""
        return f"The :attribute field has an unknown validation rule: {self.name}."

    def __str__(self) -> str:
        """String representation"""
        return self.name