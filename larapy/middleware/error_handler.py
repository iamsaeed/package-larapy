"""Error handling middleware for Larapy"""

from ..http.middleware.middleware import Middleware
from typing import Callable

class ErrorHandlingMiddleware(Middleware):
    """Middleware to catch and handle exceptions in the request pipeline"""

    def __init__(self, app=None):
        self.app = app

    def handle(self, request, next_handler: Callable):
        """Wrap request handling in try-catch"""
        try:
            return next_handler(request)
        except Exception as e:
            # Let the exception handler deal with it
            if self.app:
                handler = self.app.resolve('exception.handler')
                return handler.handle(e)
            else:
                # Fallback if no app available
                raise e