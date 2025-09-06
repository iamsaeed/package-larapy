from flask import request as flask_request
from typing import Any, Dict

class Request:
    """Laravel-style Request wrapper"""
    
    def __init__(self):
        self._flask_request = flask_request
    
    @property
    def method(self) -> str:
        """Get the request method"""
        return self._flask_request.method
    
    def input(self, key: str = None, default: Any = None):
        """Get input data"""
        if key is None:
            # Return all input
            data = {}
            if self._flask_request.json:
                data.update(self._flask_request.json)
            if self._flask_request.form:
                data.update(self._flask_request.form)
            if self._flask_request.args:
                data.update(self._flask_request.args)
            return data
        
        # Get specific key
        if self._flask_request.json and key in self._flask_request.json:
            return self._flask_request.json[key]
        if self._flask_request.form and key in self._flask_request.form:
            return self._flask_request.form[key]
        if self._flask_request.args and key in self._flask_request.args:
            return self._flask_request.args[key]
        
        return default
    
    def get(self, key: str, default: Any = None):
        """Get input data (alias for input)"""
        return self.input(key, default)
    
    def all(self) -> Dict[str, Any]:
        """Get all input data"""
        return self.input()
    
    def only(self, keys: list) -> Dict[str, Any]:
        """Get only specified keys from input"""
        all_input = self.all()
        return {key: all_input.get(key) for key in keys if key in all_input}
    
    def except_keys(self, keys: list) -> Dict[str, Any]:
        """Get all input except specified keys"""
        all_input = self.all()
        return {key: value for key, value in all_input.items() if key not in keys}
    
    def has(self, key: str) -> bool:
        """Check if input has a key"""
        return key in self.all()
    
    def header(self, key: str, default: Any = None):
        """Get header value"""
        return self._flask_request.headers.get(key, default)
    
    @property
    def headers(self):
        """Get all headers"""
        return self._flask_request.headers
    
    @property
    def url(self) -> str:
        """Get the URL"""
        return self._flask_request.url
    
    @property
    def path(self) -> str:
        """Get the path"""
        return self._flask_request.path
    
    def is_json(self) -> bool:
        """Check if request expects JSON"""
        return self._flask_request.is_json
    
    def ip(self) -> str:
        """Get client IP"""
        return self._flask_request.remote_addr
