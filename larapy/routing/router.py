from flask import request, jsonify
from typing import Callable, Dict, List, Any
import inspect

class Router:
    """Laravel-style Router implementation"""
    
    def __init__(self, app):
        self.app = app
        self.flask_app = app.flask_app
        self._middleware = {}
        self._middleware_groups = {}
        self._route_middleware = []
        
    def get(self, uri: str, action, **options):
        """Register a GET route"""
        return self._add_route(['GET'], uri, action, **options)
    
    def post(self, uri: str, action, **options):
        """Register a POST route"""
        return self._add_route(['POST'], uri, action, **options)
    
    def put(self, uri: str, action, **options):
        """Register a PUT route"""
        return self._add_route(['PUT'], uri, action, **options)
    
    def patch(self, uri: str, action, **options):
        """Register a PATCH route"""
        return self._add_route(['PATCH'], uri, action, **options)
    
    def delete(self, uri: str, action, **options):
        """Register a DELETE route"""
        return self._add_route(['DELETE'], uri, action, **options)
    
    def any(self, uri: str, action, **options):
        """Register a route responding to all verbs"""
        return self._add_route(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], uri, action, **options)
    
    def _add_route(self, methods: List[str], uri: str, action, **options):
        """Add a route to the Flask application"""
        # Convert Laravel-style URI to Flask-style
        flask_uri = self._convert_uri(uri)
        
        # Get middleware for this route
        middleware = options.get('middleware', [])
        if isinstance(middleware, str):
            middleware = [middleware]
        
        # Create the route handler
        def route_handler(*args, **kwargs):
            # Run middleware
            for mw_name in middleware:
                if mw_name in self._middleware:
                    middleware_class = self._middleware[mw_name]
                    # Apply middleware (simplified implementation)
            
            # Handle the action
            if callable(action):
                return self._call_action(action, kwargs)
            elif isinstance(action, str):
                return self._call_controller_action(action, kwargs)
            else:
                return action
        
        # Register with Flask
        endpoint = options.get('as', f"{methods[0].lower()}_{uri.replace('/', '_').replace('{', '').replace('}', '')}")
        self.flask_app.add_url_rule(
            flask_uri, 
            endpoint=endpoint,
            view_func=route_handler, 
            methods=methods
        )
        
        return self
    
    def _convert_uri(self, uri: str) -> str:
        """Convert Laravel URI format to Flask format"""
        # Convert {param} to <param>
        import re
        return re.sub(r'{(\w+)}', r'<\1>', uri)
    
    def _call_action(self, action: Callable, parameters: Dict):
        """Call a closure action with dependency injection"""
        try:
            sig = inspect.signature(action)
            resolved_params = {}
            
            for param_name, param in sig.parameters.items():
                if param_name in parameters:
                    resolved_params[param_name] = parameters[param_name]
                elif param.annotation != inspect.Parameter.empty:
                    # Try to resolve from container
                    try:
                        if hasattr(param.annotation, '__name__'):
                            dependency = self.app.resolve(param.annotation.__name__)
                        else:
                            dependency = self.app.resolve(str(param.annotation))
                        resolved_params[param_name] = dependency
                    except:
                        if param.default != inspect.Parameter.empty:
                            resolved_params[param_name] = param.default
            
            result = action(**resolved_params)
            
            # Handle different response types
            if isinstance(result, dict):
                return jsonify(result)
            return result
            
        except Exception as e:
            return str(e), 500
    
    def _call_controller_action(self, action: str, parameters: Dict):
        """Call a controller action"""
        # Parse Controller@method format
        if '@' in action:
            controller_name, method = action.split('@')
            
            # Resolve controller from container
            controller = self.app.resolve(controller_name)
            
            # Call method with dependency injection
            method_func = getattr(controller, method)
            return self._call_action(method_func, parameters)
        
        return "Invalid controller action format", 500
    
    def middleware(self, name: str, middleware_class: str):
        """Register a middleware"""
        self._middleware[name] = middleware_class
    
    def middleware_group(self, name: str, middleware: List[str]):
        """Register a middleware group"""
        self._middleware_groups[name] = middleware
    
    def group(self, attributes: Dict, callback: Callable):
        """Create a route group"""
        # Store current context
        old_middleware = self._route_middleware.copy()
        
        # Add group middleware
        if 'middleware' in attributes:
            group_middleware = attributes['middleware']
            if isinstance(group_middleware, str):
                group_middleware = [group_middleware]
            self._route_middleware.extend(group_middleware)
        
        # Execute the group callback
        callback()
        
        # Restore context
        self._route_middleware = old_middleware

# Route Group context manager for cleaner syntax
class RouteGroup:
    def __init__(self, router: Router, attributes: Dict):
        self.router = router
        self.attributes = attributes
        self.old_middleware = []
    
    def __enter__(self):
        self.old_middleware = self.router._route_middleware.copy()
        if 'middleware' in self.attributes:
            middleware = self.attributes['middleware']
            if isinstance(middleware, str):
                middleware = [middleware]
            self.router._route_middleware.extend(middleware)
        return self.router
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.router._route_middleware = self.old_middleware
