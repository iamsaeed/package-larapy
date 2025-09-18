"""
CSRF Token Service

Handles generation, storage, and validation of CSRF tokens.
Integrates with session management for secure token storage.
"""

import secrets
import time
from typing import Optional
from flask import session


class CSRFTokenService:
    """
    Service for managing CSRF tokens
    """
    
    TOKEN_KEY = '_csrf_token'
    TOKEN_TIME_KEY = '_csrf_token_time'
    TOKEN_LENGTH = 40
    TOKEN_LIFETIME = 3600  # 1 hour in seconds
    
    def generate_token(self) -> str:
        """
        Generate a new cryptographically secure CSRF token
        """
        token = secrets.token_urlsafe(self.TOKEN_LENGTH)
        self.store_token(token)
        return token
    
    def store_token(self, token: str) -> None:
        """
        Store the token in the session with timestamp
        """
        session[self.TOKEN_KEY] = token
        session[self.TOKEN_TIME_KEY] = time.time()
        session.permanent = True
    
    def get_session_token(self) -> Optional[str]:
        """
        Get the current session token if valid
        """
        token = session.get(self.TOKEN_KEY)
        token_time = session.get(self.TOKEN_TIME_KEY)
        
        if not token or not token_time:
            return None
        
        # Check if token has expired
        if time.time() - token_time > self.TOKEN_LIFETIME:
            self.clear_token()
            return None
        
        return token
    
    def get_token(self) -> str:
        """
        Get the current token or generate a new one
        """
        token = self.get_session_token()
        if not token:
            token = self.generate_token()
        return token
    
    def clear_token(self) -> None:
        """
        Clear the token from session
        """
        session.pop(self.TOKEN_KEY, None)
        session.pop(self.TOKEN_TIME_KEY, None)
    
    def regenerate_token(self) -> str:
        """
        Generate a new token (used after login/logout)
        """
        self.clear_token()
        return self.generate_token()
    
    def is_valid_token(self, token: str) -> bool:
        """
        Check if provided token matches session token
        """
        session_token = self.get_session_token()
        if not session_token:
            return False
        
        # Use constant-time comparison
        import hmac
        return hmac.compare_digest(
            session_token.encode('utf-8'),
            token.encode('utf-8')
        )