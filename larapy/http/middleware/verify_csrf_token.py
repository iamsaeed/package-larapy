"""
CSRF Token Verification Middleware

Provides Laravel-style CSRF protection for state-changing requests.
Validates tokens from forms, headers, and cookies.
"""

import hmac
import hashlib
import time
from typing import List, Optional
from flask import request, session, abort, current_app
from functools import wraps

from larapy.http.exceptions.csrf_token_mismatch_exception import CSRFTokenMismatchException
from larapy.security.csrf_token_service import CSRFTokenService


class VerifyCSRFToken:
    """
    CSRF Token Verification Middleware
    
    Validates CSRF tokens on state-changing requests to prevent
    cross-site request forgery attacks.
    """
    
    def __init__(self):
        self.except_routes: List[str] = []
        self.token_service = CSRFTokenService()
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if self.should_verify():
                if not self.verify_token():
                    raise CSRFTokenMismatchException("CSRF token mismatch")
            return f(*args, **kwargs)
        return decorated_function
    
    def should_verify(self) -> bool:
        """
        Determine if the request should be verified for CSRF
        """
        # Skip for safe methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return False
        
        # Skip for excluded routes
        if self.is_route_excluded():
            return False
        
        # Skip for JSON API requests with proper authentication
        if request.is_json and self.is_api_request():
            return False
            
        return True
    
    def is_route_excluded(self) -> bool:
        """
        Check if current route is in the exception list
        """
        current_path = request.path
        
        for pattern in self.except_routes:
            # Support wildcard patterns
            if pattern.endswith('*'):
                if current_path.startswith(pattern[:-1]):
                    return True
            elif current_path == pattern:
                return True
        return False
    
    def is_api_request(self) -> bool:
        """
        Check if this is an API request
        """
        return (request.path.startswith('/api/') or 
                request.headers.get('Accept', '').startswith('application/json'))
    
    def verify_token(self) -> bool:
        """
        Verify the CSRF token from various sources
        """
        # Get the session token
        session_token = self.token_service.get_session_token()
        if not session_token:
            return False
        
        # Get token from request
        request_token = self.get_token_from_request()
        if not request_token:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(
            session_token.encode('utf-8'),
            request_token.encode('utf-8')
        )
    
    def get_token_from_request(self) -> Optional[str]:
        """
        Get CSRF token from request (form field, headers, or cookie)
        """
        # Check form field first
        token = request.form.get('_token')
        if token:
            return token
        
        # Check X-CSRF-TOKEN header
        token = request.headers.get('X-CSRF-TOKEN')
        if token:
            return token
        
        # Check X-XSRF-TOKEN header (for JavaScript frameworks)
        token = request.headers.get('X-XSRF-TOKEN')
        if token:
            # Decrypt the cookie value if encrypted
            return self.decrypt_cookie_token(token)
        
        return None
    
    def decrypt_cookie_token(self, token: str) -> Optional[str]:
        """
        Decrypt token from XSRF-TOKEN cookie
        """
        try:
            # If we have encryption service, decrypt the cookie
            if hasattr(current_app, 'encrypter'):
                return current_app.encrypter.decrypt(token)
            return token
        except Exception:
            return None
    
    def except_routes(self, routes: List[str]):
        """
        Set routes to exclude from CSRF verification
        """
        self.except_routes = routes
        return self


# Create middleware instance
csrf_middleware = VerifyCSRFToken()