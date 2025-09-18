"""Migration runner for executing database migrations"""

import os
import importlib.util
import importlib.machinery
from typing import List, Dict, Any, Optional
from pathlib import Path
from .migration import Migration
from .repository import MigrationRepository


class Migrator:
    """
    Migration runner

    Handles the execution of migrations, tracking state,
    and rollback functionality.
    """

    def __init__(self, repository: MigrationRepository, connection_resolver, filesystem=None):
        self.repository = repository
        self.connection_resolver = connection_resolver
        self.filesystem = filesystem
        self.notes = []
        self.paths = []

    def run(self, paths: List[str] = None, options: Dict[str, Any] = None) -> List[str]:
        """Run the pending migrations"""
        self.notes = []
        options = options or {}
        
        # Ensure migration repository exists
        if not self.repository.repository_exists():
            self.repository.create_repository()
            
        # Get migration files
        migration_files = self.get_migration_files(paths or self.paths)
        
        # Get migrations that have already been run
        ran_migrations = self.repository.get_ran()
        
        # Get pending migrations
        pending_migrations = self.get_pending_migrations(migration_files, ran_migrations)
        
        if not pending_migrations:
            self.note('Nothing to migrate.')
            return self.notes
            
        # Get the next batch number
        batch = self.repository.get_next_batch_number()
        
        # Run each migration
        for migration_file in pending_migrations:
            self.run_migration(migration_file, 'up')
            self.repository.log(migration_file['name'], batch)
            
        return self.notes

    def rollback(self, paths: List[str] = None, options: Dict[str, Any] = None) -> List[str]:
        """Rollback migrations"""
        self.notes = []
        options = options or {}
        
        # Get the last batch of migrations
        migrations = self.repository.get_migrations()
        
        if not migrations:
            self.note('Nothing to rollback.')
            return self.notes
            
        # Get migrations to rollback
        last_batch = migrations[0]['batch']
        migrations_to_rollback = self.repository.get_migrations_for_batch(last_batch)
        
        # Rollback each migration
        for migration_info in migrations_to_rollback:
            self.rollback_migration(migration_info, 'down')
            self.repository.delete(migration_info['migration'])
            
        return self.notes

    def reset(self, paths: List[str] = None) -> List[str]:
        """Rollback all migrations"""
        self.notes = []
        
        # Get all migrations in reverse order
        migrations = self.repository.get_migrations()
        
        if not migrations:
            self.note('Nothing to rollback.')
            return self.notes
            
        # Rollback each migration
        for migration_info in migrations:
            self.rollback_migration(migration_info, 'down')
            self.repository.delete(migration_info['migration'])
            
        return self.notes

    def fresh(self, paths: List[str] = None, options: Dict[str, Any] = None) -> List[str]:
        """Drop all tables and re-run all migrations"""
        self.notes = []
        
        # Drop all tables
        self.drop_all_tables()
        
        # Re-run all migrations
        return self.run(paths, options)

    def run_migration(self, migration_file: Dict[str, str], method: str):
        """Run a single migration"""
        name = migration_file['name']
        path = migration_file['path']
        
        # Load the migration
        migration = self.load_migration(path)
        
        # Set up schema connection
        if hasattr(migration, 'connection') and migration.connection:
            connection = self.connection_resolver.connection(migration.connection)
        else:
            connection = self.connection_resolver.connection()
            
        migration.schema = connection.get_schema_builder()
        
        # Run the migration method
        try:
            if migration.within_transaction:
                def run_migration_method(conn):
                    getattr(migration, method)()
                    
                connection.transaction(run_migration_method)
            else:
                getattr(migration, method)()
                
            self.note(f"Migrated: {name}")
            
        except Exception as e:
            self.note(f"Migration failed: {name} - {str(e)}")
            raise

    def rollback_migration(self, migration_info: Dict[str, str], method: str):
        """Rollback a single migration"""
        migration_name = migration_info['migration']
        
        # Find the migration file
        migration_file = self.find_migration_file(migration_name)
        
        if not migration_file:
            self.note(f"Migration file not found: {migration_name}")
            return
            
        # Run the migration
        self.run_migration(migration_file, method)

    def load_migration(self, migration_path: str) -> Migration:
        """Load a migration class from file"""
        # Load the module
        spec = importlib.util.spec_from_file_location("migration_module", migration_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the migration class
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                issubclass(obj, Migration) and 
                obj is not Migration):
                return obj()
                
        raise ValueError(f"No migration class found in {migration_path}")

    def get_migration_files(self, paths: List[str]) -> List[Dict[str, str]]:
        """Get all migration files from the given paths"""
        migration_files = []
        
        for path in paths:
            if os.path.isdir(path):
                for file in sorted(os.listdir(path)):
                    if file.endswith('.py') and not file.startswith('__'):
                        migration_files.append({
                            'name': file[:-3],  # Remove .py extension
                            'path': os.path.join(path, file)
                        })
                        
        return migration_files

    def get_pending_migrations(self, migration_files: List[Dict[str, str]],
                              ran_migrations: List[str]) -> List[Dict[str, str]]:
        """Get migrations that haven't been run"""
        return [
            migration for migration in migration_files
            if migration['name'] not in ran_migrations
        ]

    def find_migration_file(self, migration_name: str) -> Optional[Dict[str, str]]:
        """Find a migration file by name"""
        migration_files = self.get_migration_files(self.paths)
        
        for migration_file in migration_files:
            if migration_file['name'] == migration_name:
                return migration_file
                
        return None

    def drop_all_tables(self):
        """Drop all database tables"""
        # This will be implemented per database type
        schema = self.connection_resolver.connection().get_schema_builder()
        # schema.drop_all_tables()  # Implementation depends on database type

    def note(self, message: str):
        """Add a note to the migration output"""
        self.notes.append(message)
        print(message)  # Also print for immediate feedback

    def get_migration_paths(self) -> List[str]:
        """Get configured migration paths"""
        return self.paths

    def set_paths(self, paths: List[str]):
        """Set migration paths"""
        self.paths = paths