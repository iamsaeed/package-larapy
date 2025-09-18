"""
Custom Jinja2 Extensions for Larapy - Laravel-like template helpers
"""

from jinja2 import nodes
from jinja2.ext import Extension
from flask import session, current_app
from markupsafe import Markup
import secrets

class LarapyExtension(Extension):
    """Jinja2 extension that provides Laravel Blade-like functionality"""
    
    tags = {'auth', 'guest', 'csrf', 'method', 'error'}
    
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals['csrf_token'] = self.csrf_token
        environment.globals['csrf_field'] = self.csrf_field
        environment.globals['csrf'] = self.csrf_field  # Alias
        environment.globals['csrf_meta'] = self.csrf_meta
        environment.globals['auth_check'] = self.auth_check
        environment.globals['is_guest'] = self.is_guest
        environment.globals['get_error'] = self.get_error
    
    def parse(self, parser):
        """Parse the custom tags"""
        tag = parser.stream.current.value
        lineno = next(parser.stream).lineno
        
        if tag == 'auth':
            return self.parse_auth(parser, lineno)
        elif tag == 'guest':
            return self.parse_guest(parser, lineno)
        elif tag == 'csrf':
            return self.parse_csrf(parser, lineno)
        elif tag == 'method':
            return self.parse_method(parser, lineno)
        elif tag == 'error':
            return self.parse_error(parser, lineno)
    
    def parse_auth(self, parser, lineno):
        """Parse {% auth %}...{% endauth %} blocks"""
        body = parser.parse_statements(['name:endauth'], drop_needle=True)
        
        call_node = self.call_method('_check_auth')
        test = nodes.Test(call_node, 'true', [], lineno=lineno)
        
        return nodes.If(test, body, [], lineno=lineno)
    
    def parse_guest(self, parser, lineno):
        """Parse {% guest %}...{% endguest %} blocks"""
        body = parser.parse_statements(['name:endguest'], drop_needle=True)
        
        call_node = self.call_method('_check_guest')
        test = nodes.Test(call_node, 'true', [], lineno=lineno)
        
        return nodes.If(test, body, [], lineno=lineno)
    
    def parse_csrf(self, parser, lineno):
        """Parse {% csrf %} tag"""
        call_node = self.call_method('_csrf_field')
        return nodes.Output([call_node], lineno=lineno)
    
    def parse_method(self, parser, lineno):
        """Parse {% method 'PUT' %} tag"""
        method = parser.parse_expression()
        call_node = self.call_method('_method_field', [method])
        return nodes.Output([call_node], lineno=lineno)
    
    def parse_error(self, parser, lineno):
        """Parse {% error 'field_name' %} tag"""
        field = parser.parse_expression()
        call_node = self.call_method('_error_field', [field])
        return nodes.Output([call_node], lineno=lineno)
    
    def _check_auth(self):
        """Check if user is authenticated"""
        return self.auth_check()
    
    def _check_guest(self):
        """Check if user is a guest"""
        return self.is_guest()
    
    def _csrf_field(self):
        """Generate CSRF token field"""
        token = self.csrf_token()
        return Markup(f'<input type="hidden" name="_token" value="{token}">')
    
    def _method_field(self, method):
        """Generate method field for form spoofing"""
        return Markup(f'<input type="hidden" name="_method" value="{method}">')
    
    def _error_field(self, field):
        """Get validation error for a field"""
        error = self.get_error(field)
        if error:
            return Markup(f'<span class="error">{error}</span>')
        return Markup('')
    
    def csrf_token(self):
        """Generate or get CSRF token"""
        try:
            # Import and use the CSRF token service
            from larapy.security.csrf_token_service import CSRFTokenService
            service = CSRFTokenService()
            return service.get_token()
        except ImportError:
            # Fallback to simple session-based token
            if 'csrf_token' not in session:
                session['csrf_token'] = secrets.token_hex(16)
            return session['csrf_token']
    
    def csrf_field(self):
        """Generate CSRF token field"""
        token = self.csrf_token()
        return Markup(f'<input type="hidden" name="_token" value="{token}">')
    
    def csrf_meta(self):
        """Generate CSRF meta tag for AJAX"""
        token = self.csrf_token()
        return Markup(f'<meta name="csrf-token" content="{token}">')
    
    def auth_check(self):
        """Check if user is authenticated"""
        try:
            # Try to get the auth manager from the app
            if hasattr(current_app, 'container'):
                auth_manager = current_app.container.make('auth.manager')
                return auth_manager.check()
        except:
            pass
        
        # Fallback to session check
        return session.get('user_authenticated', False)
    
    def is_guest(self):
        """Check if user is a guest (not authenticated)"""
        return not self.auth_check()
    
    def get_error(self, field):
        """Get validation error for a field"""
        errors = session.get('errors', {})
        if isinstance(errors, dict):
            return errors.get(field)
        return None


def setup_larapy_jinja(app):
    """Setup Larapy Jinja2 extensions for Flask app"""
    app.jinja_env.add_extension(LarapyExtension)

    # Add some useful global functions
    app.jinja_env.globals.update({
        'csrf_token': lambda: LarapyExtension(app.jinja_env).csrf_token(),
        'auth_check': lambda: LarapyExtension(app.jinja_env).auth_check(),
        'is_guest': lambda: LarapyExtension(app.jinja_env).is_guest(),
    })

    # Setup Vite helper
    try:
        from .vite import setup_vite_helper
        setup_vite_helper(app)
    except Exception as e:
        # Fallback vite function if import fails
        def vite_fallback(entries):
            from markupsafe import Markup
            import os

            # Check if we have built assets - look in public/build directory
            from pathlib import Path

            # Get the current app's root directory (where app.py is located)
            app_root = Path.cwd()
            build_path = app_root / 'public' / 'build' / '.vite' / 'manifest.json'


            if build_path.exists():
                # Production mode - use manifest
                import json
                try:
                    with open(build_path, 'r') as f:
                        manifest = json.load(f)

                    tags = []
                    for entry in entries:
                        if entry in manifest:
                            asset_info = manifest[entry]
                            file_path = f"/build/{asset_info['file']}"

                            if entry.endswith('.css'):
                                tags.append(f'<link href="{file_path}" rel="stylesheet">')
                            elif entry.endswith('.js'):
                                tags.append(f'<script src="{file_path}" type="module"></script>')

                    if tags:  # Only return if we found assets
                        return Markup('\n'.join(tags))
                except Exception as e:
                    pass

            # Fallback - just reference files directly
            tags = []
            for entry in entries:
                if entry.endswith('.css'):
                    tags.append('<link href="https://cdn.tailwindcss.com" rel="stylesheet">')
                elif entry.endswith('.js'):
                    tags.append('<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>')
            return Markup('\n'.join(tags))

        app.jinja_env.globals['vite'] = vite_fallback

        # Add Laravel-style error handling and old input support
        from ..validation.view_error_bag import ViewErrorBag
        from ..session.store import session_manager
        from flask import g
        
        def get_errors():
            """Get the errors ViewErrorBag for templates."""
            # Check if errors are available in Flask's g object
            if hasattr(g, 'errors'):
                return g.errors
            
            # Check if errors are in view_data
            if hasattr(g, 'view_data') and 'errors' in g.view_data:
                return g.view_data['errors']
            
            # Return empty ViewErrorBag
            return ViewErrorBag()
        
        def get_old_input(key=None, default=None):
            """Get old input value for templates."""
            return session_manager.getOldInput(key, default)
        
        def get_session_value(key=None, default=None):
            """Get session value for templates."""
            if key is None:
                return session_manager
            return session_manager.get(key, default)
        
        def get_field_error(field, bag='default'):
            """Get first error for a specific field."""
            errors = get_errors()
            return errors.getBag(bag).first(field)
        
        def has_field_error(field, bag='default'):
            """Check if a field has errors."""
            errors = get_errors()
            return errors.getBag(bag).has(field)
        
        def get_error_class(field, error_class='error', bag='default'):
            """Get CSS class if field has errors."""
            if has_field_error(field, bag):
                return error_class
            return ''
        
        # Add Laravel-style global functions
        app.jinja_env.globals.update({
            'errors': get_errors,
            'old': get_old_input,
            'session': get_session_value,
            'error': get_field_error,
            'has_error': has_field_error,
            'error_class': get_error_class,
        })
        
        # Add template filters
        app.jinja_env.filters.update({
            'old': lambda field, default='': get_old_input(field, default),
            'error_first': lambda field, bag='default': get_field_error(field, bag) or '',
            'error_all': lambda field, bag='default': get_errors().getBag(bag).get(field),
        })