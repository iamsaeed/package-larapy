from abc import ABC, abstractmethod
from typing import Callable

class Middleware(ABC):
    """Base Middleware class"""
    
    @abstractmethod
    def handle(self, request, next_handler: Callable):
        """Handle an incoming request"""
        pass

# Example middleware implementation
class CorsMiddleware(Middleware):
    def handle(self, request, next_handler: Callable):
        """Handle CORS"""
        response = next_handler(request)
        
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response

class AuthMiddleware(Middleware):
    def handle(self, request, next_handler: Callable):
        """Handle authentication"""
        # Check for auth token
        token = request.headers.get('Authorization')
        
        if not token:
            from flask import jsonify
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Validate token (simplified)
        if not token.startswith('Bearer '):
            from flask import jsonify
            return jsonify({'error': 'Invalid token format'}), 401
        
        return next_handler(request)
