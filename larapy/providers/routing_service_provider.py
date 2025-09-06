from ..support.service_provider import ServiceProvider
from ..routing.router import Router

class RoutingServiceProvider(ServiceProvider):
    """Routing Service Provider"""
    
    def register(self):
        """Register the router"""
        self.app.singleton('router', lambda app: Router(app))
    
    def boot(self):
        """Boot the routing services"""
        # Set up route model binding, etc.
        pass
