import os
import json
from typing import Any, Dict
from dotenv import load_dotenv

class Repository:
    """Configuration Repository"""
    
    def __init__(self, config_path: str = None):
        self._items: Dict[str, Any] = {}
        self._config_path = config_path or 'config'
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration files
        self._load_configuration_files()
    
    def _load_configuration_files(self):
        """Load all configuration files"""
        if not os.path.exists(self._config_path):
            return
        
        for filename in os.listdir(self._config_path):
            if filename.endswith('.py'):
                module_name = filename[:-3]  # Remove .py extension
                self._load_config_file(module_name)
    
    def _load_config_file(self, name: str):
        """Load a specific configuration file"""
        try:
            import importlib.util
            file_path = os.path.join(self._config_path, f"{name}.py")
            
            spec = importlib.util.spec_from_file_location(name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get all uppercase variables from module
            config = {}
            for attr in dir(module):
                if not attr.startswith('_'):
                    config[attr.lower()] = getattr(module, attr)
            
            self._items[name] = config
            
        except Exception as e:
            print(f"Failed to load config file {name}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        keys = key.split('.')
        
        if len(keys) == 1:
            return self._items.get(keys[0], default)
        
        config_name = keys[0]
        if config_name not in self._items:
            return default
        
        value = self._items[config_name]
        
        for k in keys[1:]:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        keys = key.split('.')
        
        if len(keys) == 1:
            self._items[keys[0]] = value
            return
        
        config_name = keys[0]
        if config_name not in self._items:
            self._items[config_name] = {}
        
        current = self._items[config_name]
        
        for k in keys[1:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def has(self, key: str) -> bool:
        """Determine if the given configuration value exists"""
        try:
            self.get(key)
            return True
        except:
            return False
    
    def all(self) -> Dict[str, Any]:
        """Get all configuration items"""
        return self._items.copy()

# Helper function to get environment variables with type casting
def env(key: str, default: Any = None, cast_type: type = None):
    """Get environment variable with optional type casting"""
    value = os.getenv(key, default)
    
    if cast_type and value is not None:
        if cast_type == bool:
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif cast_type == int:
            return int(value)
        elif cast_type == float:
            return float(value)
    
    return value
