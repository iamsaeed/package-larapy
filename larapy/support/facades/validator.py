"""Validator facade for easy access to validation"""

from .facade import Facade

class Validator(Facade):
    """Validator facade for easy access to validation services"""

    @classmethod
    def get_facade_accessor(cls):
        return 'validation'

    @classmethod
    def make(cls, data, rules, messages=None, attributes=None):
        """Create a new validator instance"""
        return cls.get_facade_root().make(data, rules, messages, attributes)

    @classmethod
    def validate(cls, data, rules, messages=None, attributes=None):
        """Validate data and return validated attributes"""
        return cls.get_facade_root().validate(data, rules, messages, attributes)

    @classmethod
    def extend(cls, rule, extension, message=None):
        """Register a custom validator extension"""
        return cls.get_facade_root().extend(rule, extension, message)

    @classmethod
    def extend_implicit(cls, rule, extension, message=None):
        """Register a custom implicit validator extension"""
        return cls.get_facade_root().extend_implicit(rule, extension, message)

    @classmethod
    def replacer(cls, rule, replacer):
        """Register a custom message replacer"""
        return cls.get_facade_root().replacer(rule, replacer)