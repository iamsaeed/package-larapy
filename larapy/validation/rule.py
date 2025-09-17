"""Validation rule builder and utilities"""

from typing import List, Any, Union, Callable, Optional, Dict
from .rules.required import Required
from .rules.email import Email
from .rules.string import String
from .rules.integer import Integer
from .rules.numeric import Numeric
from .rules.boolean import Boolean
from .rules.array import Array
from .rules.in_rule import In
from .rules.not_in import NotIn
from .rules.min import Min
from .rules.max import Max
from .rules.between import Between
from .rules.size import Size
from .rules.url import Url
from .rules.ip import Ip
from .rules.uuid import Uuid
from .rules.date import Date
from .rules.nullable import Nullable
from .rules.sometimes import Sometimes
from .rules.confirmed import ConfirmedRule
from .rules.different import DifferentRule
from .rules.same import SameRule
from .rules.regex import RegexRule
from .rules.alpha import AlphaRule
from .rules.alpha_dash import AlphaDashRule
from .rules.alpha_num import AlphaNumRule
from .rules.required_if import RequiredIfRule


class Rule:
    """Static rule builder for fluent validation rule creation"""

    @staticmethod
    def required() -> Required:
        """Create a required rule"""
        return Required()

    @staticmethod
    def nullable() -> Nullable:
        """Create a nullable rule"""
        return Nullable()

    @staticmethod
    def sometimes() -> Sometimes:
        """Create a sometimes rule"""
        return Sometimes()

    @staticmethod
    def email() -> Email:
        """Create an email rule"""
        return Email()

    @staticmethod
    def string() -> String:
        """Create a string rule"""
        return String()

    @staticmethod
    def integer() -> Integer:
        """Create an integer rule"""
        return Integer()

    @staticmethod
    def numeric() -> Numeric:
        """Create a numeric rule"""
        return Numeric()

    @staticmethod
    def boolean() -> Boolean:
        """Create a boolean rule"""
        return Boolean()

    @staticmethod
    def array() -> Array:
        """Create an array rule"""
        return Array()

    @staticmethod
    def url() -> Url:
        """Create a URL rule"""
        return Url()

    @staticmethod
    def ip() -> Ip:
        """Create an IP address rule"""
        return Ip()

    @staticmethod
    def uuid() -> Uuid:
        """Create a UUID rule"""
        return Uuid()

    @staticmethod
    def date(format_string: Optional[str] = None) -> Date:
        """Create a date rule"""
        return Date(format_string)

    @staticmethod
    def in_list(values: Union[List[Any], Any]) -> In:
        """Create an 'in' rule"""
        if not isinstance(values, list):
            values = [values]
        return In(values)

    @staticmethod
    def not_in(values: Union[List[Any], Any]) -> NotIn:
        """Create a 'not in' rule"""
        if not isinstance(values, list):
            values = [values]
        return NotIn(values)

    @staticmethod
    def min(value: Union[int, float]) -> Min:
        """Create a minimum value rule"""
        return Min(value)

    @staticmethod
    def max(value: Union[int, float]) -> Max:
        """Create a maximum value rule"""
        return Max(value)

    @staticmethod
    def between(min_val: Union[int, float], max_val: Union[int, float]) -> Between:
        """Create a between rule"""
        return Between(min_val, max_val)

    @staticmethod
    def size(value: Union[int, float]) -> Size:
        """Create a size rule"""
        return Size(value)

    @staticmethod
    def confirmed() -> ConfirmedRule:
        """Create a confirmed rule"""
        return ConfirmedRule()

    @staticmethod
    def different(other_field: str) -> DifferentRule:
        """Create a different rule"""
        return DifferentRule(other_field)

    @staticmethod
    def same(other_field: str) -> SameRule:
        """Create a same rule"""
        return SameRule(other_field)

    @staticmethod
    def regex(pattern: str) -> RegexRule:
        """Create a regex rule"""
        return RegexRule(pattern)

    @staticmethod
    def alpha() -> AlphaRule:
        """Create an alpha rule"""
        return AlphaRule()

    @staticmethod
    def alpha_dash() -> AlphaDashRule:
        """Create an alpha dash rule"""
        return AlphaDashRule()

    @staticmethod
    def alpha_num() -> AlphaNumRule:
        """Create an alpha numeric rule"""
        return AlphaNumRule()

    # @staticmethod
    # def when(condition: Union[bool, Callable], rules: Union[str, List, 'ValidationRule'],
    #          default_rules: Union[str, List, 'ValidationRule'] = None) -> 'ConditionalRules':
    #     """Apply rules conditionally"""
    #     from .conditional_rules import ConditionalRules
    #     return ConditionalRules(condition, rules, default_rules)

    # Aliases for common rules (Laravel compatibility)
    @staticmethod
    def in_(values: Union[List[Any], Any]) -> In:
        """Alias for in_list (in is a Python keyword)"""
        return Rule.in_list(values)

    @staticmethod
    def required_if(field: str, *values: Any) -> RequiredIfRule:
        """Create a required if rule"""
        return RequiredIfRule(field, *values)

    # @staticmethod
    # def required_unless(other_field: str, value: Any) -> 'RequiredUnless':
    #     """Create a required unless rule"""
    #     from .rules.required_unless import RequiredUnless
    #     return RequiredUnless(other_field, value)

    # @staticmethod
    # def required_with(fields: Union[str, List[str]]) -> 'RequiredWith':
    #     """Create a required with rule"""
    #     from .rules.required_with import RequiredWith
    #     return RequiredWith(fields)

    # @staticmethod
    # def required_without(fields: Union[str, List[str]]) -> 'RequiredWithout':
    #     """Create a required without rule"""
    #     from .rules.required_without import RequiredWithout
    #     return RequiredWithout(fields)

    # @staticmethod
    # def exists(table: str, column: str = 'id') -> 'Exists':
    #     """Create an exists rule for database validation"""
    #     from .rules.exists import Exists
    #     return Exists(table, column)

    # @staticmethod
    # def unique(table: str, column: str = 'id') -> 'Unique':
    #     """Create a unique rule for database validation"""
    #     from .rules.unique import Unique
    #     return Unique(table, column)

    # File validation rules (to be implemented later)
    # @staticmethod
    # def file() -> 'File':
    #     """Create a file rule"""
    #     from .rules.file import File
    #     return File()

    # @staticmethod
    # def image() -> 'Image':
    #     """Create an image rule"""
    #     from .rules.image import Image
    #     return Image()

    # @staticmethod
    # def mimes(types: List[str]) -> 'Mimes':
    #     """Create a mimes rule"""
    #     from .rules.mimes import Mimes
    #     return Mimes(types)

    # @staticmethod
    # def mimetypes(types: List[str]) -> 'MimeTypes':
    #     """Create a mimetypes rule"""
    #     from .rules.mimetypes import MimeTypes
    #     return MimeTypes(types)