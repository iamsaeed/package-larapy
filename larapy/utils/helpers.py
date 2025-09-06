"""
Helper functions for Larapy applications.
"""

import os
import re
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def snake_case(text: str) -> str:
    """
    Convert a string to snake_case.
    
    Args:
        text: Input string
        
    Returns:
        String in snake_case format
    """
    # Replace hyphens and spaces with underscores
    text = re.sub(r'[-\s]+', '_', text)
    # Insert underscores before uppercase letters
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    # Convert to lowercase
    return text.lower()


def camel_case(text: str) -> str:
    """
    Convert a string to camelCase.
    
    Args:
        text: Input string
        
    Returns:
        String in camelCase format
    """
    # Split on underscores, hyphens, and spaces
    words = re.split(r'[-_\s]+', text.lower())
    if not words:
        return text
    
    # First word lowercase, rest title case
    return words[0] + ''.join(word.capitalize() for word in words[1:])


def pascal_case(text: str) -> str:
    """
    Convert a string to PascalCase.
    
    Args:
        text: Input string
        
    Returns:
        String in PascalCase format
    """
    # Split on underscores, hyphens, and spaces
    words = re.split(r'[-_\s]+', text.lower())
    # Capitalize all words
    return ''.join(word.capitalize() for word in words)


def kebab_case(text: str) -> str:
    """
    Convert a string to kebab-case.
    
    Args:
        text: Input string
        
    Returns:
        String in kebab-case format
    """
    # Replace underscores and spaces with hyphens
    text = re.sub(r'[_\s]+', '-', text)
    # Insert hyphens before uppercase letters
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', text)
    # Convert to lowercase
    return text.lower()


def deep_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a value from nested dictionary using dot notation.
    
    Args:
        data: Dictionary to search in
        key_path: Dot-separated key path (e.g., 'user.profile.name')
        default: Default value if key is not found
        
    Returns:
        Value at key path or default
    """
    keys = key_path.split('.')
    value = data
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def deep_set(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set a value in nested dictionary using dot notation.
    
    Args:
        data: Dictionary to modify
        key_path: Dot-separated key path (e.g., 'user.profile.name')
        value: Value to set
    """
    keys = key_path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def safe_join(*args: Union[str, Path]) -> Path:
    """
    Safely join path components.
    
    Args:
        *args: Path components to join
        
    Returns:
        Joined path
    """
    return Path(*args)


def flatten_dict(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        data: Dictionary to flatten
        separator: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    def _flatten(obj: Any, parent_key: str = '') -> Dict[str, Any]:
        items = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                items.extend(_flatten(value, new_key).items())
        else:
            return {parent_key: obj}
        
        return dict(items)
    
    return _flatten(data)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_env(key: str, default: Optional[str] = None, cast_type: type = str) -> Any:
    """
    Get environment variable with optional type casting.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        cast_type: Type to cast the value to
        
    Returns:
        Environment variable value cast to specified type
    """
    value = os.getenv(key, default)
    
    if value is None:
        return None
    
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        return int(value)
    elif cast_type == float:
        return float(value)
    
    return cast_type(value)


def is_empty(value: Any) -> bool:
    """
    Check if a value is considered empty.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is empty, False otherwise
    """
    if value is None:
        return True
    if isinstance(value, (str, list, dict, tuple, set)):
        return len(value) == 0
    return False


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator for retrying function calls.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between attempts in seconds
        
    Returns:
        Decorator function
    """
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    else:
                        raise last_exception
            
        return wrapper
    return decorator
