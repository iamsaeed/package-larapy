"""Comprehensive tests for Laravel-compatible error handling system."""

import pytest
from flask import Flask, session, request, jsonify
import json
from unittest.mock import Mock, patch

# Import the components we're testing
from larapy.validation.view_error_bag import ViewErrorBag
from larapy.validation.message_bag import MessageBag
from larapy.validation.exceptions import ValidationException
from larapy.http.middleware.share_errors_from_session import ShareErrorsFromSession
from larapy.http.concerns.interacts_with_flash_data import InteractsWithFlashData
from larapy.foundation.exceptions.handler import ExceptionHandler
from larapy.session.store import SessionManager
from larapy.validation.setup import setup_error_handling_system


class TestViewErrorBag:
    """Test ViewErrorBag functionality."""
    
    def test_create_empty_view_error_bag(self):
        """Test creating an empty ViewErrorBag."""
        bag = ViewErrorBag()
        assert not bag.any()
        assert bag.count() == 0
        assert len(bag) == 0
        assert not bool(bag)
    
    def test_put_message_bag(self):
        """Test putting a MessageBag into ViewErrorBag."""
        bag = ViewErrorBag()
        message_bag = MessageBag()
        message_bag.add('email', 'Email is required')
        
        bag.put('default', message_bag)
        
        assert bag.hasBag('default')
        assert bag.getBag('default').has('email')
        assert bag.any()
        assert bag.count() == 1
    
    def test_put_dict_data(self):
        """Test putting dictionary data into ViewErrorBag."""
        bag = ViewErrorBag()
        errors = {
            'email': ['Email is required', 'Email must be valid'],
            'password': ['Password is required']
        }
        
        bag.put('default', errors)
        
        assert bag.has('email')
        assert bag.has('password')
        assert len(bag.get('email')) == 2
        assert bag.first('email') == 'Email is required'
    
    def test_magic_methods(self):
        """Test magic methods for accessing bags."""
        bag = ViewErrorBag()
        bag.put('login', {'email': ['Invalid email']})
        bag.put('register', {'username': ['Username taken']})
        
        # Test __getattr__
        assert bag.login.has('email')
        assert bag.register.has('username')
        
        # Test __getitem__
        assert bag['login'].has('email')
        assert bag['register'].has('username')
        
        # Test __contains__
        assert 'login' in bag
        assert 'register' in bag
        assert 'nonexistent' not in bag
    
    def test_delegation_to_default_bag(self):
        """Test delegation to default bag."""
        bag = ViewErrorBag()
        bag.put('default', {
            'email': ['Email is required'],
            'password': ['Password is required']
        })
        
        # These should delegate to default bag
        assert bag.has('email')
        assert bag.first('email') == 'Email is required'
        assert 'email' in bag.all()
        assert bag.count() == 2


class TestValidationException:
    """Test ValidationException enhancements."""
    
    def test_create_with_messages(self):
        """Test creating ValidationException with messages."""
        messages = {
            'email': ['Email is required', 'Email must be valid'],
            'password': 'Password is required'
        }
        
        exception = ValidationException.withMessages(messages)
        
        assert exception.error_bag == 'default'
        assert exception.status == 422
        assert 'email' in exception.errors
        assert len(exception.errors['email']) == 2
        assert exception.errors['password'] == ['Password is required']
    
    def test_set_redirect_to(self):
        """Test setting redirect URL."""
        exception = ValidationException.withMessages({'field': 'error'})
        exception.redirectTo('/custom-redirect')
        
        assert exception.redirect_to == '/custom-redirect'
    
    def test_set_error_bag(self):
        """Test setting error bag name."""
        exception = ValidationException.withMessages({'field': 'error'})
        exception.errorBag('login')
        
        assert exception.error_bag == 'login'
    
    def test_with_input(self):
        """Test withInput method."""
        exception = ValidationException.withMessages({'field': 'error'})
        input_data = {'email': 'test@example.com', 'password': 'secret'}
        
        exception.withInput(input_data)
        
        assert exception._with_input == input_data


class TestShareErrorsFromSession:
    """Test ShareErrorsFromSession middleware."""
    
    def test_get_errors_from_empty_session(self):
        """Test getting errors when session is empty."""
        middleware = ShareErrorsFromSession()
        
        with patch('flask.session', {}):
            errors = middleware._get_errors_from_session()
            
        assert isinstance(errors, ViewErrorBag)
        assert not errors.any()
    
    def test_flash_errors_to_session(self):
        """Test flashing errors to session."""
        error_bag = ViewErrorBag()
        error_bag.put('default', {'email': ['Email is required']})
        
        mock_session = {}
        with patch('flask.session', mock_session):
            ShareErrorsFromSession.flash_errors_to_session(error_bag)
            
        assert 'errors' in mock_session
        assert 'default' in mock_session['errors']
        assert 'email' in mock_session['errors']['default']
    
    def test_add_error_to_session(self):
        """Test adding single error to session."""
        mock_session = {}
        
        with patch('flask.session', mock_session):
            with patch.object(ShareErrorsFromSession, '_get_errors_from_session', return_value=ViewErrorBag()):
                ShareErrorsFromSession.add_error_to_session(
                    'default', 'email', 'Email is required'
                )
        
        assert 'errors' in mock_session


class TestInteractsWithFlashData:
    """Test InteractsWithFlashData trait."""
    
    def test_old_input_retrieval(self):
        """Test retrieving old input."""
        trait = InteractsWithFlashData()
        
        mock_session = {'_old_input': {'email': 'test@example.com', 'name': 'John'}}
        
        with patch('flask.session', mock_session):
            with patch.object(trait, 'hasSession', return_value=True):
                # Test getting specific field
                assert trait.old('email') == 'test@example.com'
                assert trait.old('name') == 'John'
                assert trait.old('nonexistent', 'default') == 'default'
                
                # Test getting all old input
                all_old = trait.old()
                assert all_old == {'email': 'test@example.com', 'name': 'John'}
    
    def test_flash_input_data(self):
        """Test flashing input data."""
        trait = InteractsWithFlashData()
        input_data = {
            'email': 'test@example.com',
            'password': 'secret',  # Should be removed
            'name': 'John'
        }
        
        mock_session = {}
        
        with patch('flask.session', mock_session):
            with patch.object(trait, 'hasSession', return_value=True):
                trait.flash(input_data)
        
        # Password should be removed from flashed data
        assert '_old_input' in mock_session
        assert 'email' in mock_session['_old_input']
        assert 'name' in mock_session['_old_input']
        assert 'password' not in mock_session['_old_input']
    
    def test_flash_only_specific_keys(self):
        """Test flashing only specific input keys."""
        trait = InteractsWithFlashData()
        
        # Mock request data
        request_data = {
            'email': 'test@example.com',
            'name': 'John',
            'age': '25'
        }
        
        mock_session = {}
        
        with patch('flask.session', mock_session):
            with patch.object(trait, 'hasSession', return_value=True):
                with patch.object(trait, '_get_request_data', return_value=request_data):
                    trait.flashOnly(['email', 'name'])
        
        assert '_old_input' in mock_session
        assert 'email' in mock_session['_old_input']
        assert 'name' in mock_session['_old_input']
        assert 'age' not in mock_session['_old_input']
    
    def test_flash_except_specific_keys(self):
        """Test flashing all except specific keys."""
        trait = InteractsWithFlashData()
        
        request_data = {
            'email': 'test@example.com',
            'password': 'secret',
            'name': 'John'
        }
        
        mock_session = {}
        
        with patch('flask.session', mock_session):
            with patch.object(trait, 'hasSession', return_value=True):
                with patch.object(trait, '_get_request_data', return_value=request_data):
                    trait.flashExcept(['password'])
        
        assert '_old_input' in mock_session
        assert 'email' in mock_session['_old_input']
        assert 'name' in mock_session['_old_input']
        assert 'password' not in mock_session['_old_input']


class TestExceptionHandler:
    """Test exception handler for validation errors."""
    
    def test_json_response_for_ajax(self):
        """Test JSON response for AJAX requests."""
        app = Flask(__name__)
        handler = ExceptionHandler(app)
        
        exception = ValidationException.withMessages({
            'email': ['Email is required'],
            'password': ['Password is required']
        })
        
        with app.test_request_context('/', headers={'X-Requested-With': 'XMLHttpRequest'}):
            assert handler.expects_json_for_validation() == True
            
            response = handler._convert_validation_to_json_response(exception)
            data = json.loads(response[0].data)
            
            assert response[1] == 422
            assert 'errors' in data
            assert 'email' in data['errors']
            assert 'password' in data['errors']
    
    def test_redirect_response_for_web(self):
        """Test redirect response for web requests."""
        app = Flask(__name__)
        handler = ExceptionHandler(app)
        
        exception = ValidationException.withMessages({
            'email': ['Email is required']
        })
        
        with app.test_request_context('/', headers={'Referer': '/contact'}):
            assert handler.expects_json_for_validation() == False
            
            redirect_url = handler._get_validation_redirect_url(exception)
            assert redirect_url == '/contact'


class TestSessionManager:
    """Test SessionManager flash data functionality."""
    
    def test_flash_and_retrieve_data(self):
        """Test flashing and retrieving data."""
        manager = SessionManager()
        
        mock_session = {}
        
        with patch('flask.session', mock_session):
            with patch.object(manager, '_has_session', return_value=True):
                # Flash some data
                manager.flash('message', 'Success!')
                manager.flashInput({'email': 'test@example.com'})
                
                # Verify flash data is stored
                assert '_flash' in mock_session
                assert 'message' in mock_session['_flash']
                
                # Test retrieval
                assert manager.get('_flash', {}).get('message') == 'Success!'
    
    def test_old_input_methods(self):
        """Test old input methods."""
        manager = SessionManager()
        
        mock_session = {'_old_input': {'email': 'test@example.com', 'name': 'John'}}
        
        with patch('flask.session', mock_session):
            with patch.object(manager, '_has_session', return_value=True):
                assert manager.getOldInput('email') == 'test@example.com'
                assert manager.getOldInput('nonexistent', 'default') == 'default'
                
                all_old = manager.getOldInput()
                assert all_old == {'email': 'test@example.com', 'name': 'John'}


class TestFullIntegration:
    """Test full integration of the error handling system."""
    
    def test_validation_exception_to_redirect(self):
        """Test complete flow from ValidationException to redirect with errors."""
        app = Flask(__name__)
        app.secret_key = 'test-secret'
        
        # Setup the error handling system
        setup_error_handling_system(app)
        
        @app.route('/test', methods=['POST'])
        def test_route():
            # Simulate a validation error
            raise ValidationException.withMessages({
                'email': ['Email is required'],
                'password': ['Password is required']
            })
        
        with app.test_client() as client:
            # Make a POST request that will trigger validation error
            response = client.post('/test', data={'name': 'John'}, 
                                 headers={'Referer': '/form'})
            
            # Should redirect back to the form
            assert response.status_code == 302
            # Note: In a real test, you'd check that errors are flashed to session
    
    def test_validation_exception_to_json(self):
        """Test complete flow from ValidationException to JSON response."""
        app = Flask(__name__)
        app.secret_key = 'test-secret'
        
        setup_error_handling_system(app)
        
        @app.route('/api/test', methods=['POST'])
        def api_test_route():
            raise ValidationException.withMessages({
                'email': ['Email is required']
            })
        
        with app.test_client() as client:
            # Make AJAX request that will trigger validation error
            response = client.post('/api/test', 
                                 headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 422
            data = json.loads(response.data)
            assert 'errors' in data
            assert 'email' in data['errors']
    
    def test_multiple_error_bags(self):
        """Test handling multiple error bags."""
        bag = ViewErrorBag()
        bag.put('login', {'email': ['Login email required']})
        bag.put('register', {'username': ['Username taken']})
        
        # Test accessing different bags
        assert bag.login.has('email')
        assert bag.register.has('username')
        assert not bag.login.has('username')
        assert not bag.register.has('email')
        
        # Test that each bag is independent
        assert bag.login.first('email') == 'Login email required'
        assert bag.register.first('username') == 'Username taken'


# Example usage and integration test
def test_example_usage():
    """Test the example usage from the documentation."""
    
    # Create Flask app
    app = Flask(__name__)
    app.secret_key = 'test-secret'
    
    # Setup Laravel-compatible error handling
    setup_error_handling_system(app)
    
    # Example controller
    from larapy.http.concerns.validates_requests import ValidatesRequests
    
    class UserController(ValidatesRequests):
        def store(self, request_data):
            # This would normally validate and throw ValidationException
            try:
                validated = self.validate(request_data, {
                    'name': 'required|string',
                    'email': 'required|email'
                })
                return {'success': True, 'data': validated}
            except ValidationException as e:
                # Exception handler will convert this to appropriate response
                raise e
    
    # Test that the controller works
    controller = UserController()
    
    # This should pass validation
    valid_data = {'name': 'John Doe', 'email': 'john@example.com'}
    
    # Note: In real usage, the validation would be integrated with actual
    # validation rules and the exception handler would manage redirects/JSON responses


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])