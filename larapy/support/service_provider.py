from abc import ABC, abstractmethod
from typing import List, Dict

class ServiceProvider(ABC):
    """Base Service Provider class"""
    
    def __init__(self, app):
        self.app = app
    
    @abstractmethod
    def register(self):
        """Register services in the container"""
        pass
    
    def boot(self):
        """Bootstrap services"""
        pass
    
    def provides(self) -> List[str]:
        """Get the services provided by the provider"""
        return []
    
    def when(self) -> List[str]:
        """Get the events that trigger this service provider"""
        return []
    
    def is_deferred(self) -> bool:
        """Determine if the provider is deferred"""
        return len(self.provides()) > 0
