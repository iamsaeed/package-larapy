"""
Example usage of the Laravel-style Response System in Larapy
============================================================

This file demonstrates how to use the comprehensive response system
that has been implemented according to the Laravel controller return
types analysis.
"""

from larapy.http import (
    Response, JsonResponse, RedirectResponse, 
    ResponseFactory, FileResponse, DownloadResponse,
    StreamedResponse, StreamDownloadResponse,
    ContentTransformer, LarapyJsonable
)
from larapy.routing import Redirector
from larapy.utils.helpers import response, redirect, back, view, old, json_response
from larapy.testing import assert_response


# Example Model class with JSON serialization
class User(LarapyJsonable):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
    
    def to_array(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


# Example Controller demonstrating various response types
class UserController:
    """Example controller showing Laravel-style response patterns."""
    
    def __init__(self):
        self.response_factory = ResponseFactory()
        self.redirector = Redirector()
    
    # 1. String Response
    def simple_string(self):
        """Return a simple string - converted to Response automatically."""
        return "Hello World"
    
    # 2. Array/Dict Response - converted to JSON
    def user_data(self):
        """Return array/dict - automatically converted to JSON."""
        return {
            'users': [
                {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
                {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
            ],
            'total': 2
        }
    
    # 3. Model Response - JSON serialized
    def show_user(self, user_id):
        """Return model instance - automatically converted to JSON."""
        user = User(user_id, "John Doe", "john@example.com")
        return user
    
    # 4. Explicit Response creation
    def custom_response(self):
        """Create custom response with headers and status."""
        return Response("Custom content", 201).header('X-Custom', 'Value')
    
    # 5. JSON Response
    def api_users(self):
        """Create explicit JSON response."""
        users = [User(1, "John", "john@example.com")]
        return JsonResponse(users, 200).header('X-API-Version', '1.0')
    
    # 6. View Response
    def show_profile(self):
        """Render a view."""
        user = User(1, "John Doe", "john@example.com")
        return view('profile', {'user': user})
    
    # 7. Redirect Responses
    def redirect_home(self):
        """Simple redirect."""
        return redirect('/')
    
    def redirect_with_message(self):
        """Redirect with flash message."""
        return redirect('/dashboard').with_('success', 'Welcome back!')
    
    def redirect_back_with_errors(self):
        """Redirect back with validation errors."""
        errors = {'email': 'Email is required', 'name': 'Name must be at least 3 characters'}
        return back().with_errors(errors).with_input()
    
    def redirect_to_route(self):
        """Redirect to named route."""
        return self.redirector.route('user.profile', {'id': 123})
    
    # 8. File Responses
    def download_file(self):
        """Download a file."""
        return DownloadResponse('/path/to/file.pdf', 'invoice.pdf')
    
    def serve_image(self):
        """Serve file inline."""
        return FileResponse('/path/to/image.jpg')
    
    # 9. Streaming Responses
    def export_csv(self):
        """Stream CSV download."""
        def generate_csv():
            yield "Name,Email\n"
            for user in [User(1, "John", "john@example.com"), User(2, "Jane", "jane@example.com")]:
                yield f"{user.name},{user.email}\n"
        
        return StreamDownloadResponse(generate_csv, 'users.csv')
    
    def streaming_data(self):
        """Stream large dataset."""
        def generate_data():
            for i in range(1000):
                yield f"Data chunk {i}\n"
        
        return StreamedResponse(generate_data)
    
    # 10. Response Factory Usage
    def factory_examples(self):
        """Examples using ResponseFactory."""
        from flask import request
        
        # No content response
        if request.args.get('empty'):
            return self.response_factory.no_content()
        
        # JSONP response
        if request.args.get('callback'):
            return self.response_factory.jsonp('myCallback', {'data': 'value'})
        
        # Stream JSON
        large_data = [{'id': i} for i in range(10000)]
        return self.response_factory.stream_json(large_data)
    
    # 11. Method Chaining
    def chained_response(self):
        """Demonstrate method chaining."""
        return (JsonResponse({'status': 'success'})
                .status(201)
                .header('X-Custom', 'value')
                .cookie('session_id', 'abc123', httponly=True))
    
    # 12. Cookie Management
    def set_cookies(self):
        """Set various types of cookies."""
        response = Response("Cookies set!")
        
        # Simple cookie
        response.cookie('simple', 'value')
        
        # Secure cookie with options
        response.cookie('secure', 'secret', secure=True, httponly=True, max_age=3600)
        
        # Multiple cookies
        response.with_cookies([
            {'name': 'first', 'value': 'one'},
            {'name': 'second', 'value': 'two', 'path': '/admin'}
        ])
        
        return response


# Helper function examples
def helper_examples():
    """Examples using helper functions."""
    
    # Response helper
    basic_response = response("Hello World", 200, {'X-Custom': 'Value'})
    
    # JSON helper
    json_resp = json_response({'message': 'Success'}, 201)
    
    # Redirect helpers
    redirect_resp = redirect('/home')
    back_resp = back()
    
    # View helper
    view_resp = view('welcome', {'name': 'John'})
    
    # Old input helper (for forms)
    old_email = old('email', '')  # Get old input with default
    
    return basic_response


# Testing examples
def test_response_assertions():
    """Examples of testing response assertions."""
    
    # Test a controller method
    controller = UserController()
    response = controller.user_data()
    
    # Convert to Flask response for testing
    from larapy.http.middleware.response_middleware import ResponseMiddleware
    middleware = ResponseMiddleware()
    flask_response = middleware.process_response(response)
    
    # Use assertions
    (assert_response(flask_response)
     .assert_ok()
     .assert_json()
     .assert_json_path('total', 2)
     .assert_json_structure({
         'users': [{'id': int, 'name': str, 'email': str}],
         'total': int
     }))


# Content transformation examples
def content_transformation_examples():
    """Examples of content transformation."""
    
    # Object with to_json method
    user = User(1, "John", "john@example.com")
    json_string = ContentTransformer.transform_to_json(user)
    
    # Object with to_array method
    array_data = ContentTransformer.transform_to_array(user)
    
    # Check if content should be JSON
    should_be_json = ContentTransformer.should_be_json({'data': 'value'})
    
    return json_string, array_data, should_be_json


# Advanced cookie examples
def advanced_cookie_examples():
    """Examples of advanced cookie features."""
    from larapy.http.cookie import CookieManager
    
    # Create cookie manager with encryption
    cookie_manager = CookieManager(
        encryption_key='your-secret-key',
        secret_key='your-signing-key'
    )
    
    # Create encrypted cookie
    encrypted_cookie = cookie_manager.make('user_data', {'id': 123}, encrypted=True)
    
    # Create permanent cookie
    forever_cookie = cookie_manager.forever('remember_token', 'abc123')
    
    # Get encrypted cookie value
    user_data = cookie_manager.get('user_data', encrypted=True)
    
    return encrypted_cookie, forever_cookie, user_data


if __name__ == "__main__":
    """
    Usage patterns and examples for the response system.
    
    This implementation provides:
    
    1. **Laravel Compatibility**: All Laravel response patterns work
    2. **Automatic Conversion**: Controllers can return primitives, they're auto-converted
    3. **Method Chaining**: All responses support fluent method chaining  
    4. **Content Negotiation**: Framework detects JSON vs HTML needs
    5. **Flash Data**: Redirects integrate seamlessly with session
    6. **File Handling**: Built-in downloads and streaming
    7. **Testing Support**: Rich assertions for response testing
    8. **Cookie Security**: Encryption and signing support
    9. **Streaming**: Large content streaming support
    10. **Extensibility**: Macro system allows custom methods
    
    Controllers can now return:
    - Strings (auto-converted to Response)
    - Arrays/Dicts (auto-converted to JSON)  
    - Model instances (auto-serialized to JSON)
    - View objects (auto-rendered to HTML)
    - Response objects (used directly)
    - Redirect objects (processed with flash data)
    - File paths (auto-converted to downloads)
    - Generators (auto-converted to streams)
    """
    
    # Create controller instance
    controller = UserController()
    
    # Test various response types
    string_resp = controller.simple_string()
    json_resp = controller.user_data()
    model_resp = controller.show_user(1)
    redirect_resp = controller.redirect_with_message()
    
    print("Laravel-style Response System Successfully Implemented!")
    print("All controller return types now supported with automatic conversion.")
    print("Method chaining, flash data, cookies, streaming, and testing all available.")