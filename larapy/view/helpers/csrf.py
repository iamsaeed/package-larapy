"""
CSRF Template Helpers

Provides template functions for CSRF protection.
"""

from flask import Markup
from larapy.security.csrf_token_service import CSRFTokenService


def csrf_token() -> str:
    """
    Get the current CSRF token
    
    Returns:
        str: The current CSRF token
    """
    service = CSRFTokenService()
    return service.get_token()


def csrf_field() -> Markup:
    """
    Generate a hidden CSRF token field for forms
    
    Returns:
        Markup: HTML hidden input field with CSRF token
    """
    token = csrf_token()
    return Markup(f'<input type="hidden" name="_token" value="{token}">')


def csrf() -> Markup:
    """
    Alias for csrf_field() - generates CSRF hidden input
    
    Returns:
        Markup: HTML hidden input field with CSRF token
    """
    return csrf_field()


def csrf_meta() -> Markup:
    """
    Generate a meta tag for CSRF token (for AJAX requests)
    
    Returns:
        Markup: HTML meta tag with CSRF token
    """
    token = csrf_token()
    return Markup(f'<meta name="csrf-token" content="{token}">')


# Template globals to be registered with Jinja2
csrf_template_globals = {
    'csrf_token': csrf_token,
    'csrf_field': csrf_field,
    'csrf': csrf,
    'csrf_meta': csrf_meta,
}