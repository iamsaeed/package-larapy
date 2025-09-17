"""
Larapy View Engine - Laravel-style template rendering with Jinja2
"""

from flask import render_template, current_app
from typing import Dict, Any
import os
from datetime import datetime
from .jinja import setup_larapy_jinja

class ViewEngine:
    """Laravel-style view engine using Jinja2"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app, base_path=None):
        """Initialize the view engine with Flask app"""
        # Set template folder - use base_path if provided, otherwise fall back to app.root_path
        if base_path:
            template_folder = os.path.join(base_path, 'resources', 'views')
        else:
            template_folder = os.path.join(app.root_path, 'resources', 'views')
        app.template_folder = template_folder
        
        # Setup Larapy Jinja2 extensions (auth, guest, csrf, etc.)
        setup_larapy_jinja(app)
        
        # Register global template functions
        app.jinja_env.globals['current_year'] = datetime.now().year
        app.jinja_env.globals['app_name'] = app.config.get('APP_NAME', 'Larapy')
        app.jinja_env.globals['app_version'] = '1.0.0'
        
        # Register template filters
        app.jinja_env.filters['currency'] = self.currency_filter
        app.jinja_env.filters['datetime'] = self.datetime_filter

    def render(self, template: str, data: Dict[str, Any] = None) -> str:
        """Render a template with data (Laravel's view helper equivalent)"""
        if data is None:
            data = {}
            
        # Add some default context
        data.setdefault('app_name', 'Larapy')
        data.setdefault('app_version', '1.0.0')
        data.setdefault('current_year', datetime.now().year)
        
        return render_template(template, **data)
    
    def currency_filter(self, value, currency='USD'):
        """Format currency"""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return value
    
    def datetime_filter(self, value, format='%Y-%m-%d %H:%M'):
        """Format datetime"""
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return value

# Global functions for convenience (Laravel-style helpers)
def view(template: str, data: Dict[str, Any] = None):
    """Render a view template (Laravel's view() helper)"""
    if data is None:
        data = {}
    return render_template(template, **data)

def render(template: str, data: Dict[str, Any] = None):
    """Alias for view function"""
    return view(template, data)
