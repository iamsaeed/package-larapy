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


# Response Helper Functions

def response(content: Any = '', status: int = 200, headers: Optional[Dict] = None):
    """
    Create a response or return ResponseFactory for chaining.
    
    Args:
        content: Response content (if None, returns factory for chaining)
        status: HTTP status code
        headers: Response headers
        
    Returns:
        Response object or ResponseFactory for chaining
    """
    from ..http.response_factory import ResponseFactory
    
    # If no arguments provided, return factory for Laravel-style chaining
    if content == '' and status == 200 and headers is None:
        return ResponseFactory()
    
    # Otherwise create response directly
    factory = ResponseFactory()
    return factory.make_response(content, status, headers)


def json_response(data: Any = None, status: int = 200, headers: Optional[Dict] = None, options: int = 0):
    """
    Create a JSON response.
    
    Args:
        data: Data to encode as JSON
        status: HTTP status code
        headers: Response headers
        options: JSON encoding options
        
    Returns:
        JsonResponse object
    """
    from ..http.json_response import JsonResponse
    return JsonResponse(data, status, headers, options)


def redirect(to: Optional[str] = None, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
    """
    Create a redirect response.
    
    Args:
        to: URL to redirect to
        status: HTTP status code
        headers: Response headers
        secure: Whether to use HTTPS
        
    Returns:
        RedirectResponse object
    """
    from ..routing.redirector import Redirector
    redirector = Redirector()
    
    if to is None:
        return redirector.back(status, headers)
    
    return redirector.to(to, status, headers, secure)


def back(status: int = 302, headers: Optional[Dict] = None, fallback: str = '/'):
    """
    Create a redirect back to previous page.
    
    Args:
        status: HTTP status code
        headers: Response headers
        fallback: Fallback URL if no previous page
        
    Returns:
        RedirectResponse object
    """
    from ..routing.redirector import Redirector
    redirector = Redirector()
    return redirector.back(status, headers, fallback)


def view(template: str, data: Optional[Dict] = None, status: int = 200, headers: Optional[Dict] = None):
    """
    Create a view response.
    
    Args:
        template: Template name
        data: Data to pass to template
        status: HTTP status code
        headers: Response headers
        
    Returns:
        Response object with rendered view
    """
    from ..http.response import Response
    return Response.view(template, data, status, headers)


def old(key: Optional[str] = None, default: Any = None):
    """
    Get old input data from session.
    
    Args:
        key: Input key to retrieve
        default: Default value if key not found
        
    Returns:
        Old input value or all old input
    """
    from flask import session
    
    old_input = session.get('_old_input', {})
    
    if key is None:
        return old_input
    
    return old_input.get(key, default)


def url(path: Optional[str] = None, parameters: Optional[Dict] = None, secure: Optional[bool] = None):
    """
    Generate a URL.
    
    Args:
        path: URL path
        parameters: URL parameters
        secure: Whether to use HTTPS
        
    Returns:
        Generated URL
    """
    from flask import request, url_for
    
    if path is None:
        path = '/'
    
    # If path starts with http/https, return as-is
    if path.startswith(('http://', 'https://')):
        return path
    
    # Build URL
    base_url = request.host_url if request else 'http://localhost'
    
    if secure is True:
        base_url = base_url.replace('http://', 'https://')
    elif secure is False:
        base_url = base_url.replace('https://', 'http://')
    
    if path.startswith('/'):
        url = base_url.rstrip('/') + path
    else:
        url = base_url.rstrip('/') + '/' + path
    
    # Add parameters if provided
    if parameters:
        from urllib.parse import urlencode
        url += '?' + urlencode(parameters)
    
    return url


def route(name: str, parameters: Optional[Dict] = None, absolute: bool = True):
    """
    Generate a URL for a named route.
    
    Args:
        name: Route name
        parameters: Route parameters
        absolute: Whether to generate absolute URL
        
    Returns:
        Generated URL
    """
    from flask import url_for
    
    try:
        if parameters:
            return url_for(name, _external=absolute, **parameters)
        else:
            return url_for(name, _external=absolute)
    except:
        # Fallback if route not found
        return '/' if not absolute else url('/')


def asset(path: str, secure: Optional[bool] = None):
    """
    Generate a URL for an asset.
    
    Args:
        path: Asset path
        secure: Whether to use HTTPS
        
    Returns:
        Asset URL
    """
    return url(f'/assets/{path.lstrip("/")}', secure=secure)


def request_helper(key: Optional[str] = None, default: Any = None):
    """
    Get request data.
    
    Args:
        key: Request key to retrieve
        default: Default value if key not found
        
    Returns:
        Request value or all request data
    """
    from flask import request
    
    if not request:
        return default if key else {}
    
    # Get data from various sources
    data = {}
    
    # Form data
    if hasattr(request, 'form'):
        data.update(request.form.to_dict())
    
    # JSON data
    if hasattr(request, 'json') and request.json:
        data.update(request.json)
    
    # Query parameters
    if hasattr(request, 'args'):
        data.update(request.args.to_dict())
    
    if key is None:
        return data
    
    return data.get(key, default)


def session_helper(key: Optional[str] = None, default: Any = None):
    """
    Get or set session data.
    
    Args:
        key: Session key
        default: Default value if key not found
        
    Returns:
        Session value or all session data
    """
    from flask import session
    
    if key is None:
        return dict(session)
    
    return session.get(key, default)


def flash(key: str, value: Any):
    """
    Flash data to session.
    
    Args:
        key: Flash key
        value: Flash value
    """
    from flask import session
    session[f'_flash.{key}'] = value


def get_flashed(key: str, default: Any = None):
    """
    Get flashed data and remove from session.
    
    Args:
        key: Flash key
        default: Default value if key not found
        
    Returns:
        Flashed value
    """
    from flask import session
    return session.pop(f'_flash.{key}', default)


def csrf_token():
    """
    Get CSRF token.
    
    Returns:
        CSRF token string
    """
    from flask import session
    import secrets
    
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    
    return session['_csrf_token']


# Laravel helper aliases for compatibility
request = request_helper  # Laravel uses 'request()' not 'request_helper()'
session = session_helper  # Laravel uses 'session()' not 'session_helper()'
