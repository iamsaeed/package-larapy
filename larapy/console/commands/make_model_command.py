"""Make model console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeModelCommand(Command):
    """Create a new Eloquent model"""
    
    signature = "make:model {name : The name of the model} {--migration : Create a new migration file for the model} {--factory : Create a new factory for the model} {--seeder : Create a new seeder for the model}"
    description = "Create a new Eloquent model class"

    def handle(self) -> int:
        """Execute the make:model command"""
        
        # Get model name from arguments
        model_name = self.argument('name')
        if not model_name:
            model_name = self.ask("What should the model be named?")
        
        if not model_name:
            self.error("Model name is required.")
            return 1

        # Clean model name (capitalize and remove Model suffix if present)
        model_name = self._clean_model_name(model_name)

        # Check options
        create_migration = self.option('migration')
        create_factory = self.option('factory')
        create_seeder = self.option('seeder')

        try:
            # Create the model file
            self._create_model_file(model_name)
            
            # Create migration if requested
            if create_migration:
                self._create_migration(model_name)
            
            # Create factory if requested
            if create_factory:
                self._create_factory(model_name)
            
            # Create seeder if requested
            if create_seeder:
                self._create_seeder(model_name)
            
            return 0
            
        except Exception as e:
            self.error(f"Failed to create model: {str(e)}")
            return 1

    def _clean_model_name(self, name: str) -> str:
        """Clean and format model name"""
        # Remove Model suffix if present
        if name.endswith('Model'):
            name = name[:-5]
        
        # Capitalize first letter
        return name.capitalize()

    def _create_model_file(self, model_name: str):
        """Create the model file"""
        # Create Models directory if it doesn't exist
        models_dir = "app/Models"
        os.makedirs(models_dir, exist_ok=True)

        # Create model file path
        model_file = os.path.join(models_dir, f"{model_name}.py")

        # Check if file already exists
        if os.path.exists(model_file):
            self.error(f"Model {model_name} already exists.")
            return

        # Generate model content
        content = self._get_model_stub(model_name)

        # Write model file
        with open(model_file, 'w') as f:
            f.write(content)

        self.success(f"Model {model_name} created successfully.")
        self.info(f"File: {model_file}")

    def _get_model_stub(self, model_name: str) -> str:
        """Get the model stub content"""
        table_name = self._get_table_name(model_name)
        
        return f'''"""{model_name} model"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'package-larapy'))

from larapy.database.eloquent.model import Model
from datetime import datetime


class {model_name}(Model):
    """{model_name} model"""
    
    # Table name
    table = '{table_name}'
    
    # Primary key
    primary_key = 'id'
    
    # Enable timestamps
    timestamps = True
    
    # Mass assignable attributes
    fillable = [
        # Add your fillable fields here
        # Example: 'name', 'email', 'description'
    ]
    
    # Hidden attributes (for serialization)
    hidden = [
        # Add hidden fields here
        # Example: 'password', 'remember_token'
    ]
    
    # Attribute casting
    casts = {{
        # Add attribute casts here
        # Example: 'is_active': 'boolean', 'settings': 'json'
    }}
    
    # Date attributes
    dates = [
        # Add date fields here
        # Example: 'published_at', 'deleted_at'
    ]
    
    def __init__(self, attributes=None):
        super().__init__(attributes)
    
    # Define your relationships here
    # Example:
    # def user(self):
    #     \"\"\"Belongs to a user\"\"\"
    #     return self.belongs_to('User', 'user_id', 'id')
    
    # def posts(self):
    #     \"\"\"Has many posts\"\"\"
    #     return self.has_many('Post', '{model_name.lower()}_id', 'id')
    
    # Define your model methods here
    # Example:
    # def is_active(self) -> bool:
    #     \"\"\"Check if the {model_name.lower()} is active\"\"\"
    #     return self.get_attribute('is_active', False)
    
    # def get_full_name(self) -> str:
    #     \"\"\"Get the full name\"\"\"
    #     return f"{{self.first_name}} {{self.last_name}}"
'''

    def _get_table_name(self, model_name: str) -> str:
        """Convert model name to table name (plural, snake_case)"""
        # Simple pluralization (add 's' for most cases)
        # In a more complete implementation, you'd use proper pluralization rules
        table_name = model_name.lower()
        
        # Handle some common irregular plurals
        if table_name.endswith('y'):
            table_name = table_name[:-1] + 'ies'
        elif table_name.endswith(('s', 'x', 'z', 'ch', 'sh')):
            table_name = table_name + 'es'
        else:
            table_name = table_name + 's'
        
        return table_name

    def _create_migration(self, model_name: str):
        """Create migration for the model"""
        try:
            # Import and use the existing make:migration command
            from ...database.console.make_migration_command import MakeMigrationCommand
            
            migration_command = MakeMigrationCommand()
            table_name = self._get_table_name(model_name)
            migration_name = f"create_{table_name}_table"
            
            # Set arguments for migration command
            migration_command._args = [migration_name]
            
            # Create the migration
            result = migration_command.handle()
            
            if result == 0:
                self.info(f"Migration for {model_name} created successfully.")
            else:
                self.error(f"Failed to create migration for {model_name}.")
                
        except Exception as e:
            self.error(f"Could not create migration: {str(e)}")

    def _create_factory(self, model_name: str):
        """Create factory for the model"""
        try:
            # Import and use the existing make:factory command
            from ...database.console.make_factory_command import MakeFactoryCommand
            
            factory_command = MakeFactoryCommand()
            factory_name = f"{model_name}Factory"
            
            # Set arguments for factory command
            factory_command._args = [factory_name]
            
            # Create the factory
            factory_command.handle()
            self.info(f"Factory for {model_name} created successfully.")
            
        except Exception as e:
            self.error(f"Could not create factory: {str(e)}")

    def _create_seeder(self, model_name: str):
        """Create seeder for the model"""
        try:
            # Import and use the existing make:seeder command
            from ...database.console.make_seeder_command import MakeSeederCommand
            
            seeder_command = MakeSeederCommand()
            seeder_name = f"{model_name}Seeder"
            
            # Set arguments for seeder command
            seeder_command._args = [seeder_name]
            
            # Create the seeder
            seeder_command.handle()
            self.info(f"Seeder for {model_name} created successfully.")
            
        except Exception as e:
            self.error(f"Could not create seeder: {str(e)}")