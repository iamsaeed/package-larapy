"""Make seeder command"""

import os
from typing import Optional
from ...console.command import Command


class MakeSeederCommand(Command):
    """Create a new database seeder"""
    
    name = "make:seeder"
    description = "Create a new database seeder"

    def handle(self):
        """Execute the command"""
        # Get seeder name from arguments
        seeder_name = self.argument('name')
        if not seeder_name:
            seeder_name = self.ask("What should the seeder be named?")
        
        if not seeder_name:
            self.error("Seeder name is required.")
            return

        # Create seeder file
        self._create_seeder_file(seeder_name)

    def _create_seeder_file(self, seeder_name: str):
        """Create the seeder file"""
        # Ensure seeder name ends with 'Seeder'
        if not seeder_name.endswith('Seeder'):
            seeder_name += 'Seeder'

        # Create seeders directory if it doesn't exist
        seeders_dir = "database/seeders"
        os.makedirs(seeders_dir, exist_ok=True)

        # Create seeder file path
        seeder_file = os.path.join(seeders_dir, f"{seeder_name}.py")

        # Check if file already exists
        if os.path.exists(seeder_file):
            self.error(f"Seeder {seeder_name} already exists.")
            return

        # Generate seeder content
        content = self._get_seeder_stub(seeder_name)

        # Write seeder file
        with open(seeder_file, 'w') as f:
            f.write(content)

        self.info(f"Seeder {seeder_name} created successfully.")

    def _get_seeder_stub(self, seeder_name: str) -> str:
        """Get the seeder stub content"""
        model_name = seeder_name.replace('Seeder', '') if seeder_name.endswith('Seeder') else seeder_name
        
        return f'''"""Database seeder for {model_name}"""

from ..seeder.seeder import Seeder


class {seeder_name}(Seeder):
    """Seeder for {model_name} data"""

    def run(self):
        """Run the database seeds"""
        # Implement your seeding logic here
        # Example:
        
        # Using model factory
        # from database.factories.{model_name}Factory import {model_name}Factory
        # {model_name}Factory().count(10).create()
        
        # Or direct model creation
        # from app.Models.{model_name} import {model_name}
        # {model_name}.create([
        #     {{'name': 'Example 1'}},
        #     {{'name': 'Example 2'}},
        # ])
        
        pass
'''

    def get_arguments(self):
        """Get command arguments"""
        return [
            ('name', 'The name of the seeder')
        ]