"""Config show console command"""

import os
import importlib.util
from typing import Optional, Any, Dict
from ...console.command import Command


class ConfigShowCommand(Command):
    """Display configuration values"""
    
    signature = "config:show {key? : The configuration key to display (optional)}"
    description = "Display application configuration values"

    def handle(self) -> int:
        """Execute the config:show command"""
        
        try:
            # Get the configuration key if provided
            config_key = self.argument('key')
            
            # Load configuration
            config_data = self._load_configuration()
            
            if config_key:
                # Show specific configuration key
                self._show_specific_config(config_data, config_key)
            else:
                # Show all configuration
                self._show_all_config(config_data)
            
            return 0
            
        except Exception as e:
            self.error(f"Failed to display configuration: {str(e)}")
            return 1

    def _load_configuration(self) -> Dict[str, Any]:
        """Load all configuration from config files"""
        config_data = {}
        config_dir = "config"
        
        if not os.path.exists(config_dir):
            self.error("Config directory not found.")
            return {}
        
        # Load all Python config files
        for filename in os.listdir(config_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                config_name = filename[:-3]  # Remove .py extension
                config_path = os.path.join(config_dir, filename)
                
                try:
                    # Load the config module
                    spec = importlib.util.spec_from_file_location(config_name, config_path)
                    config_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(config_module)
                    
                    # Extract configuration values (uppercase attributes)
                    module_config = {}
                    for attr_name in dir(config_module):
                        if not attr_name.startswith('_'):
                            attr_value = getattr(config_module, attr_name)
                            # Only include serializable values
                            if self._is_serializable(attr_value):
                                module_config[attr_name.lower()] = attr_value
                    
                    config_data[config_name] = module_config
                    
                except Exception as e:
                    self.comment(f"Could not load config file {filename}: {str(e)}")
        
        return config_data

    def _is_serializable(self, value: Any) -> bool:
        """Check if a value is serializable for display"""
        try:
            # Test basic types
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                return True
            # Skip functions, classes, modules, etc.
            return False
        except:
            return False

    def _show_specific_config(self, config_data: Dict[str, Any], key: str):
        """Show a specific configuration key"""
        # Parse dot notation (e.g., "database.connections.mysql.host")
        keys = key.split('.')
        
        current_data = config_data
        path = []
        
        for k in keys:
            path.append(k)
            if isinstance(current_data, dict) and k in current_data:
                current_data = current_data[k]
            else:
                self.error(f"Configuration key '{key}' not found.")
                return
        
        # Display the value
        self.line("")
        self.info(f"Configuration: {key}")
        self.line("-" * (len(key) + 15))
        self._display_value(current_data, indent=0)
        self.line("")

    def _show_all_config(self, config_data: Dict[str, Any]):
        """Show all configuration"""
        if not config_data:
            self.info("No configuration found.")
            return
        
        self.line("")
        self.info("Application Configuration:")
        self.line("=" * 50)
        
        for config_file, config_values in sorted(config_data.items()):
            self.line("")
            self.success(f"[{config_file}]")
            self.line("-" * (len(config_file) + 4))
            
            if isinstance(config_values, dict):
                for key, value in sorted(config_values.items()):
                    self.line(f"  {key}:")
                    self._display_value(value, indent=4)
            else:
                self._display_value(config_values, indent=2)
        
        self.line("")

    def _display_value(self, value: Any, indent: int = 0):
        """Display a configuration value with proper formatting"""
        prefix = " " * indent
        
        if value is None:
            self.line(f"{prefix}null")
        elif isinstance(value, bool):
            self.line(f"{prefix}{str(value).lower()}")
        elif isinstance(value, str):
            # Handle sensitive data
            if self._is_sensitive_key(str(value)):
                self.line(f"{prefix}\"***HIDDEN***\"")
            else:
                self.line(f"{prefix}\"{value}\"")
        elif isinstance(value, (int, float)):
            self.line(f"{prefix}{value}")
        elif isinstance(value, list):
            if not value:
                self.line(f"{prefix}[]")
            else:
                self.line(f"{prefix}[")
                for i, item in enumerate(value):
                    comma = "," if i < len(value) - 1 else ""
                    if isinstance(item, str):
                        self.line(f"{prefix}  \"{item}\"{comma}")
                    else:
                        self.line(f"{prefix}  {item}{comma}")
                self.line(f"{prefix}]")
        elif isinstance(value, dict):
            if not value:
                self.line(f"{prefix}{{}}")
            else:
                self.line(f"{prefix}{{")
                items = list(value.items())
                for i, (k, v) in enumerate(items):
                    comma = "," if i < len(items) - 1 else ""
                    self.line(f"{prefix}  \"{k}\": ", end="")
                    if isinstance(v, str):
                        if self._is_sensitive_key(k):
                            print(f"\"***HIDDEN***\"{comma}")
                        else:
                            print(f"\"{v}\"{comma}")
                    elif isinstance(v, (dict, list)):
                        print("")
                        self._display_value(v, indent + 4)
                        if comma:
                            self.line(f"{prefix}  {comma}")
                    else:
                        print(f"{v}{comma}")
                self.line(f"{prefix}}}")
        else:
            self.line(f"{prefix}{str(value)}")

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a configuration key contains sensitive data"""
        sensitive_keywords = [
            'password', 'secret', 'key', 'token', 'api_key',
            'private', 'credential', 'auth', 'cert'
        ]
        
        key_lower = key.lower()
        return any(keyword in key_lower for keyword in sensitive_keywords)

    def line(self, message: str = "", end: str = "\\n"):
        """Print a line with optional ending"""
        print(message, end=end)