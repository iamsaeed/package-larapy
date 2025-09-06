"""
Test suite for Larapy Authentication System

Tests the AuthManager, Authenticatable mixin, middleware, and facade.
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask, session
from werkzeug.security import generate_password_hash

from larapy.auth.auth_manager import AuthManager
from larapy.auth.authenticatable import Authenticatable
from larapy.auth.middleware import auth_required, guest_only, auth_api, guest_api
from larapy.support.facades.auth import Auth
from larapy.foundation.application import Application


class MockUser(Authenticatable):
    """Mock User model for testing"""
    
    def __init__(self, id=1, email='test@example.com', password='password'):
        self.id = id
        self.email = email
        self.password = generate_password_hash(password)
        self.remember_token = None
        
    @classmethod
    def find(cls, id):
        if id == 1:
            return cls()
        return None
    
    @classmethod
    def where(cls, field, value):
        mock_query = Mock()
        if field == 'email' and value == 'test@example.com':
            mock_query.first.return_value = cls()
        else:
            mock_query.first.return_value = None
        return mock_query


class TestAuthManager:
    """Test the AuthManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.secret_key = 'test-secret-key'
        self.auth_manager = AuthManager(self.app)
        self.auth_manager.set_user_model(MockUser)
        
    def test_set_user_model(self):
        """Test setting the user model"""
        auth = AuthManager()
        auth.set_user_model(MockUser)
        assert auth._user_model == MockUser
        
    def test_attempt_success(self):
        """Test successful authentication attempt"""
        with self.app.test_request_context():
            result = self.auth_manager.attempt({
                'email': 'test@example.com',
                'password': 'password'
            })
            assert result is True
            assert 'user_id' in session
            assert session['user_authenticated'] is True
            
    def test_attempt_failure_wrong_password(self):
        """Test failed authentication with wrong password"""
        with self.app.test_request_context():
            result = self.auth_manager.attempt({
                'email': 'test@example.com',
                'password': 'wrong-password'
            })
            assert result is False
            assert 'user_id' not in session
            
    def test_attempt_failure_user_not_found(self):
        """Test failed authentication with non-existent user"""
        with self.app.test_request_context():
            result = self.auth_manager.attempt({
                'email': 'nonexistent@example.com',
                'password': 'password'
            })
            assert result is False
            assert 'user_id' not in session
            
    def test_login(self):
        """Test manual login"""
        with self.app.test_request_context():
            user = MockUser()
            result = self.auth_manager.login(user)
            
            assert result == user
            assert session['user_id'] == user.id
            assert session['user_authenticated'] is True
            
    def test_login_using_id_success(self):
        """Test login using user ID"""
        with self.app.test_request_context():
            result = self.auth_manager.login_using_id(1)
            
            assert result is not None
            assert session['user_id'] == 1
            assert session['user_authenticated'] is True
            
    def test_login_using_id_failure(self):
        """Test login using non-existent user ID"""
        with self.app.test_request_context():
            result = self.auth_manager.login_using_id(999)
            
            assert result is None
            assert 'user_id' not in session
            
    def test_logout(self):
        """Test logout functionality"""
        with self.app.test_request_context():
            # Login first
            user = MockUser()
            self.auth_manager.login(user)
            
            # Logout
            self.auth_manager.logout()
            
            assert 'user_id' not in session
            assert 'user_authenticated' not in session
            
    def test_user_authenticated(self):
        """Test getting authenticated user"""
        with self.app.test_request_context():
            # Login first
            user = MockUser()
            self.auth_manager.login(user)
            
            # Get user
            current_user = self.auth_manager.user()
            assert current_user is not None
            assert current_user.id == user.id
            
    def test_user_not_authenticated(self):
        """Test getting user when not authenticated"""
        with self.app.test_request_context():
            current_user = self.auth_manager.user()
            assert current_user is None
            
    def test_check_authenticated(self):
        """Test check method when authenticated"""
        with self.app.test_request_context():
            user = MockUser()
            self.auth_manager.login(user)
            
            assert self.auth_manager.check() is True
            
    def test_check_not_authenticated(self):
        """Test check method when not authenticated"""
        with self.app.test_request_context():
            assert self.auth_manager.check() is False
            
    def test_guest_not_authenticated(self):
        """Test guest method when not authenticated"""
        with self.app.test_request_context():
            assert self.auth_manager.guest() is True
            
    def test_guest_authenticated(self):
        """Test guest method when authenticated"""
        with self.app.test_request_context():
            user = MockUser()
            self.auth_manager.login(user)
            
            assert self.auth_manager.guest() is False
            
    def test_id(self):
        """Test getting user ID"""
        with self.app.test_request_context():
            user = MockUser()
            self.auth_manager.login(user)
            
            assert self.auth_manager.id() == user.id
            
    def test_once_valid_credentials(self):
        """Test once method with valid credentials"""
        result = self.auth_manager.once({
            'email': 'test@example.com',
            'password': 'password'
        })
        assert result is True
        
    def test_once_invalid_credentials(self):
        """Test once method with invalid credentials"""
        result = self.auth_manager.once({
            'email': 'test@example.com',
            'password': 'wrong-password'
        })
        assert result is False
        
    def test_validate(self):
        """Test validate method"""
        valid = self.auth_manager.validate({
            'email': 'test@example.com',
            'password': 'password'
        })
        assert valid is True
        
        invalid = self.auth_manager.validate({
            'email': 'test@example.com',
            'password': 'wrong-password'
        })
        assert invalid is False


class TestAuthenticatable:
    """Test the Authenticatable mixin"""
    
    def test_set_password(self):
        """Test password hashing"""
        user = MockUser()
        original_password = user.password
        
        user.set_password('new-password')
        
        assert user.password != 'new-password'  # Should be hashed
        assert user.password != original_password  # Should be different
        
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        user = MockUser()
        assert user.verify_password('password') is True
        
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        user = MockUser()
        assert user.verify_password('wrong-password') is False
        
    def test_set_remember_token(self):
        """Test setting remember token"""
        user = MockUser()
        user.set_remember_token('test-token')
        
        assert user.remember_token == 'test-token'
        
    def test_set_remember_token_auto_generate(self):
        """Test auto-generating remember token"""
        user = MockUser()
        user.set_remember_token()
        
        assert user.remember_token is not None
        assert len(user.remember_token) == 60
        
    def test_get_remember_token(self):
        """Test getting remember token"""
        user = MockUser()
        user.remember_token = 'test-token'
        
        assert user.get_remember_token() == 'test-token'
        
    def test_auth_identifier_methods(self):
        """Test authentication identifier methods"""
        user = MockUser()
        
        assert user.get_auth_identifier() == user.id
        assert user.get_auth_identifier_name() == 'id'
        assert user.get_auth_password() == user.password
        assert user.get_auth_password_name() == 'password'


class TestMiddleware:
    """Test authentication middleware"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.secret_key = 'test-secret-key'
        
    def test_auth_required_authenticated(self):
        """Test auth_required with authenticated user"""
        @auth_required()
        def protected_route():
            return 'protected content'
            
        with self.app.test_request_context():
            # Set up authenticated session
            session['user_authenticated'] = True
            session['user_id'] = 1
            
            result = protected_route()
            assert result == 'protected content'
            
    def test_auth_required_not_authenticated(self):
        """Test auth_required with unauthenticated user"""
        @auth_required()
        def protected_route():
            return 'protected content'
            
        with self.app.test_request_context():
            result = protected_route()
            # Should return redirect response
            assert result.status_code == 302
            
    def test_auth_api_not_authenticated(self):
        """Test auth_api with unauthenticated user"""
        @auth_api
        def protected_api_route():
            return {'message': 'protected content'}
            
        with self.app.test_request_context():
            result = protected_api_route()
            # Should return JSON error
            assert result[1] == 401
            
    def test_guest_only_authenticated(self):
        """Test guest_only with authenticated user"""
        @guest_only()
        def guest_route():
            return 'guest content'
            
        with self.app.test_request_context():
            # Set up authenticated session
            session['user_authenticated'] = True
            session['user_id'] = 1
            
            result = guest_route()
            # Should return redirect response
            assert result.status_code == 302
            
    def test_guest_only_not_authenticated(self):
        """Test guest_only with unauthenticated user"""
        @guest_only()
        def guest_route():
            return 'guest content'
            
        with self.app.test_request_context():
            result = guest_route()
            assert result == 'guest content'


class TestAuthFacade:
    """Test the Auth facade"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = Application()
        self.app._flask_app.secret_key = 'test-secret-key'
        
        # Mock the facade root to return our auth manager
        self.auth_manager = AuthManager(self.app)
        self.auth_manager.set_user_model(MockUser)
        
        # Patch the facade to use our auth manager
        Auth._get_facade_root = lambda: self.auth_manager
        
    def test_facade_attempt(self):
        """Test Auth facade attempt method"""
        with self.app._flask_app.test_request_context():
            result = Auth.attempt({
                'email': 'test@example.com',
                'password': 'password'
            })
            assert result is True
            
    def test_facade_check(self):
        """Test Auth facade check method"""
        with self.app._flask_app.test_request_context():
            # Not authenticated initially
            assert Auth.check() is False
            
            # Login
            Auth.attempt({
                'email': 'test@example.com',
                'password': 'password'
            })
            
            # Should be authenticated now
            assert Auth.check() is True
            
    def test_facade_user(self):
        """Test Auth facade user method"""
        with self.app._flask_app.test_request_context():
            # Login first
            Auth.attempt({
                'email': 'test@example.com',
                'password': 'password'
            })
            
            user = Auth.user()
            assert user is not None
            assert user.email == 'test@example.com'
            
    def test_facade_logout(self):
        """Test Auth facade logout method"""
        with self.app._flask_app.test_request_context():
            # Login first
            Auth.attempt({
                'email': 'test@example.com',
                'password': 'password'
            })
            
            # Logout
            Auth.logout()
            
            # Should not be authenticated
            assert Auth.check() is False
            assert Auth.user() is None


if __name__ == '__main__':
    pytest.main([__file__])