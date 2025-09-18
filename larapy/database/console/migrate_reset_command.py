"""Migration reset command"""

import os
from typing import List, Dict, Any
from ...console.command import Command
from ..migrations.repository import MigrationRepository
from ..migrations.migrator import Migrator


class MigrateResetCommand(Command):
    """Rollback all database migrations"""
    
    name = "migrate:reset"
    description = "Rollback all database migrations"

    def __init__(self, migrator: Migrator, repository: MigrationRepository):
        super().__init__()
        self.migrator = migrator
        self.repository = repository

    def handle(self):
        """Execute the command"""
        if not self.repository.repository_exists():
            self.error("Migration table not found.")
            self.line("")
            self.info("Run 'migrate:install' to create the migration table.")
            return

        # Get all ran migrations
        ran_migrations = self.repository.get_ran()
        
        if not ran_migrations:
            self.info("Nothing to rollback.")
            return

        # Confirm reset
        if not self.confirm("This will rollback all migrations. Do you want to continue?"):
            self.info("Migration reset cancelled.")
            return

        self.info("Rolling back migrations...")
        
        # Get migrations in reverse order (newest first)
        migrations_to_rollback = list(reversed(ran_migrations))
        
        # Rollback each migration
        for migration_name in migrations_to_rollback:
            self._rollback_migration(migration_name)

        self.info("All migrations rolled back successfully.")

    def _rollback_migration(self, migration_name: str):
        """Rollback a single migration"""
        try:
            # Load migration file
            migration_file = self._find_migration_file(migration_name)
            if not migration_file:
                self.error(f"Migration file for '{migration_name}' not found.")
                return

            # Load and execute down method
            migration_class = self._load_migration_class(migration_file)
            migration_instance = migration_class()
            
            self.line(f"Rolling back: {migration_name}")
            
            # Execute down method
            migration_instance.down()
            
            # Remove from repository
            self.repository.delete(migration_name)
            
        except Exception as e:
            self.error(f"Error rolling back migration '{migration_name}': {str(e)}")

    def _find_migration_file(self, migration_name: str) -> str:
        """Find migration file by name"""
        migrations_path = "database/migrations"
        if not os.path.exists(migrations_path):
            return None
        
        for file in os.listdir(migrations_path):
            if file.endswith('.py') and file[:-3] == migration_name:
                return os.path.join(migrations_path, file)
        
        return None

    def _load_migration_class(self, file_path: str):
        """Load migration class from file"""
        import importlib.util
        import sys
        
        spec = importlib.util.spec_from_file_location("migration", file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["migration"] = module
        spec.loader.exec_module(module)
        
        # Find migration class (should be the only class that has up/down methods)
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                hasattr(obj, 'up') and 
                hasattr(obj, 'down') and
                name != 'Migration'):
                return obj
        
        raise Exception("No migration class found in file")