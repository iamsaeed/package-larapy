"""Migration file creator"""

import os
from datetime import datetime
from typing import Optional


class MigrationCreator:
    """
    Migration file creator
    
    Creates new migration files with the proper structure.
    """

    def __init__(self, filesystem=None):
        self.filesystem = filesystem

    def create(self, name: str, path: str, table: Optional[str] = None, create: bool = False) -> str:
        """Create a new migration file"""
        # Generate migration file name with timestamp
        timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
        filename = f"{timestamp}_{name}.py"
        full_path = os.path.join(path, filename)

        # Ensure directory exists
        os.makedirs(path, exist_ok=True)

        # Generate migration content
        content = self._get_stub(name, table, create)

        # Write the file
        with open(full_path, 'w') as f:
            f.write(content)

        return full_path

    def _get_stub(self, name: str, table: Optional[str] = None, create: bool = False) -> str:
        """Get the migration stub content"""
        class_name = self._get_class_name(name)

        if create and table:
            return self._get_create_table_stub(class_name, table)
        elif table:
            return self._get_update_table_stub(class_name, table)
        else:
            return self._get_blank_stub(class_name)

    def _get_class_name(self, name: str) -> str:
        """Convert migration name to class name"""
        # Convert snake_case to PascalCase
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)

    def _get_create_table_stub(self, class_name: str, table: str) -> str:
        """Get stub for creating a table"""
        return f'''"""Create {table} table migration"""

from larapy.database.migrations.migration import Migration
from larapy.database.schema.blueprint import Blueprint


class {class_name}(Migration):
    """Create {table} table migration"""

    def up(self):
        """Run the migrations"""
        def create_table(table):
            table.id()
            table.timestamps()

        self.schema.create('{table}', create_table)

    def down(self):
        """Reverse the migrations"""
        self.schema.drop_if_exists('{table}')
'''

    def _get_update_table_stub(self, class_name: str, table: str) -> str:
        """Get stub for updating a table"""
        return f'''"""Update {table} table migration"""

from larapy.database.migrations.migration import Migration
from larapy.database.schema.blueprint import Blueprint


class {class_name}(Migration):
    """Update {table} table migration"""

    def up(self):
        """Run the migrations"""
        def update_table(table):
            # Add your columns here
            pass

        self.schema.table('{table}', update_table)

    def down(self):
        """Reverse the migrations"""
        def revert_table(table):
            # Reverse your changes here
            pass

        self.schema.table('{table}', revert_table)
'''

    def _get_blank_stub(self, class_name: str) -> str:
        """Get blank migration stub"""
        return f'''"""Migration: {class_name}"""

from larapy.database.migrations.migration import Migration


class {class_name}(Migration):
    """Migration: {class_name}"""

    def up(self):
        """Run the migrations"""
        pass

    def down(self):
        """Reverse the migrations"""
        pass
'''