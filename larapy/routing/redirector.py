"""Redirector class for handling redirects."""

from typing import Any, Dict, Optional, Union, List
from flask import session, request, url_for

from ..contracts import Macroable
from ..http.redirect_response import RedirectResponse


class Redirector(Macroable):
    """Laravel-style Redirector for creating redirects."""
    
    def __init__(self):
        """Initialize the redirector."""
        pass
    
    def back(self, status: int = 302, headers: Optional[Dict] = None, fallback: str = '/'):
        """Redirect back to the previous page."""
        return RedirectResponse.back(status, headers, fallback)
    
    def refresh(self, status: int = 302, headers: Optional[Dict] = None):
        """Redirect to the current page."""
        current_url = request.url if request else '/'
        return RedirectResponse.to(current_url, status, headers)
    
    def guest(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Redirect guests to a specific path."""
        if secure:
            return RedirectResponse.secure(path, status, headers)
        return RedirectResponse.to(path, status, headers)
    
    def intended(self, default: str = '/', status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Redirect to the intended URL or default."""
        # Get intended URL from session
        intended_url = session.pop('_intended_url', default)
        
        if secure:
            return RedirectResponse.secure(intended_url, status, headers)
        return RedirectResponse.to(intended_url, status, headers)
    
    def set_intended_url(self, url: str):
        """Set the intended URL in session."""
        session['_intended_url'] = url
        return self
    
    def get_intended_url(self, default: str = '/') -> str:
        """Get the intended URL from session."""
        return session.get('_intended_url', default)
    
    def to(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Redirect to a specific path."""
        if secure:
            return RedirectResponse.secure(path, status, headers)
        return RedirectResponse.to(path, status, headers)
    
    def away(self, path: str, status: int = 302, headers: Optional[Dict] = None):
        """Redirect to an external URL."""
        return RedirectResponse.away(path, status, headers)
    
    def secure(self, path: str, status: int = 302, headers: Optional[Dict] = None):
        """Create a secure (HTTPS) redirect."""
        return RedirectResponse.secure(path, status, headers)
    
    def route(self, route_name: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Redirect to a named route."""
        return RedirectResponse.route(route_name, parameters, status, headers)
    
    def action(self, action: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Redirect to a controller action."""
        # This would need integration with the controller/action system
        # For now, treat it as a route
        try:
            # Try to parse controller@action format
            if '@' in action:
                controller, method = action.split('@', 1)
                route_name = f"{controller.lower()}.{method.lower()}"
            else:
                route_name = action
            
            return self.route(route_name, parameters, status, headers)
        except:
            # Fallback to treating as URL
            return self.to(action, status, headers)
    
    def home(self, status: int = 302, headers: Optional[Dict] = None):
        """Redirect to the home page."""
        try:
            return self.route('home', None, status, headers)
        except:
            return self.to('/', status, headers)
    
    def with_input(self, input_data: Optional[Dict] = None):
        """Create a redirect with input data flashed."""
        redirect_response = RedirectResponse.back()
        return redirect_response.with_input(input_data)
    
    def with_errors(self, errors: Union[Dict, List, str], key: str = 'default'):
        """Create a redirect with errors flashed."""
        redirect_response = RedirectResponse.back()
        return redirect_response.with_errors(errors, key)
    
    def with_success(self, message: str):
        """Create a redirect with success message."""
        redirect_response = RedirectResponse.back()
        return redirect_response.with_('success', message)
    
    def with_message(self, message: str, type_: str = 'info'):
        """Create a redirect with a message."""
        redirect_response = RedirectResponse.back()
        return redirect_response.with_(type_, message)
    
    def back_with_input(self):
        """Shorthand for redirecting back with input."""
        return RedirectResponse.back().with_input()
    
    def back_with_errors(self, errors: Union[Dict, List, str], key: str = 'default'):
        """Shorthand for redirecting back with errors."""
        return RedirectResponse.back().with_errors(errors, key)
    
    def previous(self, default: str = '/'):
        """Get the previous URL."""
        if hasattr(request, 'referrer') and request.referrer:
            return request.referrer
        return session.get('_previous_url', default)
    
    def set_previous_url(self, url: str):
        """Set the previous URL in session."""
        session['_previous_url'] = url
        return self
    
    def store_current_url(self):
        """Store the current URL as previous."""
        if request:
            session['_previous_url'] = request.url
        return self