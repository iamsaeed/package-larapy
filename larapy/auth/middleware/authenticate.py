"""
Authentication Middleware

Provides Laravel-style authentication middleware with guard support.
Handles user authentication, guest middleware, and remember me functionality.
"""

from typing import Optional, Dict, Any
from flask import request, session, g, abort, redirect, url_for, current_app
from functools import wraps


class Authenticate:
    """
    Middleware for requiring authentication
    """
    
    def __init__(self, guards: Optional[list] = None):
        """
        Initialize authentication middleware
        
        Args:
            guards: List of guards to check (defaults to ['web'])
        """
        self.guards = guards or ['web']
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check authentication for each guard
            authenticated = False
            
            for guard in self.guards:
                if self._check_guard(guard):
                    authenticated = True
                    break
            
            if not authenticated:
                return self._handle_unauthenticated()
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def _check_guard(self, guard: str) -> bool:
        """
        Check if user is authenticated with specific guard
        
        Args:
            guard: Guard name to check
            
        Returns:
            bool: True if authenticated
        """
        if guard == 'web':
            return self._check_web_auth()
        elif guard == 'api':
            return self._check_api_auth()
        
        return False
    
    def _check_web_auth(self) -> bool:
        """
        Check web session authentication
        
        Returns:
            bool: True if authenticated via web session
        """
        user_id = session.get('user_id')
        if not user_id:
            return False
        
        # Load user and set in Flask's g object
        user = self._load_user(user_id)
        if user:
            g.user = user
            return True
        
        return False
    
    def _check_api_auth(self) -> bool:
        """
        Check API token authentication
        
        Returns:
            bool: True if authenticated via API token
        """
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            user = self._load_user_by_token(token)
            if user:
                g.user = user
                return True
        
        # Check api_token parameter
        token = request.args.get('api_token') or request.form.get('api_token')
        if token:
            user = self._load_user_by_token(token)
            if user:
                g.user = user
                return True
        
        return False
    
    def _load_user(self, user_id: int):
        """
        Load user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        # This would typically load from database
        # For now, return a simple dict representation
        # In real implementation, integrate with your User model
        try:
            # Import and use the User model
            from app.Models.User import User
            return User.find(user_id)
        except ImportError:
            # Fallback if User model not available
            return {'id': user_id, 'name': 'User'}
    
    def _load_user_by_token(self, token: str):
        """
        Load user by API token
        
        Args:
            token: API token
            
        Returns:
            User object or None
        """
        try:
            # Import and use the User model
            from app.Models.User import User
            return User.where('api_token', token).first()
        except ImportError:
            return None
    
    def _handle_unauthenticated(self):
        """
        Handle unauthenticated request
        
        Returns:
            Response for unauthenticated user
        """
        # For API requests, return JSON error
        if self._is_api_request():
            abort(401, description={'message': 'Unauthenticated'})
        
        # For web requests, redirect to login
        login_url = url_for('login') if hasattr(current_app, 'url_map') else '/login'
        return redirect(login_url)
    
    def _is_api_request(self) -> bool:
        """
        Check if this is an API request
        
        Returns:
            bool: True if API request
        """
        return (request.path.startswith('/api/') or 
                request.headers.get('Accept', '').startswith('application/json') or
                'api' in self.guards)


class RedirectIfAuthenticated:
    """
    Middleware for redirecting authenticated users (guest middleware)
    """
    
    def __init__(self, guards: Optional[list] = None, redirect_to: str = '/dashboard'):
        """
        Initialize guest middleware
        
        Args:
            guards: List of guards to check
            redirect_to: Where to redirect authenticated users
        """
        self.guards = guards or ['web']
        self.redirect_to = redirect_to
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            for guard in self.guards:
                if self._check_guard(guard):
                    return redirect(self.redirect_to)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def _check_guard(self, guard: str) -> bool:
        """
        Check if user is authenticated with specific guard
        
        Args:
            guard: Guard name to check
            
        Returns:
            bool: True if authenticated
        """
        if guard == 'web':
            return 'user_id' in session
        elif guard == 'api':
            auth_header = request.headers.get('Authorization', '')
            return auth_header.startswith('Bearer ')
        
        return False


class VerifyPassword:
    """
    Middleware for verifying password before sensitive operations
    """
    
    def __init__(self, timeout: int = 10800):  # 3 hours default
        """
        Initialize password verification middleware
        
        Args:
            timeout: Password confirmation timeout in seconds
        """
        self.timeout = timeout
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self._password_confirmed_recently():
                return self._redirect_to_password_confirm()
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def _password_confirmed_recently(self) -> bool:
        """
        Check if password was confirmed recently
        
        Returns:
            bool: True if password confirmed within timeout
        """
        import time
        last_confirmed = session.get('password_confirmed_at', 0)
        return (time.time() - last_confirmed) < self.timeout
    
    def _redirect_to_password_confirm(self):
        """
        Redirect to password confirmation page
        
        Returns:
            Redirect response
        """
        confirm_url = url_for('password.confirm') if hasattr(current_app, 'url_map') else '/password/confirm'
        return redirect(confirm_url)


# Authentication helper functions
def auth_user():
    """
    Get the currently authenticated user
    
    Returns:
        User object or None
    """
    return getattr(g, 'user', None)


def auth_check() -> bool:
    """
    Check if user is authenticated
    
    Returns:
        bool: True if authenticated
    """
    return hasattr(g, 'user') and g.user is not None


def auth_id():
    """
    Get the current user's ID
    
    Returns:
        User ID or None
    """
    user = auth_user()
    return user.id if user else None


def auth_guest() -> bool:
    """
    Check if user is a guest (not authenticated)
    
    Returns:
        bool: True if guest
    """
    return not auth_check()


def auth_login(user, remember: bool = False):
    """
    Log in a user
    
    Args:
        user: User object
        remember: Enable remember me functionality
    """
    session['user_id'] = user.id
    session.permanent = remember
    g.user = user
    
    # Regenerate session ID for security
    session.regenerate()


def auth_logout():
    """
    Log out the current user
    """
    session.pop('user_id', None)
    session.pop('password_confirmed_at', None)
    if hasattr(g, 'user'):
        delattr(g, 'user')


def confirm_password():
    """
    Mark password as recently confirmed
    """
    import time
    session['password_confirmed_at'] = time.time()


# Convenience decorators
def auth_required(guards: Optional[list] = None):
    """
    Decorator for routes requiring authentication
    
    Args:
        guards: List of guards to check
        
    Returns:
        Authentication decorator
    """
    return Authenticate(guards)


def guest_only(guards: Optional[list] = None, redirect_to: str = '/dashboard'):
    """
    Decorator for routes accessible only to guests
    
    Args:
        guards: List of guards to check
        redirect_to: Where to redirect authenticated users
        
    Returns:
        Guest middleware decorator
    """
    return RedirectIfAuthenticated(guards, redirect_to)


def password_confirm(timeout: int = 10800):
    """
    Decorator for routes requiring recent password confirmation
    
    Args:
        timeout: Password confirmation timeout in seconds
        
    Returns:
        Password verification decorator
    """
    return VerifyPassword(timeout)


# Pre-configured middleware instances
auth_middleware = Authenticate(['web'])
api_auth_middleware = Authenticate(['api'])
guest_middleware = RedirectIfAuthenticated(['web'])
password_middleware = VerifyPassword()