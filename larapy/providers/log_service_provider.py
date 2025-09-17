"""Log service provider for registering logging and error handling services"""

from ..support.service_provider import ServiceProvider
from ..logging.logger import LarapyLogger
from ..foundation.exceptions.handler import ExceptionHandler

class LogServiceProvider(ServiceProvider):
    """Register logging and error handling services"""

    def register(self):
        """Register services"""
        # Register logger
        self.app.singleton('log', lambda app: LarapyLogger(app))

        # Register exception handler
        self.app.singleton('exception.handler',
                          lambda app: ExceptionHandler(app))

    def boot(self):
        """Boot services"""
        # Initialize exception handler to register error handlers
        self.app.resolve('exception.handler')