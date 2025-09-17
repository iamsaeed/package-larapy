"""Laravel-style Response classes for HTTP responses."""

import json
from typing import Any, Dict, Optional, Union
from flask import make_response, Response as FlaskResponse

from ..contracts import Macroable, Jsonable, Arrayable, Renderable
from .concerns import ResponseTrait


class Response(ResponseTrait, Macroable):
    """Laravel-style Response class."""
    
    def __init__(self, content: str = '', status: int = 200, headers: Optional[Dict] = None):
        """Initialize the response."""
        super().__init__()
        self._content = content
        self._status_code = status
        
        if headers:
            self._headers.update(headers)
    
    @staticmethod
    def make(content: str = '', status: int = 200, headers: Optional[Dict] = None):
        """Create a new response instance."""
        return Response(content, status, headers)
    
    def set_content(self, content: str):
        """Set the response content."""
        self._content = content
        return self
    
    def get_content(self) -> str:
        """Get the response content."""
        return self._content
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        response = make_response(self._content, self._status_code)
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    def __str__(self):
        """String representation of the response."""
        return self._content
    
    @staticmethod
    def json(data: Any = None, status: int = 200, headers: Optional[Dict] = None, options: int = 0):
        """Create a JSON response."""
        if data is None:
            data = {}
        
        # Handle Jsonable objects
        if hasattr(data, 'to_json'):
            json_content = data.to_json()
        # Handle Arrayable objects
        elif hasattr(data, 'to_array'):
            json_content = json.dumps(data.to_array(), ensure_ascii=False)
        # Handle regular objects
        else:
            json_content = json.dumps(data, ensure_ascii=False, default=str)
        
        response = Response(json_content, status, headers)
        response.header('Content-Type', 'application/json')
        return response
    
    @staticmethod
    def view(view_name: str, data: Optional[Dict] = None, status: int = 200, headers: Optional[Dict] = None):
        """Create a view response."""
        # This will be implemented when we integrate with the view system
        from ..view.engine import ViewEngine
        
        if data is None:
            data = {}
        
        # Get the view engine from container
        try:
            from ..foundation.application import Application
            app = Application.get_instance()
            view_engine = app.make('view')
            content = view_engine.render(view_name, data)
        except:
            # Fallback if view system is not available
            content = f"View: {view_name} with data: {data}"
        
        response = Response(content, status, headers)
        response.header('Content-Type', 'text/html; charset=utf-8')
        return response
