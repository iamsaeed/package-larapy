"""
Configuration management for Larapy.
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path


class Config:
    """
    Configuration manager for Larapy applications.
    """
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_data: Optional initial configuration data
        """
        self._data = config_data or {}
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Config':
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Config instance with loaded data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(data)
    
    @classmethod
    def from_env(cls, prefix: str = "LARAPY_") -> 'Config':
        """
        Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables
            
        Returns:
            Config instance with environment data
        """
        data = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Try to parse as JSON, fallback to string
                try:
                    data[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    data[config_key] = value
        
        return cls(data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation like 'app.debug')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        data = self._data
        
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def update(self, config_data: Dict[str, Any]) -> None:
        """
        Update configuration with new data.
        
        Args:
            config_data: Dictionary containing configuration updates
        """
        self._data.update(config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._data.copy()
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            file_path: Path where to save the configuration
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style assignment."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the configuration."""
        return self.get(key) is not None
