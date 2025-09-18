"""Migration repository for tracking migration state"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class MigrationRepository:
    """
    Migration repository

    Tracks which migrations have been run and provides
    methods for querying migration state.
    """

    def __init__(self, connection_resolver, table: str = 'migrations'):
        self.connection_resolver = connection_resolver
        self.table = table
        self.connection_name = None

    def get_ran(self) -> List[str]:
        """Get list of migrations that have been run"""
        return [
            row['migration'] for row in self.table().order_by('batch', 'asc').get()
        ]

    def get_migrations(self, steps: int = None) -> List[Dict[str, Any]]:
        """Get migration records"""
        query = self.table().order_by('batch', 'desc').order_by('migration', 'desc')
        
        if steps:
            query = query.limit(steps)
            
        return query.get()

    def get_last_batch_number(self) -> int:
        """Get the last batch number"""
        result = self.table().max('batch')
        return result if result is not None else 0

    def get_next_batch_number(self) -> int:
        """Get the next batch number"""
        return self.get_last_batch_number() + 1

    def get_migrations_for_batch(self, batch: int) -> List[Dict[str, Any]]:
        """Get migrations for a specific batch"""
        return self.table().where('batch', batch).order_by('migration', 'desc').get()

    def log(self, migration: str, batch: int):
        """Log that a migration was run"""
        record = {
            'migration': migration,
            'batch': batch
        }
        
        self.table().insert(record)

    def delete(self, migration: str):
        """Remove a migration from the log"""
        self.table().where('migration', migration).delete()

    def repository_exists(self) -> bool:
        """Determine if the migration repository exists"""
        schema = self.get_connection().get_schema_builder()
        return schema.has_table(self.table)

    def create_repository(self):
        """Create the migration repository"""
        schema = self.get_connection().get_schema_builder()
        
        def create_table(table):
            table.increments('id')
            table.string('migration')
            table.integer('batch')
        
        schema.create(self.table, create_table)

    def delete_repository(self):
        """Delete the migration repository"""
        schema = self.get_connection().get_schema_builder()
        schema.drop_if_exists(self.table)

    def table(self):
        """Get a query builder for the migration table"""
        return self.get_connection().table(self.table)

    def get_connection_resolver(self):
        """Get the database connection resolver"""
        return self.connection_resolver

    def get_connection(self):
        """Get the database connection"""
        return self.connection_resolver.connection(self.connection_name)

    def set_source(self, name: str):
        """Set the information source to gather data"""
        self.connection_name = name