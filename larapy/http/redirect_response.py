"""RedirectResponse class for HTTP redirects."""

from typing import Any, Dict, Optional, Union, List
from flask import redirect, session, request, Response as FlaskResponse
from urllib.parse import urljoin, urlparse

from ..contracts import Macroable
from .concerns import ResponseTrait


class RedirectResponse(ResponseTrait, Macroable):
    """Laravel-style RedirectResponse class."""
    
    def __init__(self, url: str, status: int = 302, headers: Optional[Dict] = None):
        """Initialize the redirect response."""
        super().__init__()
        self._target_url = url
        self._status_code = status
        self._flash_data = {}
        self._input_data = {}
        self._errors = {}
        self._fragment = None
        
        if headers:
            self._headers.update(headers)
    
    def get_target_url(self) -> str:
        """Get the target URL."""
        url = self._target_url
        if self._fragment:
            url += f"#{self._fragment}"
        return url
    
    def set_target_url(self, url: str):
        """Set the target URL."""
        self._target_url = url
        return self
    
    def with_input(self, input_data: Optional[Dict] = None):
        """Flash input data to the session."""
        if input_data is None:
            # Get all input from current request
            if hasattr(request, 'form'):
                input_data = request.form.to_dict()
            elif hasattr(request, 'json') and request.json:
                input_data = request.json
            else:
                input_data = {}
        
        self._input_data.update(input_data)
        return self
    
    def only_input(self, *keys: str):
        """Flash only specific input keys."""
        if hasattr(request, 'form'):
            all_input = request.form.to_dict()
        elif hasattr(request, 'json') and request.json:
            all_input = request.json
        else:
            all_input = {}
        
        filtered_input = {key: all_input.get(key) for key in keys if key in all_input}
        self._input_data.update(filtered_input)
        return self
    
    def except_input(self, *keys: str):
        """Flash all input except specific keys.""" 
        if hasattr(request, 'form'):
            all_input = request.form.to_dict()
        elif hasattr(request, 'json') and request.json:
            all_input = request.json
        else:
            all_input = {}
        
        filtered_input = {key: value for key, value in all_input.items() if key not in keys}
        self._input_data.update(filtered_input)
        return self
    
    def with_errors(self, errors: Union[Dict, List, str], key: str = 'default'):
        """Flash errors to the session."""
        if isinstance(errors, str):
            errors = {'error': errors}
        elif isinstance(errors, list):
            errors = {'errors': errors}
        
        if key not in self._errors:
            self._errors[key] = {}
        
        if isinstance(errors, dict):
            self._errors[key].update(errors)
        else:
            self._errors[key]['error'] = str(errors)
        
        return self
    
    def with_fragment(self, fragment: str):
        """Add URL fragment."""
        self._fragment = fragment.lstrip('#')
        return self
    
    def without_fragment(self):
        """Remove URL fragment."""
        self._fragment = None
        return self
    
    def with_(self, key: str, value: Any = None):
        """Flash data to session (with method)."""
        if isinstance(key, dict):
            self._flash_data.update(key)
        else:
            self._flash_data[key] = value
        return self
    
    def withCookie(self, cookie):
        """Add cookie to redirect response (Laravel style)."""
        if hasattr(cookie, 'to_dict'):
            cookie_data = cookie.to_dict()
            self.cookie(**cookie_data)
        elif isinstance(cookie, dict):
            self.cookie(**cookie)
        else:
            # Assume it's a tuple (name, value)
            self.cookie(cookie[0], cookie[1])
        return self
    
    def withCookies(self, cookies: List):
        """Add multiple cookies to redirect response (Laravel style)."""
        for cookie in cookies:
            self.withCookie(cookie)
        return self
    
    def withHeaders(self, headers: Dict[str, str]):
        """Add headers to redirect response (Laravel style)."""
        return self.with_headers(headers)
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        # Flash data to session
        self._flash_to_session()
        
        # Create redirect response
        response = redirect(self.get_target_url(), code=self._status_code)
        
        # Apply headers and cookies
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response.""" 
        return self.prepare()
    
    def _flash_to_session(self):
        """Flash all data to session."""
        # Flash custom data
        for key, value in self._flash_data.items():
            session[f'_flash.{key}'] = value
        
        # Flash input data
        if self._input_data:
            session['_old_input'] = self._input_data
        
        # Flash errors
        if self._errors:
            session['_errors'] = self._errors
    
    @staticmethod
    def create(url: str, status: int = 302, headers: Optional[Dict] = None):
        """Create a new RedirectResponse instance."""
        return RedirectResponse(url, status, headers)
    
    @staticmethod
    def to(url: str, status: int = 302, headers: Optional[Dict] = None):
        """Create redirect to URL."""
        return RedirectResponse.create(url, status, headers)
    
    @staticmethod  
    def back(status: int = 302, headers: Optional[Dict] = None, fallback: str = '/'):
        """Create redirect back to previous page."""
        # Try to get referrer from request
        if hasattr(request, 'referrer') and request.referrer:
            return RedirectResponse.create(request.referrer, status, headers)
        
        # Try to get from session
        previous_url = session.get('_previous_url', fallback)
        return RedirectResponse.create(previous_url, status, headers)
    
    @staticmethod
    def route(route_name: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Create redirect to named route."""
        # This will need URL generator integration
        try:
            from flask import url_for
            if parameters:
                url = url_for(route_name, **parameters)
            else:
                url = url_for(route_name)
            return RedirectResponse.create(url, status, headers)
        except:
            # Fallback if route not found
            return RedirectResponse.create('/', status, headers)
    
    @staticmethod
    def away(url: str, status: int = 302, headers: Optional[Dict] = None):
        """Create redirect to external URL."""
        return RedirectResponse.create(url, status, headers)
    
    @staticmethod
    def secure(path: str, status: int = 302, headers: Optional[Dict] = None):
        """Create secure redirect (HTTPS)."""
        if not path.startswith('https://'):
            if path.startswith('http://'):
                path = path.replace('http://', 'https://', 1)
            elif not path.startswith('//'):
                # Relative path - make it absolute HTTPS
                from flask import request
                if hasattr(request, 'host'):
                    path = f"https://{request.host}{path}"
        
        return RedirectResponse.create(path, status, headers)
    
    def __str__(self):
        """String representation of the response."""
        return f"Redirect to {self.get_target_url()}"