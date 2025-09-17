"""ResponseFactory class for creating responses."""

from typing import Any, Dict, Optional, Callable
from flask import request

from ..contracts import ResponseFactory as ResponseFactoryInterface, Macroable
from .response import Response
from .json_response import JsonResponse
from .redirect_response import RedirectResponse
from .file_response import FileResponse, DownloadResponse
from .streaming_response import StreamedResponse, StreamedJsonResponse, StreamDownloadResponse


class ResponseFactory(ResponseFactoryInterface, Macroable):
    """Laravel-style ResponseFactory for creating responses."""
    
    def __init__(self):
        """Initialize the response factory."""
        pass
    
    def make(self, content: str = '', status: int = 200, headers: Optional[Dict] = None):
        """Create a basic response."""
        return Response(content, status, headers)
    
    def no_content(self, status: int = 204, headers: Optional[Dict] = None):
        """Create a no content response."""
        return Response('', status, headers)
    
    def json(self, data: Any = None, status: int = 200, headers: Optional[Dict] = None, options: int = 0):
        """Create a JSON response."""
        return JsonResponse(data, status, headers, options)
    
    def jsonp(self, callback: str, data: Any = None, status: int = 200, headers: Optional[Dict] = None, options: int = 0):
        """Create a JSONP response."""
        response = JsonResponse(data, status, headers, options)
        return response.with_callback(callback)
    
    def view(self, view_name: str, data: Optional[Dict] = None, status: int = 200, headers: Optional[Dict] = None):
        """Create a view response."""
        return Response.view(view_name, data, status, headers)
    
    def redirect_to(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Create a redirect response."""
        if secure is True:
            return RedirectResponse.secure(path, status, headers)
        return RedirectResponse.to(path, status, headers)
    
    def redirect_to_route(self, route: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Create a redirect to named route."""
        return RedirectResponse.route(route, parameters, status, headers)
    
    def redirect_to_action(self, action: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Create a redirect to controller action."""
        # This would need integration with the routing system
        # For now, treat as route
        return self.redirect_to_route(action, parameters, status, headers)
    
    def redirect_guest(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Create a redirect for guests (unauthenticated users)."""
        return self.redirect_to(path, status, headers, secure)
    
    def redirect_to_intended(self, default: str = '/', status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Create a redirect to intended URL or default."""
        # Get intended URL from session
        from flask import session
        intended_url = session.pop('_intended_url', default)
        return self.redirect_to(intended_url, status, headers, secure)
    
    def download(self, file_path: str, name: Optional[str] = None, headers: Optional[Dict] = None, disposition: str = 'attachment'):
        """Create a file download response."""
        return DownloadResponse(file_path, name, headers)
    
    def file(self, file_path: str, headers: Optional[Dict] = None):
        """Create a file response for inline display."""
        return FileResponse(file_path, headers, 'inline')
    
    def stream(self, callback: Callable, status: int = 200, headers: Optional[Dict] = None):
        """Create a streamed response."""
        return StreamedResponse(callback, status, headers)
    
    def stream_json(self, data: Any, status: int = 200, headers: Optional[Dict] = None, encoding_options: int = 15):
        """Create a streamed JSON response."""
        return StreamedJsonResponse(data, status, headers, encoding_options)
    
    def stream_download(self, callback: Callable, name: str, headers: Optional[Dict] = None, disposition: str = 'attachment'):
        """Create a streamed download response."""
        return StreamDownloadResponse(callback, name, headers, disposition)
    
    # Laravel method aliases for compatibility
    def streamJson(self, data: Any, status: int = 200, headers: Optional[Dict] = None, encoding_options: int = 15):
        """Laravel alias for stream_json."""
        return self.stream_json(data, status, headers, encoding_options)
    
    def streamDownload(self, callback: Callable, name: str, headers: Optional[Dict] = None, disposition: str = 'attachment'):
        """Laravel alias for stream_download."""
        return self.stream_download(callback, name, headers, disposition)
    
    def redirectTo(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Laravel alias for redirect_to."""
        return self.redirect_to(path, status, headers, secure)
    
    def redirectToRoute(self, route: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Laravel alias for redirect_to_route."""
        return self.redirect_to_route(route, parameters, status, headers)
    
    def redirectToAction(self, action: str, parameters: Optional[Dict] = None, status: int = 302, headers: Optional[Dict] = None):
        """Laravel alias for redirect_to_action."""
        return self.redirect_to_action(action, parameters, status, headers)
    
    def redirectGuest(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Laravel alias for redirect_guest."""
        return self.redirect_guest(path, status, headers, secure)
    
    def redirectToIntended(self, default: str = '/', status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Laravel alias for redirect_to_intended."""
        return self.redirect_to_intended(default, status, headers, secure)
    
    def noContent(self, status: int = 204, headers: Optional[Dict] = None):
        """Laravel alias for no_content."""
        return self.no_content(status, headers)
    
    def make_response(self, content: Any, status: int = 200, headers: Optional[Dict] = None):
        """Create appropriate response based on content type."""
        # Auto-detect response type based on content
        if content is None:
            return self.no_content()
        
        # Check if it's a dict/list that should be JSON
        if isinstance(content, (dict, list)):
            return self.json(content, status, headers)
        
        # Check if it's a Jsonable object
        if hasattr(content, 'to_json'):
            return self.json(content, status, headers)
        
        # Check if it's an Arrayable object  
        if hasattr(content, 'to_array'):
            return self.json(content, status, headers)
        
        # Check if it's a Renderable object
        if hasattr(content, 'render'):
            content = content.render()
        
        # Check for AJAX requests that expect JSON
        if (request and hasattr(request, 'is_json') and request.is_json and 
            not isinstance(content, str)):
            return self.json({'data': content}, status, headers)
        
        # Default to string response
        return self.make(str(content), status, headers)