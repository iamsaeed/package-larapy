"""Laravel-compatible InteractsWithFlashData trait for request objects."""

from typing import Dict, Any, List, Optional, Union
from flask import session, has_request_context


class InteractsWithFlashData:
    """
    Laravel-compatible trait for request objects to interact with flash data.
    
    This trait provides methods for flashing data to session and retrieving
    old input values, following Laravel's flash data patterns.
    """
    
    def old(self, key: str = None, default: Any = None) -> Any:
        """
        Retrieve an old input value from the session.
        
        Args:
            key: The input key to retrieve (if None, returns all old input)
            default: Default value if key not found
            
        Returns:
            Any: The old input value or default
        """
        if not self.hasSession():
            return default if key else {}
        
        old_input = session.get('_old_input', {})
        
        if key is None:
            return old_input
            
        return old_input.get(key, default)
    
    def flash(self, input_data: Dict[str, Any] = None) -> None:
        """
        Flash all input to the session.
        
        Args:
            input_data: Input data to flash (if None, uses current request data)
        """
        if not self.hasSession():
            return
            
        if input_data is None:
            input_data = self._get_request_data()
        
        # Remove sensitive data before flashing
        safe_input = self._remove_sensitive_data(input_data)
        
        session['_old_input'] = safe_input
    
    def flashOnly(self, keys: Union[List[str], str]) -> None:
        """
        Flash only specific input keys to the session.
        
        Args:
            keys: List of keys or single key to flash
        """
        if not self.hasSession():
            return
            
        if isinstance(keys, str):
            keys = [keys]
        
        input_data = self._get_request_data()
        filtered_input = {k: v for k, v in input_data.items() if k in keys}
        
        session['_old_input'] = filtered_input
    
    def flash_only(self, keys: Union[List[str], str]) -> None:
        """
        Flash only specific input keys to the session (Python snake_case).
        
        Args:
            keys: List of keys or single key to flash
        """
        self.flashOnly(keys)
    
    def flashExcept(self, keys: Union[List[str], str]) -> None:
        """
        Flash all input except specific keys to the session.
        
        Args:
            keys: List of keys or single key to exclude
        """
        if not self.hasSession():
            return
            
        if isinstance(keys, str):
            keys = [keys]
        
        input_data = self._get_request_data()
        filtered_input = {k: v for k, v in input_data.items() if k not in keys}
        
        # Remove sensitive data
        safe_input = self._remove_sensitive_data(filtered_input)
        
        session['_old_input'] = safe_input
    
    def flash_except(self, keys: Union[List[str], str]) -> None:
        """
        Flash all input except specific keys to the session (Python snake_case).
        
        Args:
            keys: List of keys or single key to exclude
        """
        self.flashExcept(keys)
    
    def hasSession(self) -> bool:
        """
        Check if the request has an active session.
        
        Returns:
            bool: True if session is available
        """
        return has_request_context() and 'session' in globals()
    
    def has_session(self) -> bool:
        """
        Check if the request has an active session (Python snake_case).
        
        Returns:
            bool: True if session is available
        """
        return self.hasSession()
    
    def _get_request_data(self) -> Dict[str, Any]:
        """
        Get all request data (form, JSON, query parameters).
        
        Returns:
            Dict[str, Any]: All request data
        """
        data = {}
        
        # If this is attached to a Flask request object, get its data
        if hasattr(self, 'form'):
            data.update(self.form.to_dict())
        if hasattr(self, 'json') and self.json:
            data.update(self.json)
        if hasattr(self, 'args'):
            data.update(self.args.to_dict())
        if hasattr(self, 'values'):
            data.update(self.values.to_dict())
        
        return data
    
    def _remove_sensitive_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from input before flashing.
        
        Args:
            input_data: The input data to filter
            
        Returns:
            Dict[str, Any]: Filtered input data
        """
        sensitive_keys = [
            'password', 'password_confirmation', 'current_password',
            'new_password', 'new_password_confirmation', '_token',
            'csrf_token', '_method', 'token', 'api_token',
            'access_token', 'refresh_token', 'secret', 'key'
        ]
        
        return {k: v for k, v in input_data.items() if k not in sensitive_keys}
    
    def flashInput(self, input_data: Dict[str, Any] = None) -> None:
        """
        Laravel alias for flash method.
        
        Args:
            input_data: Input data to flash
        """
        self.flash(input_data)
    
    def flash_input(self, input_data: Dict[str, Any] = None) -> None:
        """
        Python snake_case alias for flash method.
        
        Args:
            input_data: Input data to flash
        """
        self.flash(input_data)
    
    def getOldInput(self, key: str = None, default: Any = None) -> Any:
        """
        Laravel alias for old method.
        
        Args:
            key: The input key to retrieve
            default: Default value if key not found
            
        Returns:
            Any: The old input value or default
        """
        return self.old(key, default)
    
    def get_old_input(self, key: str = None, default: Any = None) -> Any:
        """
        Python snake_case alias for old method.
        
        Args:
            key: The input key to retrieve
            default: Default value if key not found
            
        Returns:
            Any: The old input value or default
        """
        return self.old(key, default)


def add_flash_data_methods_to_request():
    """
    Add flash data methods to Flask request object.
    
    This function can be called to monkey-patch Flask's request object
    with the InteractsWithFlashData methods.
    """
    from flask import request
    
    # Add methods to request object
    request.old = InteractsWithFlashData.old.__get__(request, type(request))
    request.flash = InteractsWithFlashData.flash.__get__(request, type(request))
    request.flashOnly = InteractsWithFlashData.flashOnly.__get__(request, type(request))
    request.flash_only = InteractsWithFlashData.flash_only.__get__(request, type(request))
    request.flashExcept = InteractsWithFlashData.flashExcept.__get__(request, type(request))
    request.flash_except = InteractsWithFlashData.flash_except.__get__(request, type(request))
    request.hasSession = InteractsWithFlashData.hasSession.__get__(request, type(request))
    request.has_session = InteractsWithFlashData.has_session.__get__(request, type(request))
    request.flashInput = InteractsWithFlashData.flashInput.__get__(request, type(request))
    request.flash_input = InteractsWithFlashData.flash_input.__get__(request, type(request))
    request.getOldInput = InteractsWithFlashData.getOldInput.__get__(request, type(request))
    request.get_old_input = InteractsWithFlashData.get_old_input.__get__(request, type(request))
    
    # Add private methods
    request._get_request_data = InteractsWithFlashData._get_request_data.__get__(request, type(request))
    request._remove_sensitive_data = InteractsWithFlashData._remove_sensitive_data.__get__(request, type(request))


# Enhanced Request class that includes flash data methods
class RequestWithFlashData(InteractsWithFlashData):
    """
    Enhanced request class that includes flash data methods.
    
    This can be used as a base class for custom request objects
    or as a mixin for existing request classes.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the request with flash data capabilities."""
        super().__init__(*args, **kwargs)
        
    def all(self) -> Dict[str, Any]:
        """
        Get all request data.
        
        Returns:
            Dict[str, Any]: All request data
        """
        return self._get_request_data()