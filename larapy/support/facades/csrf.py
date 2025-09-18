"""
CSRF Facade

Provides easy access to CSRF token functionality.
"""

from larapy.support.facades.facade import Facade
from larapy.security.csrf_token_service import CSRFTokenService


class CSRF(Facade):
    """
    CSRF Token Facade
    """
    
    @staticmethod
    def get_facade_accessor():
        return CSRFTokenService()
    
    @classmethod
    def token(cls):
        """Get the current CSRF token"""
        return cls.get_facade_accessor().get_token()
    
    @classmethod
    def regenerate(cls):
        """Regenerate the CSRF token"""
        return cls.get_facade_accessor().regenerate_token()
    
    @classmethod
    def verify(cls, token: str):
        """Verify a CSRF token"""
        return cls.get_facade_accessor().is_valid_token(token)