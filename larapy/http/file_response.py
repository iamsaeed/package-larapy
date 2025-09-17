"""File response classes for file downloads and serving."""

import os
import mimetypes
from typing import Dict, Optional
from flask import send_file, send_from_directory, Response as FlaskResponse

from ..contracts import Macroable
from .concerns import ResponseTrait


class FileResponse(ResponseTrait, Macroable):
    """Laravel-style FileResponse class for serving files."""
    
    def __init__(self, file_path: str, headers: Optional[Dict] = None, disposition: str = 'inline'):
        """Initialize the file response."""
        super().__init__()
        self._file_path = file_path
        self._disposition = disposition
        self._status_code = 200
        
        if headers:
            self._headers.update(headers)
        
        # Auto-detect content type if not provided
        if 'Content-Type' not in self._headers:
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type:
                self._headers['Content-Type'] = content_type
        
        # Set disposition header
        filename = os.path.basename(file_path)
        self._headers['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    
    def get_file_path(self) -> str:
        """Get the file path."""
        return self._file_path
    
    def set_file_path(self, file_path: str):
        """Set the file path."""
        self._file_path = file_path
        return self
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        if not os.path.exists(self._file_path):
            raise FileNotFoundError(f"File not found: {self._file_path}")
        
        # Use Flask's send_file for efficient file serving
        response = send_file(
            self._file_path,
            as_attachment=(self._disposition == 'attachment'),
            download_name=os.path.basename(self._file_path)
        )
        
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    @staticmethod
    def create(file_path: str, headers: Optional[Dict] = None, disposition: str = 'inline'):
        """Create a new FileResponse instance."""
        return FileResponse(file_path, headers, disposition)


class DownloadResponse(FileResponse):
    """Laravel-style DownloadResponse class for file downloads."""
    
    def __init__(self, file_path: str, name: Optional[str] = None, headers: Optional[Dict] = None):
        """Initialize the download response."""
        # Always use attachment disposition for downloads
        super().__init__(file_path, headers, 'attachment')
        
        if name:
            # Override the filename in Content-Disposition header
            self._headers['Content-Disposition'] = f'attachment; filename="{name}"'
            self._download_name = name
        else:
            self._download_name = os.path.basename(file_path)
    
    def get_download_name(self) -> str:
        """Get the download filename."""
        return self._download_name
    
    def set_download_name(self, name: str):
        """Set the download filename."""
        self._download_name = name
        self._headers['Content-Disposition'] = f'attachment; filename="{name}"'
        return self
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        if not os.path.exists(self._file_path):
            raise FileNotFoundError(f"File not found: {self._file_path}")
        
        # Use Flask's send_file for downloads
        response = send_file(
            self._file_path,
            as_attachment=True,
            download_name=self._download_name
        )
        
        return self._apply_headers_and_cookies(response)
    
    @staticmethod
    def create(file_path: str, name: Optional[str] = None, headers: Optional[Dict] = None):
        """Create a new DownloadResponse instance."""
        return DownloadResponse(file_path, name, headers)


class DirectoryResponse(ResponseTrait, Macroable):
    """Response for serving files from a directory."""
    
    def __init__(self, directory: str, filename: str, headers: Optional[Dict] = None, disposition: str = 'inline'):
        """Initialize the directory response."""
        super().__init__()
        self._directory = directory
        self._filename = filename
        self._disposition = disposition
        self._status_code = 200
        
        if headers:
            self._headers.update(headers)
        
        # Auto-detect content type
        if 'Content-Type' not in self._headers:
            content_type, _ = mimetypes.guess_type(filename)
            if content_type:
                self._headers['Content-Type'] = content_type
        
        # Set disposition header
        self._headers['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    
    def get_directory(self) -> str:
        """Get the directory path."""
        return self._directory
    
    def get_filename(self) -> str:
        """Get the filename."""
        return self._filename
    
    def prepare(self) -> FlaskResponse:
        """Prepare the Flask response object."""
        file_path = os.path.join(self._directory, self._filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.commonpath([os.path.abspath(self._directory), os.path.abspath(file_path)]).startswith(os.path.abspath(self._directory)):
            raise ValueError("File is outside the allowed directory")
        
        # Use Flask's send_from_directory for security
        response = send_from_directory(
            self._directory,
            self._filename,
            as_attachment=(self._disposition == 'attachment')
        )
        
        return self._apply_headers_and_cookies(response)
    
    def send(self) -> FlaskResponse:
        """Send the response."""
        return self.prepare()
    
    @staticmethod
    def create(directory: str, filename: str, headers: Optional[Dict] = None, disposition: str = 'inline'):
        """Create a new DirectoryResponse instance."""
        return DirectoryResponse(directory, filename, headers, disposition)


# Laravel compatibility aliases
BinaryFileResponse = FileResponse  # Laravel Symfony equivalent