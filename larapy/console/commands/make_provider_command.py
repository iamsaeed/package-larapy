"""Make provider console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeProviderCommand(Command):
    """Create a new service provider"""
    
    signature = "make:provider {name : The name of the service provider}"
    description = "Create a new service provider class"

    def handle(self) -> int:
        """Execute the make:provider command"""
        
        # Get provider name from arguments
        provider_name = self.argument('name')
        if not provider_name:
            provider_name = self.ask("What should the service provider be named?")
        
        if not provider_name:
            self.error("Service provider name is required.")
            return 1

        # Clean provider name
        provider_name = self._clean_provider_name(provider_name)

        try:
            # Create the provider file
            self._create_provider_file(provider_name)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create service provider: {str(e)}")
            return 1

    def _clean_provider_name(self, name: str) -> str:
        """Clean and format provider name"""
        # Add ServiceProvider suffix if not present
        if not name.endswith('ServiceProvider') and not name.endswith('Provider'):
            name = name + 'ServiceProvider'
        elif name.endswith('Provider') and not name.endswith('ServiceProvider'):
            name = name[:-8] + 'ServiceProvider'
        
        # Ensure proper capitalization (capitalize each word)
        base_name = name.replace('ServiceProvider', '').replace('Provider', '')
        return ''.join(word.capitalize() for word in base_name.split()) + 'ServiceProvider'

    def _create_provider_file(self, provider_name: str):
        """Create the provider file"""
        # Create Providers directory if it doesn't exist
        providers_dir = "app/Providers"
        os.makedirs(providers_dir, exist_ok=True)

        # Create provider file path
        provider_file = os.path.join(providers_dir, f"{provider_name}.py")

        # Check if file already exists
        if os.path.exists(provider_file):
            self.error(f"Service provider {provider_name} already exists.")
            return

        # Generate provider content
        content = self._get_provider_stub(provider_name)

        # Write provider file
        with open(provider_file, 'w') as f:
            f.write(content)

        self.success(f"Service provider {provider_name} created successfully.")
        self.info(f"File: {provider_file}")
        self.comment("Don't forget to register your service provider in config/app.py")

    def _get_provider_stub(self, provider_name: str) -> str:
        """Get the provider stub content"""
        class_name_without_suffix = provider_name[:-15] if provider_name.endswith('ServiceProvider') else provider_name
        
        return f'''"""
{provider_name}

Service provider for {class_name_without_suffix.lower()} related services and functionality.
"""

from larapy.support.service_provider import ServiceProvider
from typing import List


class {provider_name}(ServiceProvider):
    """
    {provider_name}
    
    This service provider handles the registration and bootstrapping
    of {class_name_without_suffix.lower()} related services.
    """
    
    def register(self):
        """
        Register services in the container
        
        This method is called to register service bindings, singletons,
        and other services in the application's service container.
        """
        # Register your services here
        # Example:
        # self.app.bind('my_service', lambda app: MyService())
        # self.app.singleton('singleton_service', lambda app: SingletonService())
        
        pass
    
    def boot(self):
        """
        Bootstrap services
        
        This method is called after all service providers have been registered.
        Use this method to perform actions that depend on other services being available.
        """
        # Bootstrap your services here
        # Example:
        # - Configure middleware
        # - Set up event listeners
        # - Publish configuration files
        # - Register view composers
        
        pass
    
    def provides(self) -> List[str]:
        """
        Get the services provided by the provider
        
        Returns:
            List of service names that this provider offers
        """
        return [
            # List the services this provider offers
            # Example: 'my_service', 'another_service'
        ]
    
    def when(self) -> List[str]:
        """
        Get the events that trigger this service provider
        
        Returns:
            List of event names that should trigger this provider
        """
        return [
            # List events that should trigger this provider
            # Example: 'user.created', 'order.completed'
        ]
    
    def is_deferred(self) -> bool:
        """
        Determine if the provider is deferred
        
        Deferred providers are only loaded when their services are actually needed.
        
        Returns:
            True if the provider should be deferred, False otherwise
        """
        # Return True if this provider should be loaded on-demand
        # Return False if this provider should be loaded on every request
        return len(self.provides()) > 0
'''