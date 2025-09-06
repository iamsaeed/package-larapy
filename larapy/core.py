"""
Core application class for Larapy.
"""

from typing import Dict, Any, Optional


class LarapyApp:
    """
    Main application class that provides Laravel-like functionality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Larapy application.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._services = {}
        self._initialized = False
    
    def configure(self, config: Dict[str, Any]) -> 'LarapyApp':
        """
        Configure the application with the given settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Self for method chaining
        """
        self._config.update(config)
        return self
    
    def register_service(self, name: str, service: Any) -> 'LarapyApp':
        """
        Register a service with the application.
        
        Args:
            name: Service name
            service: Service instance or factory
            
        Returns:
            Self for method chaining
        """
        self._services[name] = service
        return self
    
    def get_service(self, name: str) -> Any:
        """
        Get a registered service.
        
        Args:
            name: Service name
            
        Returns:
            The requested service
            
        Raises:
            KeyError: If service is not found
        """
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found")
        return self._services[name]
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def initialize(self) -> 'LarapyApp':
        """
        Initialize the application.
        
        Returns:
            Self for method chaining
        """
        if not self._initialized:
            # Perform initialization logic here
            self._initialized = True
        return self
    
    @property
    def is_initialized(self) -> bool:
        """Check if the application is initialized."""
        return self._initialized
