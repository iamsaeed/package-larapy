"""Make factory command"""

import os
from typing import Optional
from ...console.command import Command


class MakeFactoryCommand(Command):
    """Create a new model factory"""
    
    name = "make:factory"
    description = "Create a new model factory"

    def handle(self):
        """Execute the command"""
        # Get factory name from arguments
        factory_name = self.argument('name')
        if not factory_name:
            factory_name = self.ask("What should the factory be named?")
        
        if not factory_name:
            self.error("Factory name is required.")
            return

        # Get model name (optional)
        model_name = self.option('model')
        if not model_name:
            # Try to guess model name from factory name
            if factory_name.endswith('Factory'):
                model_name = factory_name[:-7]  # Remove 'Factory' suffix
            else:
                model_name = factory_name

        # Create factory file
        self._create_factory_file(factory_name, model_name)

    def _create_factory_file(self, factory_name: str, model_name: str):
        """Create the factory file"""
        # Ensure factory name ends with 'Factory'
        if not factory_name.endswith('Factory'):
            factory_name += 'Factory'

        # Create factories directory if it doesn't exist
        factories_dir = "database/factories"
        os.makedirs(factories_dir, exist_ok=True)

        # Create factory file path
        factory_file = os.path.join(factories_dir, f"{factory_name}.py")

        # Check if file already exists
        if os.path.exists(factory_file):
            self.error(f"Factory {factory_name} already exists.")
            return

        # Generate factory content
        content = self._get_factory_stub(factory_name, model_name)

        # Write factory file
        with open(factory_file, 'w') as f:
            f.write(content)

        self.info(f"Factory {factory_name} created successfully.")

    def _get_factory_stub(self, factory_name: str, model_name: str) -> str:
        """Get the factory stub content"""
        return f'''"""Factory for {model_name} model"""

from ..factory.factory import Factory
from app.Models.{model_name} import {model_name}


class {factory_name}(Factory):
    """Factory for {model_name} model"""
    
    model = {model_name}

    def definition(self) -> dict:
        """Define the model's default state"""
        return {{
            # Define factory attributes here
            # Example:
            # 'name': self.faker.name(),
            # 'email': self.faker.unique().email(),
            # 'created_at': self.faker.date_time(),
        }}

    def configure(self):
        """Configure the model factory"""
        return self

    # Define factory states
    def active(self):
        """Factory state for active {model_name.lower()}s"""
        return self.state({{
            'active': True,
        }})

    def inactive(self):
        """Factory state for inactive {model_name.lower()}s"""
        return self.state({{
            'active': False,
        }})
'''

    def get_arguments(self):
        """Get command arguments"""
        return [
            ('name', 'The name of the factory')
        ]

    def get_options(self):
        """Get command options"""
        return [
            ('model', 'm', 'The name of the model')
        ]