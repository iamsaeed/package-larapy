"""Response middleware for transforming controller returns."""

from typing import Any, Optional
from flask import request, Response as FlaskResponse

from ..response import Response
from ..json_response import JsonResponse
from ..redirect_response import RedirectResponse
from ..response_factory import ResponseFactory
from ..content_transformer import ContentTransformer
from ...contracts import Renderable


class ResponseMiddleware:
    """Middleware to transform controller return values to proper responses."""
    
    def __init__(self):
        """Initialize the response middleware."""
        self.response_factory = ResponseFactory()
    
    def process_response(self, controller_return: Any) -> FlaskResponse:
        """
        Process controller return value and convert to proper Flask response.
        
        Args:
            controller_return: Value returned from controller method
            
        Returns:
            Proper Flask response object
        """
        # If it's already a Flask response, return as-is
        if isinstance(controller_return, FlaskResponse):
            return controller_return
        
        # If it's one of our response objects, prepare it
        if hasattr(controller_return, 'prepare'):
            return controller_return.prepare()
        
        # Handle None returns
        if controller_return is None:
            return self.response_factory.no_content().prepare()
        
        # Handle redirect responses (might be created by helpers)
        if isinstance(controller_return, RedirectResponse):
            return controller_return.prepare()
        
        # Handle JSON responses
        if isinstance(controller_return, JsonResponse):
            return controller_return.prepare()
        
        # Handle basic responses
        if isinstance(controller_return, Response):
            return controller_return.prepare()
        
        # Auto-detect response type based on content
        return self._auto_detect_response_type(controller_return)
    
    def _auto_detect_response_type(self, content: Any) -> FlaskResponse:
        """Auto-detect appropriate response type for content."""
        
        # Handle view/renderable objects
        if ContentTransformer.is_view_response(content):
            html_content = ContentTransformer.transform_to_string(content)
            response = Response(html_content, 200)
            response.header('Content-Type', 'text/html; charset=utf-8')
            return response.prepare()
        
        # Handle JSON content
        if ContentTransformer.should_be_json(content, request):
            return JsonResponse(content).prepare()
        
        # Handle string content
        if isinstance(content, str):
            response = Response(content)
            response.header('Content-Type', 'text/html; charset=utf-8')
            return response.prepare()
        
        # Handle numeric content
        if isinstance(content, (int, float)):
            return Response(str(content)).prepare()
        
        # Handle boolean content
        if isinstance(content, bool):
            return Response(str(content).lower()).prepare()
        
        # Default to JSON for complex objects
        return JsonResponse(content).prepare()
    
    def __call__(self, controller_return: Any) -> FlaskResponse:
        """Make the middleware callable."""
        return self.process_response(controller_return)


def make_response_middleware():
    """Factory function to create response middleware."""
    return ResponseMiddleware()


def transform_controller_response(response):
    """
    Decorator to automatically transform controller responses.
    
    Usage:
    @app.route('/api/users')
    @transform_controller_response
    def get_users():
        return User.all()  # Automatically converted to JSON
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            middleware = ResponseMiddleware()
            return middleware.process_response(result)
        return wrapper
    return decorator


class ResponseProcessor:
    """Helper class for processing responses in different contexts."""
    
    @staticmethod
    def process_for_api(content: Any, status: int = 200, headers: Optional[dict] = None) -> FlaskResponse:
        """Process content specifically for API responses."""
        if content is None:
            return JsonResponse({'data': None}, status, headers).prepare()
        
        if isinstance(content, str):
            return JsonResponse({'message': content}, status, headers).prepare()
        
        return JsonResponse(content, status, headers).prepare()
    
    @staticmethod
    def process_for_web(content: Any, status: int = 200, headers: Optional[dict] = None) -> FlaskResponse:
        """Process content specifically for web responses."""
        if content is None:
            return Response('', status, headers).prepare()
        
        if isinstance(content, str):
            response = Response(content, status, headers)
            response.header('Content-Type', 'text/html; charset=utf-8')
            return response.prepare()
        
        if ContentTransformer.is_view_response(content):
            html_content = ContentTransformer.transform_to_string(content)
            response = Response(html_content, status, headers)
            response.header('Content-Type', 'text/html; charset=utf-8')
            return response.prepare()
        
        # For complex objects in web context, still prefer JSON for AJAX
        if ContentTransformer.should_be_json(content, request):
            return JsonResponse(content, status, headers).prepare()
        
        # Default to string representation
        response = Response(str(content), status, headers)
        response.header('Content-Type', 'text/html; charset=utf-8')
        return response.prepare()
    
    @staticmethod
    def process_error_response(error: Exception, status: int = 500) -> FlaskResponse:
        """Process error into appropriate response."""
        error_data = {
            'error': str(error),
            'type': error.__class__.__name__
        }
        
        # Check if client expects JSON
        if ContentTransformer.should_be_json(error_data, request):
            return JsonResponse(error_data, status).prepare()
        
        # Default to HTML error page
        html_content = f"""
        <html>
        <head><title>Error {status}</title></head>
        <body>
        <h1>Error {status}</h1>
        <p>{str(error)}</p>
        </body>
        </html>
        """
        response = Response(html_content, status)
        response.header('Content-Type', 'text/html; charset=utf-8')
        return response.prepare()