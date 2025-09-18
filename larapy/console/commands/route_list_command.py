"""Route list console command"""

import os
from typing import Optional
from ...console.command import Command


class RouteListCommand(Command):
    """Display application routes"""
    
    signature = "route:list {--method= : Filter by HTTP method} {--name= : Filter by route name}"
    description = "List all registered routes"

    def handle(self) -> int:
        """Execute the route:list command"""
        
        try:
            # Get filter options
            method_filter = self.option('method')
            name_filter = self.option('name')
            
            # Bootstrap the application to get routes
            from bootstrap.app import create_application
            app = create_application()
            
            # Get all routes from Flask app
            routes = self._get_routes(app.flask_app, method_filter, name_filter)
            
            if not routes:
                if method_filter or name_filter:
                    self.info("No routes found matching the specified filters.")
                else:
                    self.info("No routes registered.")
                return 0
            
            # Display routes in a table format
            self._display_routes(routes)
            
            return 0
            
        except Exception as e:
            self.error(f"Failed to list routes: {str(e)}")
            return 1

    def _get_routes(self, flask_app, method_filter=None, name_filter=None):
        """Get routes from Flask app with optional filtering"""
        routes = []
        
        for rule in flask_app.url_map.iter_rules():
            # Filter by method if specified
            if method_filter:
                if method_filter.upper() not in [method.upper() for method in rule.methods]:
                    continue
            
            # Filter by name if specified
            if name_filter:
                endpoint_name = rule.endpoint or ""
                if name_filter.lower() not in endpoint_name.lower():
                    continue
            
            # Get route information
            route_info = {
                'methods': sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]),
                'uri': rule.rule,
                'name': rule.endpoint or 'N/A',
                'action': self._get_route_action(flask_app, rule)
            }
            
            routes.append(route_info)
        
        # Sort routes by URI
        return sorted(routes, key=lambda x: x['uri'])

    def _get_route_action(self, flask_app, rule):
        """Get the action/handler for a route"""
        try:
            # Get the view function for this endpoint
            view_func = flask_app.view_functions.get(rule.endpoint)
            
            if view_func:
                # Get module and function name
                module = getattr(view_func, '__module__', 'Unknown')
                name = getattr(view_func, '__name__', 'Unknown')
                
                # Try to get controller info if it's a method
                if hasattr(view_func, '__self__'):
                    controller_class = view_func.__self__.__class__.__name__
                    method_name = view_func.__name__
                    return f"{controller_class}@{method_name}"
                elif module != '__main__':
                    return f"{module}.{name}"
                else:
                    return name
            else:
                return 'Closure'
                
        except Exception:
            return 'Unknown'

    def _display_routes(self, routes):
        """Display routes in a formatted table"""
        # Calculate column widths
        method_width = max(len(str(route['methods'])) for route in routes)
        method_width = max(method_width, len('Method'))
        
        uri_width = max(len(route['uri']) for route in routes)
        uri_width = max(uri_width, len('URI'))
        
        name_width = max(len(route['name']) for route in routes)
        name_width = max(name_width, len('Name'))
        
        action_width = max(len(route['action']) for route in routes)
        action_width = max(action_width, len('Action'))
        
        # Add some padding
        method_width += 2
        uri_width += 2
        name_width += 2
        action_width += 2
        
        # Print header
        self.line("")
        self.info("Route List:")
        self.line("")
        
        header = f"{'Method':<{method_width}} {'URI':<{uri_width}} {'Name':<{name_width}} {'Action':<{action_width}}"
        self.line(header)
        self.line("-" * len(header))
        
        # Print routes
        for route in routes:
            methods_str = "|".join(route['methods']) if route['methods'] else 'ANY'
            line = f"{methods_str:<{method_width}} {route['uri']:<{uri_width}} {route['name']:<{name_width}} {route['action']:<{action_width}}"
            self.line(line)
        
        self.line("")
        self.success(f"Showing {len(routes)} routes")

    def _format_methods(self, methods):
        """Format HTTP methods for display"""
        if not methods:
            return "ANY"
        # Remove HEAD and OPTIONS as they're automatic
        filtered_methods = [m for m in methods if m not in ['HEAD', 'OPTIONS']]
        return "|".join(sorted(filtered_methods)) if filtered_methods else "ANY"