"""Setup utilities for Laravel-compatible error handling system."""

from typing import Any
from flask import Flask
from ..http.middleware.share_errors_from_session import ShareErrorsFromSession
from ..http.concerns.interacts_with_flash_data import add_flash_data_methods_to_request
from ..foundation.exceptions.handler import ExceptionHandler
from ..view.jinja import setup_larapy_jinja


def setup_error_handling_system(app: Flask, 
                               register_middleware: bool = True,
                               enhance_request: bool = True,
                               setup_templates: bool = True,
                               setup_exception_handler: bool = True) -> Flask:
    """
    Setup complete Laravel-compatible error handling system.
    
    Args:
        app: Flask application instance
        register_middleware: Whether to register ShareErrorsFromSession middleware
        enhance_request: Whether to add flash data methods to request
        setup_templates: Whether to setup template integration
        setup_exception_handler: Whether to setup validation exception handler
        
    Returns:
        Flask: Enhanced Flask application
    """
    
    # 1. Setup exception handler for validation exceptions
    if setup_exception_handler:
        _setup_validation_exception_handler(app)
    
    # 2. Register ShareErrorsFromSession middleware
    if register_middleware:
        _register_error_sharing_middleware(app)
    
    # 3. Enhance request object with flash data methods
    if enhance_request:
        _enhance_request_with_flash_data(app)
    
    # 4. Setup template integration
    if setup_templates:
        _setup_template_integration(app)
    
    # 5. Setup session flash data aging
    _setup_flash_data_aging(app)
    
    return app


def _setup_validation_exception_handler(app: Flask):
    """Setup validation exception handler."""
    from ..validation.exceptions import ValidationException
    
    # Get or create exception handler
    if not hasattr(app, 'exception_handler'):
        app.exception_handler = ExceptionHandler(app)
    
    # Register validation exception handler
    @app.errorhandler(ValidationException)
    def handle_validation_exception(error):
        return app.exception_handler.convertValidationExceptionToResponse(error)


def _register_error_sharing_middleware(app: Flask):
    """Register ShareErrorsFromSession middleware."""
    
    # Create middleware instance
    error_sharing_middleware = ShareErrorsFromSession()
    
    # Register as before_request and after_request handlers
    @app.before_request
    def share_errors_before_request():
        """Make errors available before request processing."""
        from flask import request, g
        from ..validation.view_error_bag import ViewErrorBag
        
        # Get errors from session or create empty ViewErrorBag
        errors = error_sharing_middleware._get_errors_from_session()
        
        # Make errors available to all views
        g.errors = errors
        if not hasattr(g, 'view_data'):
            g.view_data = {}
        g.view_data['errors'] = errors
    
    @app.after_request
    def cleanup_flash_errors_after_request(response):
        """Cleanup flash errors after request."""
        error_sharing_middleware._cleanup_flashed_errors()
        return response


def _enhance_request_with_flash_data(app: Flask):
    """Enhance request object with flash data methods."""
    
    @app.before_request
    def add_flash_methods_to_request():
        """Add flash data methods to the current request."""
        add_flash_data_methods_to_request()


def _setup_template_integration(app: Flask):
    """Setup template integration for error handling."""
    
    # Setup Jinja environment with Laravel features
    setup_larapy_jinja(app)
    
    # Add context processor for template variables
    @app.context_processor
    def inject_error_context():
        """Inject error and session helpers into all templates."""
        from flask import g
        from ..validation.view_error_bag import ViewErrorBag
        from ..session.store import session_manager
        
        # Get errors from g object or create empty ViewErrorBag
        errors = getattr(g, 'errors', ViewErrorBag())
        
        return {
            'errors': errors,
            'old': session_manager.getOldInput,
            'session': session_manager.get,
        }


def _setup_flash_data_aging(app: Flask):
    """Setup flash data aging for proper session management."""
    from ..session.store import session_manager
    
    @app.before_request
    def age_flash_data():
        """Age flash data at the beginning of each request."""
        session_manager.age_flash_data()
    
    @app.after_request 
    def prepare_flash_data(response):
        """Prepare flash data for next request."""
        session_manager.prepare_flash_data_for_next_request()
        return response


def register_web_middleware(app: Flask):
    """
    Register middleware specifically for web routes.
    
    Args:
        app: Flask application instance
    """
    
    # Register ShareErrorsFromSession for web routes
    error_middleware = ShareErrorsFromSession()
    
    # Create a custom middleware wrapper for web routes only
    @app.before_request
    def web_middleware():
        """Apply web-specific middleware."""
        from flask import request
        
        # Only apply to non-API routes
        if not request.path.startswith('/api/'):
            # Share errors with views
            from flask import g
            errors = error_middleware._get_errors_from_session()
            g.errors = errors
            if not hasattr(g, 'view_data'):
                g.view_data = {}
            g.view_data['errors'] = errors


def quick_setup(app: Flask) -> Flask:
    """
    Quick setup with all Laravel error handling features enabled.
    
    Args:
        app: Flask application instance
        
    Returns:
        Flask: Enhanced Flask application with complete error handling
    """
    return setup_error_handling_system(
        app,
        register_middleware=True,
        enhance_request=True,
        setup_templates=True,
        setup_exception_handler=True
    )


# Convenience aliases
setup_laravel_error_handling = setup_error_handling_system
setup_validation_system = setup_error_handling_system