"""
AuthManager - Core authentication manager for Larapy

Handles user authentication, session management, and user retrieval.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, current_app
from typing import Optional, Dict, Any


class AuthManager:
    """
    Core authentication manager that handles login, logout, and user management.
    """
    
    def __init__(self, app=None):
        """
        Initialize the AuthManager.
        
        Args:
            app: The application instance
        """
        self.app = app
        self._user_model = None
        self._user_provider = None
        
    def set_user_model(self, model_class):
        """
        Set the User model class for authentication.
        
        Args:
            model_class: The User model class
        """
        self._user_model = model_class
        return self
        
    def attempt(self, credentials: Dict[str, str]) -> bool:
        """
        Attempt to authenticate a user with the given credentials.
        
        Args:
            credentials: Dictionary containing 'email' and 'password'
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._user_model:
            raise RuntimeError("User model not set. Call set_user_model() first.")
            
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            return False
            
        # Find user by email
        user = self._user_model.where('email', email).first()
        
        if not user:
            return False
            
        # Check password
        if hasattr(user, 'verify_password'):
            password_valid = user.verify_password(password)
        else:
            password_valid = check_password_hash(user.password, password)
            
        if password_valid:
            self.login(user)
            return True
            
        return False
    
    def login(self, user, remember: bool = False):
        """
        Log in a user by storing their ID in the session.
        
        Args:
            user: User model instance
            remember: Whether to remember the user (for future implementation)
            
        Returns:
            User: The logged-in user
        """
        session['user_id'] = user.id
        session['user_authenticated'] = True
        
        if remember:
            session.permanent = True
            
        return user
    
    def login_using_id(self, user_id: int, remember: bool = False):
        """
        Log in a user by their ID.
        
        Args:
            user_id: The user's ID
            remember: Whether to remember the user
            
        Returns:
            User or None: The logged-in user or None if not found
        """
        if not self._user_model:
            raise RuntimeError("User model not set. Call set_user_model() first.")
            
        user = self._user_model.find(user_id)
        if user:
            return self.login(user, remember)
        return None
    
    def logout(self):
        """
        Log out the current user by clearing the session.
        """
        session.pop('user_id', None)
        session.pop('user_authenticated', None)
        session.permanent = False
    
    def user(self):
        """
        Get the currently authenticated user.
        
        Returns:
            User or None: The authenticated user or None if not logged in
        """
        if not self.check():
            return None
            
        user_id = session.get('user_id')
        if not user_id or not self._user_model:
            return None
            
        return self._user_model.find(user_id)
    
    def id(self) -> Optional[int]:
        """
        Get the ID of the currently authenticated user.
        
        Returns:
            int or None: The user's ID or None if not authenticated
        """
        return session.get('user_id')
    
    def check(self) -> bool:
        """
        Check if a user is currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return session.get('user_authenticated', False) and 'user_id' in session
    
    def guest(self) -> bool:
        """
        Check if the current user is a guest (not authenticated).
        
        Returns:
            bool: True if guest, False if authenticated
        """
        return not self.check()
    
    def once(self, credentials: Dict[str, str]) -> bool:
        """
        Log a user in for a single request without affecting the session.
        
        Args:
            credentials: Dictionary containing 'email' and 'password'
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if not self._user_model:
            raise RuntimeError("User model not set. Call set_user_model() first.")
            
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            return False
            
        user = self._user_model.where('email', email).first()
        
        if not user:
            return False
            
        if hasattr(user, 'verify_password'):
            return user.verify_password(password)
        else:
            return check_password_hash(user.password, password)
    
    def validate(self, credentials: Dict[str, str]) -> bool:
        """
        Validate user credentials without logging them in.
        
        Args:
            credentials: Dictionary containing 'email' and 'password'
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        return self.once(credentials)