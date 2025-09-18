"""
Cookie Encryption Middleware

Automatically encrypts outgoing cookies and decrypts incoming cookies.
Provides Laravel-style cookie encryption with exclusion support.
"""

from typing import List, Dict, Any
from flask import request, make_response, current_app
from functools import wraps

from larapy.encryption.encrypter import get_encrypter


class EncryptCookies:
    """
    Middleware for encrypting and decrypting cookies
    """
    
    def __init__(self):
        self.except_cookies: List[str] = [
            'cookie_consent',  # Common cookies that shouldn't be encrypted
            'session',  # Flask session cookie
        ]
        self.encrypter = None
    
    def __call__(self, f):
        """
        Decorator for route functions
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Decrypt incoming cookies
            self.decrypt_request_cookies()
            
            # Call the original function
            response = make_response(f(*args, **kwargs))
            
            # Encrypt outgoing cookies
            self.encrypt_response_cookies(response)
            
            return response
        
        return decorated_function
    
    def decrypt_request_cookies(self):
        """
        Decrypt incoming cookies that are not in the exception list
        """
        if not self.encrypter:
            self.encrypter = get_encrypter()
        
        # Create a mutable copy of cookies
        decrypted_cookies = {}
        
        for cookie_name, cookie_value in request.cookies.items():
            if cookie_name in self.except_cookies:
                decrypted_cookies[cookie_name] = cookie_value
            else:
                try:
                    decrypted_value = self.encrypter.decrypt_string(cookie_value)
                    decrypted_cookies[cookie_name] = decrypted_value
                except Exception:
                    # If decryption fails, keep original value
                    # This handles cookies that weren't encrypted
                    decrypted_cookies[cookie_name] = cookie_value
        
        # Replace request cookies with decrypted ones
        # Note: This is a bit hacky but necessary for Flask
        request.cookies = type(request.cookies)(decrypted_cookies)
    
    def encrypt_response_cookies(self, response):
        """
        Encrypt outgoing cookies that are not in the exception list
        """
        if not self.encrypter:
            self.encrypter = get_encrypter()
        
        # Get all cookies from response
        cookies_to_encrypt = []
        
        # Flask stores cookies in response.headers as Set-Cookie headers
        set_cookie_headers = response.headers.getlist('Set-Cookie')
        
        # Remove existing Set-Cookie headers
        response.headers = type(response.headers)([
            (key, value) for key, value in response.headers 
            if key != 'Set-Cookie'
        ])
        
        # Process each cookie
        for cookie_header in set_cookie_headers:
            cookie_parts = cookie_header.split(';')
            cookie_def = cookie_parts[0].strip()
            
            if '=' in cookie_def:
                cookie_name, cookie_value = cookie_def.split('=', 1)
                cookie_name = cookie_name.strip()
                
                # Check if this cookie should be encrypted
                if cookie_name not in self.except_cookies:
                    try:
                        encrypted_value = self.encrypter.encrypt_string(cookie_value)
                        # Rebuild cookie header with encrypted value
                        new_cookie = f"{cookie_name}={encrypted_value}"
                        if len(cookie_parts) > 1:
                            new_cookie += '; ' + '; '.join(cookie_parts[1:])
                        response.headers.add('Set-Cookie', new_cookie)
                    except Exception:
                        # If encryption fails, use original cookie
                        response.headers.add('Set-Cookie', cookie_header)
                else:
                    # Don't encrypt excluded cookies
                    response.headers.add('Set-Cookie', cookie_header)
            else:
                # Malformed cookie, keep as is
                response.headers.add('Set-Cookie', cookie_header)
    
    def except_cookies(self, cookies: List[str]):
        """
        Set cookies to exclude from encryption
        
        Args:
            cookies: List of cookie names to exclude
        """
        self.except_cookies.extend(cookies)
        return self
    
    def is_disabled(self, cookie_name: str) -> bool:
        """
        Check if encryption is disabled for a specific cookie
        
        Args:
            cookie_name: Name of the cookie to check
            
        Returns:
            bool: True if encryption is disabled for this cookie
        """
        return cookie_name in self.except_cookies


# Helper class for adding encrypted cookies to responses
class CookieEncryptionHelper:
    """
    Helper for working with encrypted cookies
    """
    
    @staticmethod
    def set_encrypted_cookie(response, name: str, value: str, **kwargs):
        """
        Set an encrypted cookie on a response
        
        Args:
            response: Flask response object
            name: Cookie name
            value: Cookie value
            **kwargs: Additional cookie options (max_age, secure, etc.)
        """
        encrypter = get_encrypter()
        encrypted_value = encrypter.encrypt_string(value)
        response.set_cookie(name, encrypted_value, **kwargs)
    
    @staticmethod
    def get_decrypted_cookie(name: str, default=None):
        """
        Get and decrypt a cookie value
        
        Args:
            name: Cookie name
            default: Default value if cookie doesn't exist
            
        Returns:
            Decrypted cookie value or default
        """
        cookie_value = request.cookies.get(name)
        if cookie_value is None:
            return default
        
        try:
            encrypter = get_encrypter()
            return encrypter.decrypt_string(cookie_value)
        except Exception:
            return default


# Create middleware instance
encrypt_cookies = EncryptCookies()