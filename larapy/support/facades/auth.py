"""
Auth Facade - Laravel-style static access to authentication services

Provides a clean, static interface to the AuthManager for easy access
throughout the Larapy application.
"""

from .facade import Facade
from typing import Dict, Any, Optional


class Auth(Facade):
    """
    Auth facade providing static access to authentication services.
    
    Usage:
        from larapy.support.facades import Auth
        
        # Check if user is authenticated
        if Auth.check():
            user = Auth.user()
            
        # Attempt login
        if Auth.attempt({'email': 'user@example.com', 'password': 'secret'}):
            print('Login successful')
            
        # Logout
        Auth.logout()
    """
    
    @staticmethod
    def get_facade_accessor() -> str:
        """
        Get the registered name of the component.
        
        Returns:
            str: The service container binding name
        """
        return 'auth'
    
    @classmethod
    def attempt(cls, credentials: Dict[str, str]) -> bool:
        """
        Attempt to authenticate a user with the given credentials.
        
        Args:
            credentials: Dictionary containing 'email' and 'password'
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        return cls._get_facade_root().attempt(credentials)
    
    @classmethod
    def login(cls, user, remember: bool = False):
        """
        Log in a user.
        
        Args:
            user: User model instance
            remember: Whether to remember the user
            
        Returns:
            User: The logged-in user
        """
        return cls._get_facade_root().login(user, remember)
    
    @classmethod
    def login_using_id(cls, user_id: int, remember: bool = False):
        """
        Log in a user by their ID.
        
        Args:
            user_id: The user's ID
            remember: Whether to remember the user
            
        Returns:
            User or None: The logged-in user or None if not found
        """
        return cls._get_facade_root().login_using_id(user_id, remember)
    
    @classmethod
    def logout(cls):
        """
        Log out the current user.
        """
        return cls._get_facade_root().logout()
    
    @classmethod
    def user(cls):
        """
        Get the currently authenticated user.
        
        Returns:
            User or None: The authenticated user or None if not logged in
        """
        return cls._get_facade_root().user()
    
    @classmethod
    def id(cls) -> Optional[int]:
        """
        Get the ID of the currently authenticated user.
        
        Returns:
            int or None: The user's ID or None if not authenticated
        """
        return cls._get_facade_root().id()
    
    @classmethod
    def check(cls) -> bool:
        """
        Check if a user is currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return cls._get_facade_root().check()
    
    @classmethod
    def guest(cls) -> bool:
        """
        Check if the current user is a guest (not authenticated).
        
        Returns:
            bool: True if guest, False if authenticated
        """
        return cls._get_facade_root().guest()
    
    @classmethod
    def once(cls, credentials: Dict[str, str]) -> bool:
        """
        Log a user in for a single request without affecting the session.
        
        Args:
            credentials: Dictionary containing 'email' and 'password'
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        return cls._get_facade_root().once(credentials)
    
    @classmethod
    def validate(cls, credentials: Dict[str, str]) -> bool:
        """
        Validate user credentials without logging them in.
        
        Args:
            credentials: Dictionary containing 'email' and 'password'
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        return cls._get_facade_root().validate(credentials)
    
    @classmethod
    def set_user_model(cls, model_class):
        """
        Set the User model class for authentication.
        
        Args:
            model_class: The User model class
            
        Returns:
            AuthManager: The auth manager instance
        """
        return cls._get_facade_root().set_user_model(model_class)