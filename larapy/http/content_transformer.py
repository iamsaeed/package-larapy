"""Content transformation utilities for responses."""

import json
from typing import Any, Dict, Optional, Union
from ..contracts import Jsonable, Arrayable, Renderable


class ContentTransformer:
    """Transforms content for appropriate response types."""
    
    @staticmethod
    def transform_to_json(content: Any) -> str:
        """Transform content to JSON string."""
        # Handle Jsonable objects
        if isinstance(content, Jsonable):
            return content.to_json()
        
        # Handle Arrayable objects
        if isinstance(content, Arrayable):
            return json.dumps(content.to_array(), ensure_ascii=False, default=ContentTransformer._json_serialize_default)
        
        # Handle objects with to_json method
        if hasattr(content, 'to_json') and callable(getattr(content, 'to_json')):
            return content.to_json()
        
        # Handle objects with to_array method
        if hasattr(content, 'to_array') and callable(getattr(content, 'to_array')):
            return json.dumps(content.to_array(), ensure_ascii=False, default=ContentTransformer._json_serialize_default)
        
        # Handle objects with to_dict method
        if hasattr(content, 'to_dict') and callable(getattr(content, 'to_dict')):
            return json.dumps(content.to_dict(), ensure_ascii=False, default=ContentTransformer._json_serialize_default)
        
        # Handle objects with __dict__ (like model instances)
        if hasattr(content, '__dict__') and not isinstance(content, (dict, list, str, int, float, bool, type(None))):
            # Filter out private attributes and methods
            data = {k: v for k, v in content.__dict__.items() if not k.startswith('_') and not callable(v)}
            return json.dumps(data, ensure_ascii=False, default=ContentTransformer._json_serialize_default)
        
        # Handle regular Python objects
        return json.dumps(content, ensure_ascii=False, default=ContentTransformer._json_serialize_default)
    
    @staticmethod
    def transform_to_array(content: Any) -> Union[Dict, list]:
        """Transform content to array/dict."""
        # Handle Arrayable objects
        if isinstance(content, Arrayable):
            return content.to_array()
        
        # Handle objects with to_array method
        if hasattr(content, 'to_array') and callable(getattr(content, 'to_array')):
            return content.to_array()
        
        # Handle objects with to_dict method
        if hasattr(content, 'to_dict') and callable(getattr(content, 'to_dict')):
            return content.to_dict()
        
        # Handle objects with __dict__
        if hasattr(content, '__dict__') and not isinstance(content, (dict, list, str, int, float, bool, type(None))):
            return {k: v for k, v in content.__dict__.items() if not k.startswith('_') and not callable(v)}
        
        # Handle regular dict/list
        if isinstance(content, (dict, list)):
            return content
        
        # Fallback - wrap in dict
        return {'data': content}
    
    @staticmethod
    def transform_to_string(content: Any) -> str:
        """Transform content to string."""
        # Handle Renderable objects
        if isinstance(content, Renderable):
            return content.render()
        
        # Handle objects with render method
        if hasattr(content, 'render') and callable(getattr(content, 'render')):
            return content.render()
        
        # Handle objects with __str__ method
        if hasattr(content, '__str__'):
            return str(content)
        
        # Fallback
        return repr(content)
    
    @staticmethod
    def _json_serialize_default(obj):
        """Default JSON serializer for non-serializable objects."""
        # Handle datetime objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        
        # Handle objects with to_dict method
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
        
        # Handle objects with to_array method
        if hasattr(obj, 'to_array') and callable(getattr(obj, 'to_array')):
            return obj.to_array()
        
        # Handle objects with __dict__
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_') and not callable(v)}
        
        # Fallback to string representation
        return str(obj)
    
    @staticmethod
    def should_be_json(content: Any, request=None) -> bool:
        """Determine if content should be JSON response."""
        # Check content type
        if isinstance(content, (dict, list)):
            return True
        
        # Check if object implements Jsonable or Arrayable
        if isinstance(content, (Jsonable, Arrayable)):
            return True
        
        # Check if object has JSON methods
        if hasattr(content, 'to_json') or hasattr(content, 'to_array'):
            return True
        
        # Check request for JSON expectation
        if request:
            # Check Accept header
            if hasattr(request, 'headers') and 'application/json' in request.headers.get('Accept', ''):
                return True
            
            # Check if it's an AJAX request
            if hasattr(request, 'is_xhr') and request.is_xhr:
                return True
            
            # Check if request content type is JSON
            if hasattr(request, 'is_json') and request.is_json:
                return True
        
        return False
    
    @staticmethod
    def is_view_response(content: Any) -> bool:
        """Check if content represents a view response."""
        # Check if it's a Renderable object
        if isinstance(content, Renderable):
            return True
        
        # Check if object has render method
        if hasattr(content, 'render') and callable(getattr(content, 'render')):
            return True
        
        return False


class LarapyJsonable:
    """Mixin class to make objects JSON serializable."""
    
    def to_json(self, options: int = 0) -> str:
        """Convert object to JSON string."""
        return ContentTransformer.transform_to_json(self.to_array())
    
    def to_array(self) -> Dict:
        """Convert object to array/dict. Override this method."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and not callable(v)}


class LarapyArrayable:
    """Mixin class to make objects array serializable."""
    
    def to_array(self) -> Union[Dict, list]:
        """Convert object to array/dict. Override this method."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and not callable(v)}


class LarapyRenderable:
    """Mixin class to make objects renderable."""
    
    def render(self) -> str:
        """Render object to string. Override this method."""
        return str(self)