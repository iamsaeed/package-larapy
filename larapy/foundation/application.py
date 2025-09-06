import os
from flask import Flask
from ..container.container import Container
from ..support.service_provider import ServiceProvider
from typing import List, Dict, Any

class Application(Container):
    """The Application class - Laravel's Application equivalent"""
    
    VERSION = '1.0.0'
    
    def __init__(self, base_path: str = None):
        super().__init__()
        
        # Set up base path
        self._base_path = base_path or os.getcwd()
        
        # Flask application instance
        self._flask_app = Flask(__name__)
        
        # Service providers
        self._service_providers: List[ServiceProvider] = []
        self._loaded_providers: Dict[str, ServiceProvider] = {}
        
        # Booted status
        self._booted = False
        
        # Register base bindings
        self._register_base_bindings()
        
        # Register base service providers
        self._register_base_service_providers()
    
    def _register_base_bindings(self):
        """Register the basic bindings into the container"""
        self.instance('app', self)
        self.instance('Application', self)
        self.instance('Container', self)
        self.instance('flask_app', self._flask_app)
    
    def _register_base_service_providers(self):
        """Register all of the base service providers"""
        from ..providers.routing_service_provider import RoutingServiceProvider
        from ..providers.config_service_provider import ConfigServiceProvider
        from ..providers.auth_service_provider import AuthServiceProvider
        
        self.register(ConfigServiceProvider(self))
        self.register(RoutingServiceProvider(self))
        self.register(AuthServiceProvider(self))
    
    def register(self, provider: ServiceProvider):
        """Register a service provider"""
        if isinstance(provider, str):
            # Import and instantiate if it's a string
            module_path, class_name = provider.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            provider_class = getattr(module, class_name)
            provider = provider_class(self)
        
        # Register the provider
        provider.register()
        
        # Mark provider as loaded
        provider_name = provider.__class__.__name__
        self._loaded_providers[provider_name] = provider
        self._service_providers.append(provider)
        
        # If application already booted, boot the provider
        if self._booted:
            self._boot_provider(provider)
        
        return provider
    
    def boot(self):
        """Boot the application's service providers"""
        if self._booted:
            return
        
        # Boot all providers
        for provider in self._service_providers:
            self._boot_provider(provider)
        
        self._booted = True
    
    def _boot_provider(self, provider: ServiceProvider):
        """Boot the given service provider"""
        if hasattr(provider, 'boot'):
            self.call(provider.boot)
    
    def call(self, callback, parameters: Dict = None):
        """Call the given Closure / class@method and inject its dependencies"""
        return self.resolve_method_dependencies(callback, parameters or {})
    
    def resolve_method_dependencies(self, callback, parameters: Dict):
        """Resolve method dependencies"""
        if callable(callback):
            try:
                import inspect
                sig = inspect.signature(callback)
                resolved_params = {}
                
                for param_name, param in sig.parameters.items():
                    if param_name in parameters:
                        resolved_params[param_name] = parameters[param_name]
                    elif param.annotation != inspect.Parameter.empty:
                        # Try to resolve from container
                        try:
                            if hasattr(param.annotation, '__name__'):
                                dependency = self.resolve(param.annotation.__name__)
                            else:
                                dependency = self.resolve(str(param.annotation))
                            resolved_params[param_name] = dependency
                        except:
                            if param.default != inspect.Parameter.empty:
                                resolved_params[param_name] = param.default
                
                return callback(**resolved_params)
            except Exception as e:
                print(f"Failed to resolve method dependencies: {e}")
                return callback()
        
        return callback
    
    @property
    def flask_app(self) -> Flask:
        """Get the Flask application instance"""
        return self._flask_app
    
    def base_path(self, path: str = '') -> str:
        """Get the base path of the Laravel installation"""
        return os.path.join(self._base_path, path)
    
    def config_path(self, path: str = '') -> str:
        """Get the path to the configuration cache file"""
        return self.base_path(f'config/{path}')
    
    def public_path(self, path: str = '') -> str:
        """Get the path to the public / web directory"""
        return self.base_path(f'public/{path}')
    
    def storage_path(self, path: str = '') -> str:
        """Get the path to the storage directory"""
        return self.base_path(f'storage/{path}')
    
    def database_path(self, path: str = '') -> str:
        """Get the path to the database directory"""
        return self.base_path(f'database/{path}')
    
    def resource_path(self, path: str = '') -> str:
        """Get the path to the resources directory"""
        return self.base_path(f'resources/{path}')
    
    def environment(self) -> str:
        """Get the current application environment"""
        return os.getenv('APP_ENV', 'production')
    
    def is_production(self) -> bool:
        """Determine if the application is in the production environment"""
        return self.environment() == 'production'
    
    def is_local(self) -> bool:
        """Determine if the application is in the local environment"""
        return self.environment() == 'local'
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = None):
        """Run the Flask application"""
        if debug is None:
            debug = not self.is_production()
        
        # Boot the application
        self.boot()
        
        # Run Flask app
        self._flask_app.run(host=host, port=port, debug=debug)
