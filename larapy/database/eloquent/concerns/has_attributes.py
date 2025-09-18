"""Has Attributes concern for Eloquent models"""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class HasAttributes:
    """
    Provides attribute management functionality for Eloquent models
    """

    def __init__(self, attributes: Dict[str, Any] = None):
        # Model attributes
        self.attributes = attributes or {}
        self.original = {}
        self.changes = {}
        self.casts = getattr(self, 'casts', {})
        self.dates = getattr(self, 'dates', [])
        self.date_format = getattr(self, 'date_format', '%Y-%m-%d %H:%M:%S')

    def get_attribute(self, key: str) -> Any:
        """Get an attribute value"""
        if not self.has_get_mutator(key):
            return self._get_attribute_value(key)

        # Call the mutator
        mutator_method = f"get_{key}_attribute"
        value = self._get_attribute_value(key)
        return getattr(self, mutator_method)(value)

    def _get_attribute_value(self, key: str) -> Any:
        """Get the raw attribute value"""
        value = self.attributes.get(key)

        # Cast the attribute if needed
        if self.has_cast(key):
            return self.cast_attribute(key, value)

        # Handle date attributes
        if key in self.get_dates() and value is not None:
            return self.as_datetime(value)

        return value

    def set_attribute(self, key: str, value: Any):
        """Set an attribute value"""
        # Call the mutator if it exists
        if self.has_set_mutator(key):
            mutator_method = f"set_{key}_attribute"
            getattr(self, mutator_method)(value)
            return

        # Handle date attributes
        if key in self.get_dates() and value is not None:
            value = self.from_datetime(value)

        # Cast the attribute if needed
        if self.has_cast(key):
            value = self.cast_attribute(key, value)

        self.attributes[key] = value

    def has_get_mutator(self, key: str) -> bool:
        """Determine if a get mutator exists for an attribute"""
        method_name = f"get_{key}_attribute"
        return hasattr(self, method_name) and callable(getattr(self, method_name))

    def has_set_mutator(self, key: str) -> bool:
        """Determine if a set mutator exists for an attribute"""
        method_name = f"set_{key}_attribute"
        return hasattr(self, method_name) and callable(getattr(self, method_name))

    def has_cast(self, key: str) -> bool:
        """Determine if an attribute should be cast"""
        return key in self.casts

    def cast_attribute(self, key: str, value: Any) -> Any:
        """Cast an attribute to a specific type"""
        if value is None:
            return value

        cast_type = self.casts.get(key)

        if cast_type == 'int' or cast_type == 'integer':
            return int(value)
        elif cast_type == 'float' or cast_type == 'double':
            return float(value)
        elif cast_type == 'string':
            return str(value)
        elif cast_type == 'bool' or cast_type == 'boolean':
            return bool(value)
        elif cast_type == 'array' or cast_type == 'json':
            if isinstance(value, str):
                return json.loads(value)
            return value
        elif cast_type == 'object':
            if isinstance(value, str):
                return json.loads(value)
            return value
        elif cast_type == 'collection':
            # Would return a Collection object in full implementation
            return list(value) if value else []
        elif cast_type == 'date':
            return self.as_date(value)
        elif cast_type == 'datetime':
            return self.as_datetime(value)
        elif cast_type == 'timestamp':
            return self.as_timestamp(value)

        return value

    def get_dates(self) -> List[str]:
        """Get the attributes that should be mutated to dates"""
        dates = getattr(self, 'dates', [])
        
        if getattr(self, 'timestamps', False):
            dates.extend([
                getattr(self, 'created_at', 'created_at'),
                getattr(self, 'updated_at', 'updated_at')
            ])

        return dates

    def as_datetime(self, value: Any) -> Optional[datetime]:
        """Return a datetime instance from a value"""
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.strptime(value, self.date_format)
            except ValueError:
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue

        return None

    def as_date(self, value: Any) -> Optional[datetime]:
        """Return a date instance from a value"""
        dt = self.as_datetime(value)
        return dt.date() if dt else None

    def as_timestamp(self, value: Any) -> Optional[int]:
        """Return a timestamp from a value"""
        dt = self.as_datetime(value)
        return int(dt.timestamp()) if dt else None

    def from_datetime(self, value: Any) -> str:
        """Convert a datetime to a storable string"""
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.strftime(self.date_format)

        if isinstance(value, str):
            return value

        return str(value)

    def get_attributes(self) -> Dict[str, Any]:
        """Get all the current attributes on the model"""
        return self.attributes

    def set_raw_attributes(self, attributes: Dict[str, Any], sync: bool = False):
        """Set the raw attributes on the model"""
        self.attributes = attributes

        if sync:
            self.sync_original()

    def get_original(self, key: str = None, default: Any = None) -> Any:
        """Get the original value of an attribute"""
        if key is None:
            return self.original

        return self.original.get(key, default)

    def get_dirty(self) -> Dict[str, Any]:
        """Get the attributes that have been changed since last sync"""
        dirty = {}

        for key, value in self.attributes.items():
            if not self._original_is_equivalent(key):
                dirty[key] = value

        return dirty

    def is_dirty(self, attributes: Union[str, List[str]] = None) -> bool:
        """Determine if the model or any of the given attributes are dirty"""
        if attributes is None:
            return len(self.get_dirty()) > 0

        if isinstance(attributes, str):
            attributes = [attributes]

        for attribute in attributes:
            if not self._original_is_equivalent(attribute):
                return True

        return False

    def is_clean(self, attributes: Union[str, List[str]] = None) -> bool:
        """Determine if the model or all the given attributes are clean"""
        return not self.is_dirty(attributes)

    def was_changed(self, attributes: Union[str, List[str]] = None) -> bool:
        """Determine if the model or any of the given attributes were changed"""
        if attributes is None:
            return len(self.changes) > 0

        if isinstance(attributes, str):
            attributes = [attributes]

        for attribute in attributes:
            if attribute in self.changes:
                return True

        return False

    def get_changes(self) -> Dict[str, Any]:
        """Get the attributes that were changed"""
        return self.changes

    def sync_original(self):
        """Sync the original attributes with the current"""
        self.original = self.attributes.copy()

    def sync_changes(self):
        """Sync the changed attributes"""
        self.changes = self.get_dirty()

    def _original_is_equivalent(self, key: str) -> bool:
        """Determine if the new and old values for a key are equivalent"""
        current = self.attributes.get(key)
        original = self.original.get(key)

        # Handle None values
        if current is None and original is None:
            return True

        if current is None or original is None:
            return False

        # Handle numeric comparisons
        if isinstance(current, (int, float)) and isinstance(original, (int, float)):
            return current == original

        # Handle string comparisons
        return str(current) == str(original)

    def __getattr__(self, key: str) -> Any:
        """Dynamically access attributes"""
        if key in self.attributes:
            return self.get_attribute(key)

        # Check if it's a relationship
        if hasattr(self, f"{key}_relation"):
            relation_method = getattr(self, f"{key}_relation")
            return relation_method()

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any):
        """Dynamically set attributes"""
        # Internal attributes should be set directly
        if key.startswith('_') or key in ['attributes', 'original', 'changes', 'casts', 'dates', 'date_format']:
            super().__setattr__(key, value)
            return

        # Check if it's a fillable attribute
        if hasattr(self, 'is_fillable') and self.is_fillable(key):
            self.set_attribute(key, value)
        else:
            super().__setattr__(key, value)