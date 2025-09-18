"""
Security Headers Middleware

Adds security headers to responses including CSP, HSTS, X-Frame-Options, etc.
Helps protect against common web vulnerabilities.
"""

from typing import Dict, Any, Optional
from flask import make_response, current_app
from functools import wraps


class SecurityHeaders:
    """
    Middleware for adding security headers to responses
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize security headers middleware
        
        Args:
            config: Security headers configuration
        """
        self.config = config or self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default security headers configuration"""
        return {
            'x_frame_options': 'SAMEORIGIN',
            'x_content_type_options': 'nosniff',
            'x_xss_protection': '1; mode=block',
            'strict_transport_security': 'max-age=31536000; includeSubDomains',
            'content_security_policy': "default-src 'self'",
            'referrer_policy': 'strict-origin-when-cross-origin',
            'permissions_policy': 'geolocation=(), microphone=(), camera=()',
        }
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            return self._add_security_headers(response)
        
        return decorated_function
    
    def _add_security_headers(self, response):
        """
        Add security headers to response
        
        Args:
            response: Flask response object
            
        Returns:
            Response with security headers
        """
        # X-Frame-Options (Clickjacking protection)
        if 'x_frame_options' in self.config and self.config['x_frame_options']:
            response.headers['X-Frame-Options'] = self.config['x_frame_options']
        
        # X-Content-Type-Options (MIME type sniffing protection)
        if 'x_content_type_options' in self.config and self.config['x_content_type_options']:
            response.headers['X-Content-Type-Options'] = self.config['x_content_type_options']
        
        # X-XSS-Protection (Legacy XSS protection)
        if 'x_xss_protection' in self.config and self.config['x_xss_protection']:
            response.headers['X-XSS-Protection'] = self.config['x_xss_protection']
        
        # Strict-Transport-Security (HTTPS enforcement)
        if 'strict_transport_security' in self.config and self.config['strict_transport_security']:
            response.headers['Strict-Transport-Security'] = self.config['strict_transport_security']
        
        # Content-Security-Policy (XSS and injection protection)
        if 'content_security_policy' in self.config and self.config['content_security_policy']:
            response.headers['Content-Security-Policy'] = self.config['content_security_policy']
        
        # Referrer-Policy (Control referrer information)
        if 'referrer_policy' in self.config and self.config['referrer_policy']:
            response.headers['Referrer-Policy'] = self.config['referrer_policy']
        
        # Permissions-Policy (Feature policy)
        if 'permissions_policy' in self.config and self.config['permissions_policy']:
            response.headers['Permissions-Policy'] = self.config['permissions_policy']
        
        return response


class FrameGuard:
    """
    Specific middleware for X-Frame-Options header
    """
    
    def __init__(self, action: str = 'SAMEORIGIN'):
        """
        Initialize frame guard
        
        Args:
            action: Frame options action (DENY, SAMEORIGIN, ALLOW-FROM uri)
        """
        self.action = action
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['X-Frame-Options'] = self.action
            return response
        
        return decorated_function


class ContentSecurityPolicy:
    """
    Content Security Policy middleware
    """
    
    def __init__(self, policy: Optional[str] = None, report_only: bool = False):
        """
        Initialize CSP middleware
        
        Args:
            policy: CSP policy string
            report_only: If True, uses Content-Security-Policy-Report-Only header
        """
        self.policy = policy or "default-src 'self'"
        self.report_only = report_only
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            header_name = ('Content-Security-Policy-Report-Only' 
                          if self.report_only else 'Content-Security-Policy')
            response.headers[header_name] = self.policy
            
            return response
        
        return decorated_function


class StrictTransportSecurity:
    """
    HTTP Strict Transport Security (HSTS) middleware
    """
    
    def __init__(self, max_age: int = 31536000, include_subdomains: bool = True, 
                 preload: bool = False):
        """
        Initialize HSTS middleware
        
        Args:
            max_age: Max age in seconds (default: 1 year)
            include_subdomains: Include subdomains
            preload: Enable preload
        """
        self.max_age = max_age
        self.include_subdomains = include_subdomains
        self.preload = preload
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            hsts_value = f'max-age={self.max_age}'
            if self.include_subdomains:
                hsts_value += '; includeSubDomains'
            if self.preload:
                hsts_value += '; preload'
            
            response.headers['Strict-Transport-Security'] = hsts_value
            return response
        
        return decorated_function


# Helper functions for creating security middleware
def frame_guard(action: str = 'SAMEORIGIN'):
    """Create frame guard middleware"""
    return FrameGuard(action)


def csp(policy: Optional[str] = None, report_only: bool = False):
    """Create CSP middleware"""
    return ContentSecurityPolicy(policy, report_only)


def hsts(max_age: int = 31536000, include_subdomains: bool = True, preload: bool = False):
    """Create HSTS middleware"""
    return StrictTransportSecurity(max_age, include_subdomains, preload)


def security_headers(config: Optional[Dict[str, Any]] = None):
    """Create security headers middleware"""
    return SecurityHeaders(config)


# Pre-configured middleware instances
security_headers_middleware = SecurityHeaders()
frame_guard_middleware = FrameGuard()
csp_middleware = ContentSecurityPolicy()
hsts_middleware = StrictTransportSecurity()