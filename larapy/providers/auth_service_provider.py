"""
AuthServiceProvider - Registers authentication services in the container

Bootstraps the authentication system by registering the AuthManager
and related services in the application's service container.
"""

from ..support.service_provider import ServiceProvider
from ..auth.auth_manager import AuthManager


class AuthServiceProvider(ServiceProvider):
    """
    Service provider for authentication services.
    
    Registers the AuthManager and sets up authentication-related
    bindings in the application container.
    """
    
    def register(self):
        """
        Register authentication services in the container.
        """
        self.app.singleton('auth', lambda app: AuthManager(app))
        
        # Register auth manager with different binding names for flexibility
        self.app.bind('auth.manager', lambda app: app.resolve('auth'))
        self.app.bind('AuthManager', lambda app: app.resolve('auth'))
        
    def boot(self):
        """
        Bootstrap authentication services.
        
        This method is called after all service providers have been registered.
        Use this to perform any additional setup that requires other services.
        """
        # Get the auth manager
        auth = self.app.resolve('auth')
        
        # Set up default configuration if available
        if hasattr(self.app, 'config'):
            config = self.app.config
            
            # Configure session settings for authentication
            if hasattr(self.app, 'flask_app'):
                flask_app = self.app.flask_app
                
                # Set session configuration
                flask_app.config.update({
                    'SESSION_COOKIE_SECURE': config.get('session.secure', False),
                    'SESSION_COOKIE_HTTPONLY': config.get('session.http_only', True),
                    'SESSION_COOKIE_SAMESITE': config.get('session.same_site', 'Lax'),
                    'PERMANENT_SESSION_LIFETIME': config.get('session.lifetime', 120 * 60),  # 2 hours
                })
                
                # Set secret key if not already set
                if not flask_app.secret_key:
                    secret_key = config.get('app.key', 'dev-secret-key-change-in-production')
                    flask_app.secret_key = secret_key
        
        # Auto-detect and set User model if it exists
        self._auto_detect_user_model(auth)
    
    def _auto_detect_user_model(self, auth):
        """
        Auto-detect and set the User model for authentication.
        
        Args:
            auth: AuthManager instance
        """
        try:
            # Try to import common User model locations
            user_model = None
            
            # Try different common locations for User model
            model_paths = [
                'app.models.user.User',
                'models.user.User', 
                'app.User',
                'models.User',
            ]
            
            for model_path in model_paths:
                try:
                    module_path, class_name = model_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    user_model = getattr(module, class_name, None)
                    if user_model:
                        break
                except (ImportError, AttributeError):
                    continue
            
            # Set the user model if found
            if user_model:
                auth.set_user_model(user_model)
                
        except Exception:
            # If auto-detection fails, that's okay
            # The user can manually set the model later
            pass
    
    @property
    def provides(self):
        """
        Get the services provided by this provider.
        
        Returns:
            list: List of service names provided
        """
        return ['auth', 'auth.manager', 'AuthManager']
    
    def when(self):
        """
        Define when this provider should be loaded.
        
        Returns:
            list: List of services that trigger loading this provider
        """
        return ['auth']