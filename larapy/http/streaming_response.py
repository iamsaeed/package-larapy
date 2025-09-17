"""Streaming response classes for large content."""

import json
from typing import Any, Dict, Optional, Callable, Iterator, Union
from flask import Response as FlaskResponse, stream_template
from io import StringIO

from ..contracts import Macroable
from .concerns import ResponseTrait


class StreamedResponse(ResponseTrait, Macroable):
    """Laravel-style StreamedResponse class."""
    
    def __init__(self, callback: Callable, status: int = 200, headers: Optional[Dict] = None):
        """Initialize the streamed response."""
        super().__init__()
        self._callback = callback
        self._status_code = status
        
        if headers:
            self._headers.update(headers)
    
    def get_callback(self) -> Callable:
        """Get the callback function."""
        return self._callback
    
    def set_callback(self, callback: Callable):
        """Set the callback function."""
        self._callback = callback
        return self
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        def generate():
            if self._callback:
                if hasattr(self._callback, '__call__'):
                    # If callback is callable, call it
                    result = self._callback()
                    if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                        # If result is iterable, yield from it
                        for item in result:
                            yield str(item)
                    else:
                        yield str(result)
                else:
                    yield str(self._callback)
        
        response = FlaskResponse(
            generate(),
            status=self._status_code,
            content_type='text/plain'
        )
        
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    @staticmethod
    def create(callback: Callable, status: int = 200, headers: Optional[Dict] = None):
        """Create a new StreamedResponse instance."""
        return StreamedResponse(callback, status, headers)


class StreamedJsonResponse(ResponseTrait, Macroable):
    """Streamed JSON response for large JSON data."""
    
    def __init__(self, data: Any = None, status: int = 200, headers: Optional[Dict] = None, encoding_options: int = 15):
        """Initialize the streamed JSON response."""
        super().__init__()
        self._data = data
        self._status_code = status
        self._encoding_options = encoding_options
        
        if headers:
            self._headers.update(headers)
        
        # Set JSON content type
        self._headers['Content-Type'] = 'application/json'
    
    def get_data(self) -> Any:
        """Get the response data."""
        return self._data
    
    def set_data(self, data: Any):
        """Set the response data."""
        self._data = data
        return self
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        def generate():
            # Start JSON
            yield '{'
            
            if isinstance(self._data, dict):
                first = True
                for key, value in self._data.items():
                    if not first:
                        yield ','
                    first = False
                    yield f'"{key}":'
                    yield json.dumps(value, ensure_ascii=False, default=str)
            elif isinstance(self._data, list):
                yield '"data":['
                first = True
                for item in self._data:
                    if not first:
                        yield ','
                    first = False
                    yield json.dumps(item, ensure_ascii=False, default=str)
                yield ']'
            else:
                yield f'"data":{json.dumps(self._data, ensure_ascii=False, default=str)}'
            
            # End JSON
            yield '}'
        
        response = FlaskResponse(
            generate(),
            status=self._status_code,
            content_type='application/json'
        )
        
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    @staticmethod
    def create(data: Any = None, status: int = 200, headers: Optional[Dict] = None, encoding_options: int = 15):
        """Create a new StreamedJsonResponse instance."""
        return StreamedJsonResponse(data, status, headers, encoding_options)


class StreamDownloadResponse(ResponseTrait, Macroable):
    """Streamed download response for file downloads."""
    
    def __init__(self, callback: Callable, filename: str, headers: Optional[Dict] = None, disposition: str = 'attachment'):
        """Initialize the stream download response."""
        super().__init__()
        self._callback = callback
        self._filename = filename
        self._disposition = disposition
        self._status_code = 200
        
        if headers:
            self._headers.update(headers)
        
        # Set download headers
        self._headers['Content-Disposition'] = f'{disposition}; filename="{filename}"'
        if not self._headers.get('Content-Type'):
            self._headers['Content-Type'] = 'application/octet-stream'
    
    def get_callback(self) -> Callable:
        """Get the callback function."""
        return self._callback
    
    def get_filename(self) -> str:
        """Get the filename."""
        return self._filename
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        def generate():
            if self._callback:
                if hasattr(self._callback, '__call__'):
                    result = self._callback()
                    if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                        for item in result:
                            if isinstance(item, str):
                                yield item
                            else:
                                yield str(item)
                    else:
                        yield str(result)
                else:
                    yield str(self._callback)
        
        response = FlaskResponse(
            generate(),
            status=self._status_code
        )
        
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    @staticmethod
    def create(callback: Callable, filename: str, headers: Optional[Dict] = None, disposition: str = 'attachment'):
        """Create a new StreamDownloadResponse instance."""
        return StreamDownloadResponse(callback, filename, headers, disposition)