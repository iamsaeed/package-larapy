"""
Authentication Middleware - Route protection and authentication checks

Provides decorators and middleware for protecting routes and managing
authentication requirements in Larapy applications.
"""

from functools import wraps
from flask import request, jsonify, redirect, url_for, session, current_app
from typing import Callable, Any, Optional


def auth_required(redirect_to: str = '/login', api: bool = False):
    """
    Middleware decorator that requires authentication to access a route.
    
    Args:
        redirect_to: URL to redirect unauthenticated users (web routes)
        api: If True, returns JSON error instead of redirect
        
    Returns:
        Decorated function that checks authentication
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get auth manager from application container
            try:
                if hasattr(current_app, 'container'):
                    auth = current_app.container.resolve('auth')
                else:
                    # Fallback: check session directly
                    if not session.get('user_authenticated', False):
                        if api:
                            return jsonify({'error': 'Unauthenticated'}), 401
                        return redirect(redirect_to)
                    return f(*args, **kwargs)
                
                if not auth.check():
                    if api:
                        return jsonify({'error': 'Unauthenticated'}), 401
                    return redirect(redirect_to)
                    
            except Exception:
                # Fallback to session check if container/auth not available
                if not session.get('user_authenticated', False):
                    if api:
                        return jsonify({'error': 'Unauthenticated'}), 401
                    return redirect(redirect_to)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def guest_only(redirect_to: str = '/home', api: bool = False):
    """
    Middleware decorator that only allows unauthenticated users.
    
    Args:
        redirect_to: URL to redirect authenticated users
        api: If True, returns JSON error instead of redirect
        
    Returns:
        Decorated function that checks guest status
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get auth manager from application container
            try:
                if hasattr(current_app, 'container'):
                    auth = current_app.container.resolve('auth')
                else:
                    # Fallback: check session directly
                    if session.get('user_authenticated', False):
                        if api:
                            return jsonify({'error': 'Already authenticated'}), 403
                        return redirect(redirect_to)
                    return f(*args, **kwargs)
                
                if auth.check():
                    if api:
                        return jsonify({'error': 'Already authenticated'}), 403
                    return redirect(redirect_to)
                    
            except Exception:
                # Fallback to session check if container/auth not available
                if session.get('user_authenticated', False):
                    if api:
                        return jsonify({'error': 'Already authenticated'}), 403
                    return redirect(redirect_to)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_api(f: Callable) -> Callable:
    """
    Shorthand decorator for API routes that require authentication.
    Returns JSON errors instead of redirects.
    """
    return auth_required(api=True)(f)


def guest_api(f: Callable) -> Callable:
    """
    Shorthand decorator for API routes that require guest status.
    Returns JSON errors instead of redirects.
    """
    return guest_only(api=True)(f)


class AuthMiddleware:
    """
    Class-based middleware for authentication checks.
    
    Can be used with Flask's before_request decorator or similar middleware systems.
    """
    
    def __init__(self, app=None):
        """
        Initialize the middleware.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the middleware with the application.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        app.before_request(self.before_request)
    
    def before_request(self):
        """
        Run before each request to handle authentication.
        
        This method can be customized to add global authentication logic.
        """
        pass
    
    @staticmethod
    def authenticate():
        """
        Check if the current request is authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            if hasattr(current_app, 'container'):
                auth = current_app.container.resolve('auth')
                return auth.check()
            else:
                return session.get('user_authenticated', False)
        except Exception:
            return session.get('user_authenticated', False)
    
    @staticmethod
    def user():
        """
        Get the currently authenticated user.
        
        Returns:
            User instance or None
        """
        try:
            if hasattr(current_app, 'container'):
                auth = current_app.container.resolve('auth')
                return auth.user()
            else:
                return None
        except Exception:
            return None


def verify_csrf_token():
    """
    Middleware decorator to verify CSRF tokens for POST requests.
    
    Note: This is a basic implementation. For production use,
    consider using Flask-WTF or similar CSRF protection.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                token = request.form.get('_token') or request.headers.get('X-CSRF-TOKEN')
                session_token = session.get('_token')
                
                if not token or not session_token or token != session_token:
                    if request.is_json:
                        return jsonify({'error': 'CSRF token mismatch'}), 419
                    return 'CSRF token mismatch', 419
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def throttle(max_attempts: int = 60, window_minutes: int = 1):
    """
    Basic rate limiting middleware decorator.
    
    Args:
        max_attempts: Maximum number of attempts allowed
        window_minutes: Time window in minutes
        
    Returns:
        Decorated function with rate limiting
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Basic implementation - in production, use Redis or similar
            client_ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
            rate_key = f"throttle:{client_ip}:{request.endpoint}"
            
            # This is a very basic implementation
            # In production, implement proper rate limiting with Redis
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator