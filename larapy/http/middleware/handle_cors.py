"""
CORS (Cross-Origin Resource Sharing) Middleware

Handles CORS requests including preflight OPTIONS requests.
Supports configurable origins, methods, headers, and credentials.
"""

from typing import List, Dict, Any, Optional, Union
from flask import request, make_response, current_app
from functools import wraps
import re


class HandleCors:
    """
    Middleware for handling CORS requests
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CORS middleware
        
        Args:
            config: CORS configuration dictionary
        """
        self.config = config or self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default CORS configuration"""
        return {
            'paths': ['api/*'],
            'allowed_origins': ['*'],
            'allowed_methods': ['*'],
            'allowed_headers': ['*'],
            'exposed_headers': [],
            'max_age': 0,
            'supports_credentials': False,
        }
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if CORS should be applied to this path
            if not self._should_handle_cors():
                return f(*args, **kwargs)
            
            # Handle preflight request
            if request.method == 'OPTIONS':
                return self._handle_preflight_request()
            
            # Handle actual request
            response = make_response(f(*args, **kwargs))
            return self._add_cors_headers(response)
        
        return decorated_function
    
    def _should_handle_cors(self) -> bool:
        """
        Check if CORS should be handled for current request path
        
        Returns:
            bool: True if CORS should be handled
        """
        current_path = request.path
        
        for pattern in self.config['paths']:
            if self._match_path_pattern(current_path, pattern):
                return True
        
        return False
    
    def _match_path_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if path matches pattern (supports wildcards)
        
        Args:
            path: Request path
            pattern: Pattern to match against
            
        Returns:
            bool: True if path matches pattern
        """
        if pattern == '*':
            return True
        
        if pattern.endswith('*'):
            return path.startswith(pattern[:-1])
        
        return path == pattern
    
    def _handle_preflight_request(self):
        """
        Handle CORS preflight OPTIONS request
        
        Returns:
            Response for preflight request
        """
        response = make_response('')
        
        # Add CORS headers
        self._add_cors_headers(response)
        
        # Add preflight-specific headers
        if self.config['max_age'] > 0:
            response.headers['Access-Control-Max-Age'] = str(self.config['max_age'])
        
        # Handle requested method
        requested_method = request.headers.get('Access-Control-Request-Method')
        if requested_method and self._is_method_allowed(requested_method):
            response.headers['Access-Control-Allow-Methods'] = self._get_allowed_methods()
        
        # Handle requested headers
        requested_headers = request.headers.get('Access-Control-Request-Headers')
        if requested_headers:
            allowed_headers = self._get_allowed_headers()
            if allowed_headers:
                response.headers['Access-Control-Allow-Headers'] = allowed_headers
        
        return response
    
    def _add_cors_headers(self, response):
        """
        Add CORS headers to response
        
        Args:
            response: Flask response object
            
        Returns:
            Response with CORS headers
        """
        # Access-Control-Allow-Origin
        origin = self._get_allowed_origin()
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        
        # Access-Control-Allow-Credentials
        if self.config['supports_credentials']:
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # Access-Control-Expose-Headers
        exposed_headers = self._get_exposed_headers()
        if exposed_headers:
            response.headers['Access-Control-Expose-Headers'] = exposed_headers
        
        # Vary header for proper caching
        vary_headers = []
        if '*' not in self.config['allowed_origins']:
            vary_headers.append('Origin')
        
        if vary_headers:
            existing_vary = response.headers.get('Vary', '')
            if existing_vary:
                vary_headers = [existing_vary] + vary_headers
            response.headers['Vary'] = ', '.join(vary_headers)
        
        return response
    
    def _get_allowed_origin(self) -> Optional[str]:
        """
        Get allowed origin for current request
        
        Returns:
            str: Allowed origin or None
        """
        request_origin = request.headers.get('Origin')
        allowed_origins = self.config['allowed_origins']
        
        # If wildcard is allowed
        if '*' in allowed_origins:
            if self.config['supports_credentials'] and request_origin:
                # Can't use wildcard with credentials, return specific origin
                return request_origin
            return '*'
        
        # Check if request origin is in allowed list
        if request_origin in allowed_origins:
            return request_origin
        
        # Check for pattern matching
        for origin_pattern in allowed_origins:
            if self._match_origin_pattern(request_origin, origin_pattern):
                return request_origin
        
        return None
    
    def _match_origin_pattern(self, origin: Optional[str], pattern: str) -> bool:
        """
        Check if origin matches pattern
        
        Args:
            origin: Request origin
            pattern: Origin pattern
            
        Returns:
            bool: True if origin matches pattern
        """
        if not origin:
            return False
        
        if pattern.startswith('*.'):
            # Subdomain wildcard: *.example.com
            domain = pattern[2:]
            return origin.endswith('.' + domain) or origin == domain
        
        return origin == pattern
    
    def _is_method_allowed(self, method: str) -> bool:
        """
        Check if HTTP method is allowed
        
        Args:
            method: HTTP method
            
        Returns:
            bool: True if method is allowed
        """
        allowed_methods = self.config['allowed_methods']
        return '*' in allowed_methods or method in allowed_methods
    
    def _get_allowed_methods(self) -> str:
        """
        Get comma-separated list of allowed methods
        
        Returns:
            str: Allowed methods string
        """
        allowed_methods = self.config['allowed_methods']
        
        if '*' in allowed_methods:
            return 'GET, HEAD, PUT, PATCH, POST, DELETE, OPTIONS'
        
        return ', '.join(allowed_methods)
    
    def _get_allowed_headers(self) -> str:
        """
        Get comma-separated list of allowed headers
        
        Returns:
            str: Allowed headers string
        """
        allowed_headers = self.config['allowed_headers']
        
        if '*' in allowed_headers:
            # Return requested headers if wildcard
            requested_headers = request.headers.get('Access-Control-Request-Headers')
            return requested_headers or ''
        
        return ', '.join(allowed_headers)
    
    def _get_exposed_headers(self) -> str:
        """
        Get comma-separated list of exposed headers
        
        Returns:
            str: Exposed headers string
        """
        exposed_headers = self.config['exposed_headers']
        return ', '.join(exposed_headers) if exposed_headers else ''


# Helper function to create CORS middleware with config
def cors(config: Optional[Dict[str, Any]] = None):
    """
    Create CORS middleware with configuration
    
    Args:
        config: CORS configuration
        
    Returns:
        CORS middleware decorator
    """
    return HandleCors(config)


# Pre-configured CORS middleware
cors_middleware = HandleCors()