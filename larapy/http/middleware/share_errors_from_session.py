"""Laravel-compatible ShareErrorsFromSession middleware."""

from typing import Callable, Any
from flask import session, g
from ...validation.view_error_bag import ViewErrorBag


class ShareErrorsFromSession:
    """
    Laravel-compatible middleware that shares errors from session with all views.
    
    This middleware runs on every request and makes the 'errors' variable
    available to all templates, containing a ViewErrorBag with validation errors.
    """
    
    def __init__(self):
        """Initialize the middleware."""
        pass
    
    def __call__(self, request, response_handler: Callable) -> Any:
        """
        Handle the request and share errors with views.
        
        Args:
            request: The current request
            response_handler: The next middleware/handler in chain
            
        Returns:
            Any: The response from the next handler
        """
        # Get errors from session or create empty ViewErrorBag
        errors = self._get_errors_from_session()
        
        # Make errors available to all views
        self._share_errors_with_views(errors)
        
        # Continue with the request
        response = response_handler(request)
        
        # Clean up flashed errors after first use
        self._cleanup_flashed_errors()
        
        return response
    
    def _get_errors_from_session(self) -> ViewErrorBag:
        """
        Get errors from session or create empty ViewErrorBag.
        
        Returns:
            ViewErrorBag: Errors from session or empty bag
        """
        if 'errors' in session:
            # Get errors from session
            session_errors = session.get('errors', {})
            
            if isinstance(session_errors, dict):
                # Convert dict to ViewErrorBag
                errors = ViewErrorBag()
                for bag_name, bag_data in session_errors.items():
                    errors.put(bag_name, bag_data)
                return errors
            elif hasattr(session_errors, '_bags'):
                # Already a ViewErrorBag
                return session_errors
        
        # Return empty ViewErrorBag
        return ViewErrorBag()
    
    def _share_errors_with_views(self, errors: ViewErrorBag):
        """
        Share errors with all views through Flask's g object.
        
        Args:
            errors: The ViewErrorBag to share
        """
        # Store in Flask's g object for template access
        g.errors = errors
        
        # Also store in a way that view engines can access
        if not hasattr(g, 'view_data'):
            g.view_data = {}
        g.view_data['errors'] = errors
    
    def _cleanup_flashed_errors(self):
        """
        Clean up flashed errors from session after first use.
        
        This ensures that error messages only persist for one request,
        following Laravel's flash data behavior.
        """
        if 'errors' in session:
            # Remove errors from session after first use
            session.pop('errors', None)
    
    @staticmethod
    def flash_errors_to_session(errors: ViewErrorBag):
        """
        Flash errors to session for next request.
        
        Args:
            errors: The ViewErrorBag to flash
        """
        # Convert ViewErrorBag to serializable format
        error_data = {}
        for bag_name, bag in errors.getBags().items():
            error_data[bag_name] = bag.to_dict()
        
        # Store in session
        session['errors'] = error_data
    
    @staticmethod
    def add_error_to_session(bag_name: str = 'default', field: str = None, message: str = None, errors: dict = None):
        """
        Add a single error or multiple errors to session.
        
        Args:
            bag_name: The error bag name
            field: The field name (if adding single error)
            message: The error message (if adding single error)
            errors: Dictionary of field->messages (if adding multiple)
        """
        # Get existing errors or create new ViewErrorBag
        current_errors = ShareErrorsFromSession()._get_errors_from_session()
        
        # Get the specific bag
        bag = current_errors.getBag(bag_name)
        
        if field and message:
            # Add single error
            bag.add(field, message)
        elif errors:
            # Add multiple errors
            for field_name, field_messages in errors.items():
                if isinstance(field_messages, list):
                    for msg in field_messages:
                        bag.add(field_name, msg)
                else:
                    bag.add(field_name, field_messages)
        
        # Flash updated errors back to session
        ShareErrorsFromSession.flash_errors_to_session(current_errors)


def share_errors_from_session():
    """
    Factory function to create ShareErrorsFromSession middleware instance.
    
    Returns:
        ShareErrorsFromSession: Middleware instance
    """
    return ShareErrorsFromSession()


# Alias for convenience
ErrorSharingMiddleware = ShareErrorsFromSession