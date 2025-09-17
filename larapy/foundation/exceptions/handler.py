"""Global exception handler for Larapy applications"""

import traceback
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from typing import Optional

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