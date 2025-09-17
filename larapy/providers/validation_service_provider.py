"""Validation service provider for registering validation services"""

from ..support.service_provider import ServiceProvider
from ..validation.factory import ValidationFactory


class ValidationServiceProvider(ServiceProvider):
    """Register validation services"""

    def register(self):
        """Register services"""
        # Register the validation factory
        self.app.singleton('validation', lambda app: ValidationFactory())

        # Alias for 'validator' (Laravel compatibility)
        self.app.alias('validation', 'validator')

    def boot(self):
        """Boot services"""
        # Any additional setup when the application boots
        pass