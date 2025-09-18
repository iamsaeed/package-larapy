"""Make migration console command"""

import os
from larapy.console.command import Command
from ..migrations.creator import MigrationCreator


class MakeMigrationCommand(Command):
    """
    Create a new migration file
    """

    signature = "make:migration {name : The name of the migration} {--create= : The table to be created} {--table= : The table to migrate}"
    description = "Create a new database migration"

    def handle(self) -> int:
        """Execute the make:migration command"""
        
        name = self.argument('name')
        if not name:
            self.error("Migration name is required")
            return 1
            
        table = self.option('table')
        create = self.option('create')
        
        # Determine if this is a create table migration
        is_create = bool(create)
        table_name = create or table
        
        # Get migration path
        migration_path = self._get_migration_path()
        
        # Create migration creator
        creator = MigrationCreator()
        
        try:
            # Create the migration file
            file_path = creator.create(name, migration_path, table_name, is_create)
            
            self.success(f"Migration created: {os.path.basename(file_path)}")
            self.info(f"File: {file_path}")
            
            return 0
            
        except Exception as e:
            self.error(f"Failed to create migration: {str(e)}")
            return 1

    def _get_migration_path(self) -> str:
        """Get the migration directory path"""
        # Default migration path
        if hasattr(self.app, 'base_path'):
            base_path = self.app.base_path('database/migrations')
        else:
            # Fallback for simplified structure
            base_path = os.path.join(os.getcwd(), 'database', 'migrations')
            
        return base_path