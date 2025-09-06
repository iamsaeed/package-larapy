from ..support.service_provider import ServiceProvider
from ..config.repository import Repository

class ConfigServiceProvider(ServiceProvider):
    """Configuration Service Provider"""
    
    def register(self):
        """Register the configuration repository"""
        config_path = self.app.base_path('config')
        self.app.singleton('config', lambda app: Repository(config_path))
