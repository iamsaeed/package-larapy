"""
Image validation rule.

This rule validates that the input is an image file upload. It extends the file rule
to specifically check for image MIME types and file extensions.
"""

from .file import FileRule


class ImageRule(FileRule):
    """
    Validates that the input is an image file upload.
    
    This rule extends the FileRule to specifically check for image files.
    It validates both that the input is a file and that it's an image type.
    """
    
    def __init__(self):
        super().__init__()
        
        # Common image MIME types
        self.allowed_mime_types = {
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/gif',
            'image/bmp',
            'image/svg+xml',
            'image/webp',
            'image/tiff',
            'image/x-icon',
            'image/vnd.microsoft.icon'
        }
        
        # Common image file extensions
        self.allowed_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
            '.svg', '.webp', '.tiff', '.tif', '.ico'
        }
    
    def passes(self, attribute, value, parameters=None):
        """
        Check if the value is an image file upload.
        
        Args:
            attribute (str): The name of the attribute being validated
            value: The value to validate
            parameters: Additional parameters (not used)
            
        Returns:
            bool: True if the value is an image file, False otherwise
        """
        # First check if it's a file at all
        if not super().passes(attribute, value):
            return False
        
        # Then check if it's an image
        return self._is_image(value)
    
    def _is_image(self, value):
        """
        Check if the file is an image based on MIME type or extension.
        
        Args:
            value: The file object to check
            
        Returns:
            bool: True if the file is an image, False otherwise
        """
        # Check MIME type if available
        mime_type = self._get_mime_type(value)
        if mime_type and mime_type.lower() in self.allowed_mime_types:
            return True
        
        # Check file extension if available
        filename = self._get_filename(value)
        if filename:
            extension = self._get_file_extension(filename)
            if extension.lower() in self.allowed_extensions:
                return True
        
        # Try to detect image using Python's imghdr module
        if self._detect_image_type(value):
            return True
        
        return False
    
    def _get_mime_type(self, value):
        """
        Get the MIME type of the file.
        
        Args:
            value: The file object
            
        Returns:
            str|None: The MIME type if available, None otherwise
        """
        # Check for content_type attribute (Flask FileStorage, etc.)
        if hasattr(value, 'content_type') and value.content_type:
            return value.content_type
        
        # Check for mimetype attribute 
        if hasattr(value, 'mimetype') and value.mimetype:
            return value.mimetype
        
        # For FastAPI UploadFile
        if hasattr(value, 'content_type') and callable(getattr(value, 'content_type', None)):
            try:
                return value.content_type
            except:
                pass
        
        return None
    
    def _get_filename(self, value):
        """
        Get the filename of the file.
        
        Args:
            value: The file object
            
        Returns:
            str|None: The filename if available, None otherwise
        """
        # Check for filename attribute (most file upload objects)
        if hasattr(value, 'filename') and value.filename:
            return value.filename
        
        # Check for name attribute (Python file objects)
        if hasattr(value, 'name') and value.name:
            return value.name
        
        return None
    
    def _get_file_extension(self, filename):
        """
        Get the file extension from a filename.
        
        Args:
            filename (str): The filename
            
        Returns:
            str: The file extension (including the dot)
        """
        import os
        return os.path.splitext(filename)[1]
    
    def _detect_image_type(self, value):
        """
        Try to detect if the file is an image using Python's imghdr module.
        
        Args:
            value: The file object
            
        Returns:
            bool: True if detected as image, False otherwise
        """
        try:
            import imghdr
            
            # If it's a file-like object with read method
            if hasattr(value, 'read') and hasattr(value, 'seek'):
                # Save current position
                current_pos = 0
                try:
                    current_pos = value.tell()
                except (OSError, IOError):
                    pass
                
                # Read some data for detection
                try:
                    value.seek(0)
                    data = value.read(512)  # Read first 512 bytes
                    
                    # Reset position
                    try:
                        value.seek(current_pos)
                    except (OSError, IOError):
                        pass
                    
                    # Try to detect image type from data
                    if data:
                        image_type = imghdr.what(None, h=data)
                        return image_type is not None
                        
                except (OSError, IOError, AttributeError):
                    pass
            
            # If it has a filename, try to detect from file
            filename = self._get_filename(value)
            if filename:
                try:
                    image_type = imghdr.what(filename)
                    return image_type is not None
                except (OSError, IOError):
                    pass
                    
        except ImportError:
            # imghdr not available
            pass
        
        return False
    
    def get_default_message(self):
        """
        Get the default validation error message.
        
        Returns:
            str: The default error message
        """
        return "The {attribute} must be an image."


# For backwards compatibility and easier imports
def image():
    """
    Create a new image validation rule.
    
    Returns:
        ImageRule: A new instance of the image rule
    """
    return ImageRule()