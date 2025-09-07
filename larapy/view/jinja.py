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
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']
    
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