"""Response contracts and interfaces for Laravel-style responses."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class Jsonable(ABC):
    """Interface for objects that can be converted to JSON."""
    
    @abstractmethod
    def to_json(self, options: int = 0) -> str:
        """Convert the object to JSON."""
        pass


class Arrayable(ABC):
    """Interface for objects that can be converted to array/dict."""
    
    @abstractmethod
    def to_array(self) -> Union[Dict, list]:
        """Convert the object to array/dict."""
        pass


class Renderable(ABC):
    """Interface for objects that can be rendered to string."""
    
    @abstractmethod
    def render(self) -> str:
        """Render the object to string."""
        pass


class ResponseFactory(ABC):
    """Interface for response factory."""
    
    @abstractmethod
    def make(self, content: str = '', status: int = 200, headers: Optional[Dict] = None):
        """Create a basic response."""
        pass
    
    @abstractmethod
    def json(self, data: Any = None, status: int = 200, headers: Optional[Dict] = None, options: int = 0):
        """Create a JSON response."""
        pass
    
    @abstractmethod
    def view(self, view: str, data: Optional[Dict] = None, status: int = 200, headers: Optional[Dict] = None):
        """Create a view response."""
        pass
    
    @abstractmethod
    def redirect_to(self, path: str, status: int = 302, headers: Optional[Dict] = None, secure: Optional[bool] = None):
        """Create a redirect response."""
        pass
    
    @abstractmethod
    def download(self, file_path: str, name: Optional[str] = None, headers: Optional[Dict] = None, disposition: str = 'attachment'):
        """Create a file download response."""
        pass
    
    @abstractmethod
    def stream(self, callback, status: int = 200, headers: Optional[Dict] = None):
        """Create a streamed response."""
        pass


class Macroable:
    """Trait to add macro functionality to classes."""
    
    _macros = {}
    
    @classmethod
    def macro(cls, name: str, func):
        """Register a macro."""
        cls._macros[name] = func
    
    @classmethod
    def has_macro(cls, name: str) -> bool:
        """Check if a macro exists."""
        return name in cls._macros
    
    def __getattr__(self, name: str):
        """Handle macro method calls."""
        if name in self._macros:
            return lambda *args, **kwargs: self._macros[name](self, *args, **kwargs)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")