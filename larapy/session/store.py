"""Enhanced session manager with Laravel-compatible flash data support."""

from typing import Dict, Any, List, Optional, Union
from flask import session, has_request_context
import json


class SessionManager:
    """
    Laravel-compatible session manager with flash data support.
    
    This class provides methods for managing session data including
    flash data that persists for exactly one request.
    """
    
    def __init__(self):
        """Initialize the session manager."""
        pass
    
    def put(self, key: str, value: Any) -> None:
        """
        Store a value in the session.
        
        Args:
            key: The session key
            value: The value to store
        """
        if not self._has_session():
            return
            
        session[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from the session.
        
        Args:
            key: The session key
            default: Default value if key not found
            
        Returns:
            Any: The session value or default
        """
        if not self._has_session():
            return default
            
        return session.get(key, default)
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in the session.
        
        Args:
            key: The session key to check
            
        Returns:
            bool: True if key exists
        """
        if not self._has_session():
            return False
            
        return key in session
    
    def forget(self, key: str) -> None:
        """
        Remove a key from the session.
        
        Args:
            key: The session key to remove
        """
        if not self._has_session():
            return
            
        session.pop(key, None)
    
    def flush(self) -> None:
        """Clear all session data."""
        if not self._has_session():
            return
            
        session.clear()
    
    def flash(self, key: str, value: Any = None) -> None:
        """
        Flash data to the session for the next request.
        
        Args:
            key: The flash key
            value: The value to flash (if None, flashes True)
        """
        if not self._has_session():
            return
            
        if value is None:
            value = True
            
        # Get existing flash data or create new
        flash_data = session.get('_flash', {})
        flash_data[key] = value
        session['_flash'] = flash_data
    
    def flashInput(self, input_data: Dict[str, Any] = None) -> None:
        """
        Flash input data to the session.
        
        Args:
            input_data: The input data to flash
        """
        if input_data is None:
            input_data = {}
            
        # Remove sensitive data before flashing
        safe_input = self._remove_sensitive_data(input_data)
        self.flash('_old_input', safe_input)
    
    def flash_input(self, input_data: Dict[str, Any] = None) -> None:
        """
        Flash input data to the session (Python snake_case).
        
        Args:
            input_data: The input data to flash
        """
        self.flashInput(input_data)
    
    def getOldInput(self, key: str = None, default: Any = None) -> Any:
        """
        Retrieve old input data from the session.
        
        Args:
            key: The input key (if None, returns all old input)
            default: Default value if key not found
            
        Returns:
            Any: The old input value or default
        """
        old_input = self.get('_old_input', {})
        
        if key is None:
            return old_input
            
        return old_input.get(key, default) if isinstance(old_input, dict) else default
    
    def get_old_input(self, key: str = None, default: Any = None) -> Any:
        """
        Retrieve old input data from the session (Python snake_case).
        
        Args:
            key: The input key (if None, returns all old input)
            default: Default value if key not found
            
        Returns:
            Any: The old input value or default
        """
        return self.getOldInput(key, default)
    
    def reflash(self) -> None:
        """
        Reflash all current flash data for another request.
        """
        if not self._has_session():
            return
            
        current_flash = session.get('_flash', {})
        if current_flash:
            # Move current flash data to next flash
            session['_flash'] = current_flash
    
    def keep(self, keys: Union[str, List[str]] = None) -> None:
        """
        Keep specific flash data for another request.
        
        Args:
            keys: Key or list of keys to keep (if None, keeps all)
        """
        if not self._has_session():
            return
            
        if keys is None:
            self.reflash()
            return
            
        if isinstance(keys, str):
            keys = [keys]
            
        current_flash = session.get('_flash', {})
        new_flash = {k: v for k, v in current_flash.items() if k in keys}
        session['_flash'] = new_flash
    
    def now(self, key: str, value: Any) -> None:
        """
        Flash data that is available immediately in the current request.
        
        Args:
            key: The flash key
            value: The value to flash
        """
        if not self._has_session():
            return
            
        # Store in current session data (not flash)
        session[key] = value
        
        # Also flash for next request
        self.flash(key, value)
    
    def pull(self, key: str, default: Any = None) -> Any:
        """
        Get a value from session and remove it.
        
        Args:
            key: The session key
            default: Default value if key not found
            
        Returns:
            Any: The session value or default
        """
        value = self.get(key, default)
        self.forget(key)
        return value
    
    def increment(self, key: str, value: int = 1) -> int:
        """
        Increment a session value.
        
        Args:
            key: The session key
            value: Amount to increment by
            
        Returns:
            int: The new value
        """
        current = self.get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        
        new_value = current + value
        self.put(key, new_value)
        return new_value
    
    def decrement(self, key: str, value: int = 1) -> int:
        """
        Decrement a session value.
        
        Args:
            key: The session key
            value: Amount to decrement by
            
        Returns:
            int: The new value
        """
        return self.increment(key, -value)
    
    def all(self) -> Dict[str, Any]:
        """
        Get all session data.
        
        Returns:
            Dict[str, Any]: All session data
        """
        if not self._has_session():
            return {}
            
        return dict(session)
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in session (alias for has).
        
        Args:
            key: The session key
            
        Returns:
            bool: True if key exists
        """
        return self.has(key)
    
    def missing(self, key: str) -> bool:
        """
        Check if a key is missing from session.
        
        Args:
            key: The session key
            
        Returns:
            bool: True if key is missing
        """
        return not self.has(key)
    
    def _has_session(self) -> bool:
        """
        Check if session is available.
        
        Returns:
            bool: True if session is available
        """
        return has_request_context()
    
    def _remove_sensitive_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from input before flashing.
        
        Args:
            input_data: The input data to filter
            
        Returns:
            Dict[str, Any]: Filtered input data
        """
        if not isinstance(input_data, dict):
            return input_data
            
        sensitive_keys = [
            'password', 'password_confirmation', 'current_password',
            'new_password', 'new_password_confirmation', '_token',
            'csrf_token', '_method', 'token', 'api_token',
            'access_token', 'refresh_token', 'secret', 'key'
        ]
        
        return {k: v for k, v in input_data.items() if k not in sensitive_keys}
    
    def age_flash_data(self):
        """
        Age flash data - move next flash to current and clear next.
        
        This should be called at the beginning of each request to age
        the flash data appropriately.
        """
        if not self._has_session():
            return
            
        # Get current flash data
        current_flash = session.get('_flash', {})
        
        # Make current flash data available in session
        for key, value in current_flash.items():
            session[key] = value
        
        # Clear flash data for next request
        session.pop('_flash', None)
    
    def prepare_flash_data_for_next_request(self):
        """
        Prepare flash data for the next request.
        
        This should be called at the end of request processing to ensure
        flash data is properly set up for the next request.
        """
        if not self._has_session():
            return
            
        # Remove old flash data from main session
        flash_data = session.get('_flash', {})
        for key in flash_data.keys():
            if key in session and key != '_flash':
                session.pop(key, None)


# Global session manager instance
session_manager = SessionManager()


def session_helper(key: str = None, default: Any = None) -> Any:
    """
    Global session helper function.
    
    Args:
        key: Session key (if None, returns session manager)
        default: Default value if key not found
        
    Returns:
        Any: Session value, default, or session manager
    """
    if key is None:
        return session_manager
    
    return session_manager.get(key, default)