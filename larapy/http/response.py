from flask import jsonify, make_response
from typing import Any, Dict

class Response:
    """Laravel-style Response helper"""
    
    @staticmethod
    def json(data: Any, status: int = 200, headers: Dict = None):
        """Return JSON response"""
        response = jsonify(data)
        response.status_code = status
        
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        
        return response
    
    @staticmethod
    def make(content: str, status: int = 200, headers: Dict = None):
        """Make a response"""
        response = make_response(content, status)
        
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        
        return response
