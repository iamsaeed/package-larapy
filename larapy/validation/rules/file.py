"""
File validation rule.

This rule validates that the input is a file upload. It checks for file-like objects
or specific file upload types depending on the web framework being used.
"""

from .base_rule import BaseRule


class FileRule(BaseRule):
    """
    Validates that the input is a file upload.
    
    This rule checks if the value is a file object or file upload. It supports
    various file object types commonly used in web frameworks like Flask, Django,
    FastAPI, etc.
    """
    
    def __init__(self):
        super().__init__()
    
    def passes(self, attribute, value, parameters=None):
        """
        Check if the value is a file upload.
        
        Args:
            attribute (str): The name of the attribute being validated
            value: The value to validate
            parameters: Additional parameters (not used)
            
        Returns:
            bool: True if the value is a file, False otherwise
        """
        if value is None:
            return False
        
        # Check for common file object types
        return self._is_file_like(value)
    
    def _is_file_like(self, value):
        """
        Check if the value is a file-like object.
        
        This method checks for various file object types:
        - Standard file objects (has read() and seek() methods)
        - Flask FileStorage objects
        - Django UploadedFile objects
        - FastAPI UploadFile objects
        - Python file objects
        - BytesIO/StringIO objects
        
        Args:
            value: The value to check
            
        Returns:
            bool: True if the value is file-like, False otherwise
        """
        # Check for None or empty values
        if value is None or value == '':
            return False
        
        # Check for file-like object methods
        if hasattr(value, 'read') and callable(getattr(value, 'read')):
            return True
        
        # Check for Flask FileStorage
        if hasattr(value, 'filename') and hasattr(value, 'content_type'):
            return True
        
        # Check for Django UploadedFile
        if hasattr(value, 'name') and hasattr(value, 'size') and hasattr(value, 'read'):
            return True
        
        # Check for FastAPI UploadFile
        if hasattr(value, 'filename') and hasattr(value, 'file'):
            return True
        
        # Check for Python file objects
        if hasattr(value, 'name') and hasattr(value, 'mode'):
            return True
        
        # Check for BytesIO/StringIO objects
        try:
            import io
            if isinstance(value, (io.BytesIO, io.StringIO, io.IOBase)):
                return True
        except ImportError:
            pass
        
        # Check for werkzeug FileStorage (used by Flask)
        try:
            from werkzeug.datastructures import FileStorage
            if isinstance(value, FileStorage):
                return True
        except ImportError:
            pass
        
        # Check for Django UploadedFile
        try:
            from django.core.files.uploadedfile import UploadedFile
            if isinstance(value, UploadedFile):
                return True
        except ImportError:
            pass
        
        # Check for FastAPI UploadFile
        try:
            from fastapi import UploadFile
            if isinstance(value, UploadFile):
                return True
        except ImportError:
            pass
        
        return False
    
    def get_default_message(self):
        """
        Get the default validation error message.
        
        Returns:
            str: The default error message
        """
        return "The {attribute} must be a file."


# For backwards compatibility and easier imports
def file():
    """
    Create a new file validation rule.
    
    Returns:
        FileRule: A new instance of the file rule
    """
    return FileRule()