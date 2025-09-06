"""
Authenticatable Mixin - Adds authentication capabilities to User models

This mixin provides password hashing, verification, and other authentication
methods that can be used with User models in Larapy.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
import secrets
import string


class Authenticatable:
    """
    Mixin class that adds authentication capabilities to User models.
    
    This mixin provides methods for password hashing, verification,
    remember tokens, and other authentication-related functionality.
    """
    
    def set_password(self, password: str):
        """
        Hash and set the user's password.
        
        Args:
            password: Plain text password to hash and store
        """
        self.password = generate_password_hash(password)
        
    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not hasattr(self, 'password') or not self.password:
            return False
        return check_password_hash(self.password, password)
    
    def set_remember_token(self, token: Optional[str] = None):
        """
        Set the remember token for the user.
        
        Args:
            token: Remember token string, or None to generate a new one
        """
        if token is None:
            token = self._generate_remember_token()
        self.remember_token = token
        
    def get_remember_token(self) -> Optional[str]:
        """
        Get the user's remember token.
        
        Returns:
            str or None: The remember token or None if not set
        """
        return getattr(self, 'remember_token', None)
    
    def get_remember_token_name(self) -> str:
        """
        Get the name of the remember token field.
        
        Returns:
            str: The field name for the remember token
        """
        return 'remember_token'
    
    def _generate_remember_token(self, length: int = 60) -> str:
        """
        Generate a secure random remember token.
        
        Args:
            length: Length of the token to generate
            
        Returns:
            str: Randomly generated token
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def get_auth_identifier(self):
        """
        Get the unique identifier for authentication.
        
        Returns:
            The user's ID or primary key
        """
        return getattr(self, 'id', None)
    
    def get_auth_identifier_name(self) -> str:
        """
        Get the name of the auth identifier field.
        
        Returns:
            str: The field name for the auth identifier (usually 'id')
        """
        return 'id'
    
    def get_auth_password(self) -> str:
        """
        Get the password for authentication.
        
        Returns:
            str: The hashed password
        """
        return getattr(self, 'password', '')
    
    def get_auth_password_name(self) -> str:
        """
        Get the name of the password field.
        
        Returns:
            str: The field name for the password
        """
        return 'password'
    
    @classmethod
    def find_for_auth(cls, identifier):
        """
        Find a user by their auth identifier.
        
        Args:
            identifier: The user's ID or identifier
            
        Returns:
            User instance or None
        """
        return cls.find(identifier)
    
    @classmethod
    def find_by_remember_token(cls, token: str):
        """
        Find a user by their remember token.
        
        Args:
            token: The remember token to search for
            
        Returns:
            User instance or None
        """
        if hasattr(cls, 'where'):
            return cls.where('remember_token', token).first()
        return None
    
    def can_reset_password(self) -> bool:
        """
        Determine if the user can reset their password.
        
        Returns:
            bool: True if password reset is allowed
        """
        return hasattr(self, 'email') and self.email is not None
    
    def send_password_reset_notification(self, token: str):
        """
        Send the password reset notification.
        
        This method should be overridden in your User model to actually
        send the password reset email.
        
        Args:
            token: The password reset token
        """
        pass
    
    def get_email_for_password_reset(self) -> Optional[str]:
        """
        Get the email address where password reset links should be sent.
        
        Returns:
            str or None: The email address for password resets
        """
        return getattr(self, 'email', None)