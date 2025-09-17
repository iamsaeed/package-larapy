"""Global exception handler for Larapy applications"""

import traceback
from flask import jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException
from typing import Optional, Union, Dict, Any
from ...validation.exceptions import ValidationException
from ...validation.view_error_bag import ViewErrorBag
from ...http.middleware.share_errors_from_session import ShareErrorsFromSession

class ExceptionHandler:
    """Global exception handler for Larapy applications"""

    def __init__(self, app):
        self.app = app
        self.register()

    def register(self):
        """Register exception handlers with Flask"""
        self.app.flask_app.register_error_handler(Exception, self.handle)
        self.app.flask_app.register_error_handler(404, self.handle_404)
        self.app.flask_app.register_error_handler(500, self.handle_500)

    def handle(self, error):
        """Handle all exceptions"""
        # Special handling for validation exceptions
        if isinstance(error, ValidationException):
            return self.convertValidationExceptionToResponse(error)
        
        # Log the error
        self.report(error)

        # Render appropriate response
        return self.render(error)

    def report(self, error):
        """Log exception to configured channels"""
        if self.should_report(error):
            try:
                logger = self.app.resolve('log')

                # Build error context
                context = {}
                if request:
                    context = {
                        'url': request.url,
                        'method': request.method,
                        'ip': request.remote_addr,
                        'user_agent': request.user_agent.string if request.user_agent else None,
                        'headers': dict(request.headers),
                    }

                # Log with full traceback
                logger.error(
                    f"Exception: {type(error).__name__}: {str(error)}",
                    {'context': context, 'traceback': traceback.format_exc()}
                )
            except Exception as log_error:
                # Fallback logging if our logger fails
                print(f"Failed to log exception: {log_error}")
                print(f"Original exception: {error}")

    def should_report(self, error) -> bool:
        """Determine if exception should be logged"""
        # Don't report 404s and validation errors by default
        dont_report = [
            'NotFoundException',
            'ValidationException',
            'NotFound',  # Werkzeug's 404
        ]
        return type(error).__name__ not in dont_report

    def convertValidationExceptionToResponse(self, exception: ValidationException):
        """
        Convert ValidationException to appropriate response.
        
        Args:
            exception: The validation exception to handle
            
        Returns:
            Response: Appropriate redirect or JSON response
        """
        # Check if request wants JSON response
        if self.expects_json_for_validation():
            return self._convert_validation_to_json_response(exception)
        else:
            return self._convert_validation_to_redirect_response(exception)
    
    def convert_validation_exception_to_response(self, exception: ValidationException):
        """Python snake_case alias for convertValidationExceptionToResponse."""
        return self.convertValidationExceptionToResponse(exception)
    
    def expects_json_for_validation(self) -> bool:
        """Check if request expects JSON response for validation errors."""
        if not request:
            return False
        
        # Check Accept header
        if 'application/json' in request.headers.get('Accept', ''):
            return True
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return True
        
        # Check if request content type is JSON
        if request.content_type and 'application/json' in request.content_type:
            return True
        
        # Check if request is made to API routes
        if request.path.startswith('/api/'):
            return True
            
        return False
    
    def _convert_validation_to_json_response(self, exception: ValidationException):
        """Convert ValidationException to JSON response for API/AJAX requests."""
        response_data = {
            'message': str(exception),
            'errors': exception.errors
        }
        
        # Add error bag information if not default
        if exception.error_bag != 'default':
            response_data['error_bag'] = exception.error_bag
        
        return jsonify(response_data), exception.status
    
    def _convert_validation_to_redirect_response(self, exception: ValidationException):
        """Convert ValidationException to redirect response for web requests."""
        from ...http.response_factory import ResponseFactory
        
        # Get response factory
        response_factory = ResponseFactory()
        
        # Determine redirect URL
        redirect_url = self._get_validation_redirect_url(exception)
        
        # Flash errors to session
        self._flash_validation_errors_to_session(exception)
        
        # Flash input if specified
        if exception._with_input is not None:
            self._flash_input_to_session(exception._with_input)
        else:
            # Flash current request input by default
            self._flash_current_input_to_session()
        
        # Create redirect response
        from werkzeug.utils import redirect
        return redirect(redirect_url, code=302)
    
    def _get_validation_redirect_url(self, exception: ValidationException) -> str:
        """Get the URL to redirect to for validation errors."""
        # Use explicit redirectTo if set
        if exception.redirect_to:
            return exception.redirect_to
        
        # Use referer header (previous page)
        referer = request.headers.get('Referer')
        if referer:
            return referer
        
        # Fallback to root
        return '/'
    
    def _flash_validation_errors_to_session(self, exception: ValidationException):
        """Flash validation errors to session."""
        # Create ViewErrorBag with the errors
        error_bag = ViewErrorBag()
        error_bag.put(exception.error_bag, exception.errors)
        
        # Flash to session
        ShareErrorsFromSession.flash_errors_to_session(error_bag)
    
    def _flash_input_to_session(self, input_data: Dict[str, Any]):
        """Flash input data to session."""
        # Remove sensitive data
        safe_input = self._remove_sensitive_data(input_data)
        session['_old_input'] = safe_input
    
    def _flash_current_input_to_session(self):
        """Flash current request input to session."""
        input_data = {}
        
        # Get form data
        if request.form:
            input_data.update(request.form.to_dict())
        
        # Get JSON data
        if request.json:
            input_data.update(request.json)
        
        # Get query parameters
        if request.args:
            input_data.update(request.args.to_dict())
        
        # Flash the input
        if input_data:
            self._flash_input_to_session(input_data)
    
    def _remove_sensitive_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from input before flashing."""
        sensitive_keys = [
            'password', 'password_confirmation', 'current_password',
            'new_password', 'new_password_confirmation', '_token',
            'csrf_token', '_method', 'token', 'api_token',
            'access_token', 'refresh_token', 'secret', 'key'
        ]
        
        return {k: v for k, v in input_data.items() if k not in sensitive_keys}

    def render(self, error):
        """Render error response"""
        if request and self.expects_json():
            return self.render_json(error)
        return self.render_html(error)

    def expects_json(self) -> bool:
        """Check if request expects JSON response"""
        if not request:
            return False

        return (
            request.is_json or
            request.path.startswith('/api/') or
            'application/json' in request.headers.get('Accept', '')
        )

    def render_json(self, error):
        """Render JSON error response"""
        status_code = 500
        response = {
            'message': 'Server Error'
        }

        if isinstance(error, HTTPException):
            status_code = error.code
            response['message'] = error.description
        elif hasattr(error, 'status_code'):
            status_code = error.status_code
            response['message'] = str(error)

        # Add validation errors if present
        if hasattr(error, 'errors'):
            response['errors'] = error.errors

        # Add debug info in development
        if self.app.config.get('app.debug', False):
            response['exception'] = type(error).__name__
            response['trace'] = traceback.format_exc().split('\n')

        return jsonify(response), status_code

    def render_html(self, error):
        """Render HTML error page"""
        status_code = 500

        if isinstance(error, HTTPException):
            status_code = error.code
        elif hasattr(error, 'status_code'):
            status_code = error.status_code

        # Try to render custom error template
        try:
            return render_template(
                f'errors/{status_code}.html',
                error=error
            ), status_code
        except:
            # Fallback to generic error page
            return self.render_fallback(error, status_code)

    def render_fallback(self, error, status_code: int):
        """Render fallback error page"""
        debug = self.app.config.get('app.debug', False)
        message = str(error) if debug else 'An error occurred'

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {status_code}</title>
            <style>
                body {{ font-family: sans-serif; padding: 50px; background: #f8f9fa; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                .message {{ background: #f8f9fa; padding: 20px; border-radius: 5px; border-left: 4px solid #e74c3c; margin-bottom: 20px; }}
                .trace {{ background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 5px; white-space: pre-wrap; font-family: monospace; font-size: 14px; overflow-x: auto; }}
                .footer {{ margin-top: 30px; text-align: center; color: #6c757d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Error {status_code}</h1>
                <div class="message">{message}</div>
        '''

        if debug:
            html += f'<div class="trace">{traceback.format_exc()}</div>'

        html += '''
                <div class="footer">
                    <p>Larapy Framework</p>
                </div>
            </div>
        </body>
        </html>
        '''
        return html, status_code

    def handle_404(self, error):
        """Handle 404 errors"""
        from ...exceptions.http import NotFoundException
        return self.handle(NotFoundException())

    def handle_500(self, error):
        """Handle 500 errors"""
        return self.handle(error)