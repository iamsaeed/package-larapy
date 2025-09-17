"""JsonResponse class for JSON HTTP responses."""

import json
from typing import Any, Dict, Optional, Union, Callable
from flask import jsonify, make_response, Response as FlaskResponse

from ..contracts import Macroable, Jsonable, Arrayable
from .concerns import ResponseTrait


class JsonResponse(ResponseTrait, Macroable):
    """Laravel-style JsonResponse class."""
    
    def __init__(self, data: Any = None, status: int = 200, headers: Optional[Dict] = None, json_options: int = 0):
        """Initialize the JSON response."""
        super().__init__()
        self._data = data if data is not None else {}
        self._status_code = status
        self._json_options = json_options
        self._callback = None  # For JSONP
        
        if headers:
            self._headers.update(headers)
        
        # Set default content type
        self._headers['Content-Type'] = 'application/json'
    
    def get_data(self) -> Any:
        """Get the response data."""
        return self._data
    
    def set_data(self, data: Any):
        """Set the response data."""
        self._data = data
        return self
    
    def with_callback(self, callback: str):
        """Set JSONP callback."""
        self._callback = callback
        self._headers['Content-Type'] = 'text/javascript'
        return self
    
    def get_callback(self) -> Optional[str]:
        """Get the JSONP callback."""
        return self._callback
    
    def _convert_data_to_json(self) -> str:
        """Convert data to JSON string."""
        data = self._data
        
        # Handle Jsonable objects
        if hasattr(data, 'to_json'):
            return data.to_json()
        
        # Handle Arrayable objects
        if hasattr(data, 'to_array'):
            data = data.to_array()
        
        # Handle objects with __dict__ (like model instances)
        if hasattr(data, '__dict__') and not isinstance(data, (dict, list, str, int, float, bool, type(None))):
            data = data.__dict__
        
        # Convert to JSON
        return json.dumps(data, ensure_ascii=False, default=self._json_serialize_default)
    
    def _json_serialize_default(self, obj):
        """Default JSON serializer for non-serializable objects."""
        # Handle common Python objects
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        if hasattr(obj, '__dict__'):  # objects with __dict__
            return obj.__dict__
        if hasattr(obj, 'to_dict'):  # objects with to_dict method
            return obj.to_dict()
        return str(obj)
    
    def get_content(self) -> str:
        """Get the JSON content."""
        json_content = self._convert_data_to_json()
        
        if self._callback:
            # JSONP response
            return f"{self._callback}({json_content});"
        
        return json_content
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        content = self.get_content()
        response = make_response(content, self._status_code)
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    @staticmethod
    def create(data: Any = None, status: int = 200, headers: Optional[Dict] = None, json_options: int = 0):
        """Create a new JsonResponse instance."""
        return JsonResponse(data, status, headers, json_options)
    
    @staticmethod
    def from_jsonable(jsonable_object: Jsonable, status: int = 200, headers: Optional[Dict] = None):
        """Create JsonResponse from Jsonable object."""
        return JsonResponse(jsonable_object, status, headers)
    
    @staticmethod  
    def from_arrayable(arrayable_object: Arrayable, status: int = 200, headers: Optional[Dict] = None):
        """Create JsonResponse from Arrayable object."""
        return JsonResponse(arrayable_object, status, headers)
    
    def is_json_request(self) -> bool:
        """Check if this is a JSON response."""
        return True
    
    def __str__(self):
        """String representation of the response."""
        return self.get_content()