"""Response trait with common response methods."""

from typing import Any, Dict, Optional, Union
from flask import make_response, Response as FlaskResponse


class ResponseTrait:
    """Trait providing common response functionality."""
    
    def __init__(self):
        self._response = None
        self._headers = {}
        self._cookies = []
        
    def header(self, key: str, value: str = None):
        """Add or get a header."""
        if value is None:
            return self._headers.get(key)
        
        self._headers[key] = value
        if self._response:
            self._response.headers[key] = value
        return self
    
    def with_headers(self, headers: Dict[str, str]):
        """Add multiple headers."""
        for key, value in headers.items():
            self.header(key, value)
        return self
    
    def cookie(self, name: str, value: str = '', max_age: Optional[int] = None, 
               expires: Optional[str] = None, path: str = '/', domain: Optional[str] = None,
               secure: bool = False, httponly: bool = False, samesite: Optional[str] = None):
        """Add a cookie to the response."""
        cookie_data = {
            'key': name,
            'value': value,
            'max_age': max_age,
            'expires': expires,
            'path': path,
            'domain': domain,
            'secure': secure,
            'httponly': httponly,
            'samesite': samesite
        }
        self._cookies.append(cookie_data)
        
        if self._response:
            self._response.set_cookie(**{k: v for k, v in cookie_data.items() if v is not None})
        return self
    
    def with_cookies(self, cookies: list):
        """Add multiple cookies."""
        for cookie in cookies:
            if isinstance(cookie, dict):
                self.cookie(**cookie)
            else:
                # Assume it's a tuple (name, value)
                self.cookie(cookie[0], cookie[1])
        return self
    
    def status(self, code: int):
        """Set the status code."""
        self._status_code = code
        if self._response:
            self._response.status_code = code
        return self
    
    def setStatusCode(self, code: int):
        """Set the status code (Laravel alias)."""
        return self.status(code)
    
    def get_status_code(self) -> int:
        """Get the status code."""
        if hasattr(self, '_status_code'):
            return self._status_code
        if self._response:
            return self._response.status_code
        return 200
    
    def get_content(self) -> str:
        """Get the response content."""
        if self._response:
            return self._response.get_data(as_text=True)
        return ''
    
    def _apply_headers_and_cookies(self, response: FlaskResponse):
        """Apply stored headers and cookies to a Flask response."""
        for key, value in self._headers.items():
            response.headers[key] = value
            
        for cookie in self._cookies:
            response.set_cookie(**{k: v for k, v in cookie.items() if v is not None and k != 'key'})
            
        if hasattr(self, '_status_code'):
            response.status_code = self._status_code
            
        return response