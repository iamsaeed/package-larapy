"""Larapy Database Package

Laravel-inspired database toolkit for Python with ORM, Query Builder, Migrations, and more.
"""

# Core database components
from .manager import DatabaseManager
from .connections.connection import Connection
from .query.builder import QueryBuilder
from .query.grammar import Grammar
from .query.processor import Processor

# Schema building
from .schema.builder import SchemaBuilder
from .schema.blueprint import Blueprint

# Migrations
from .migrations.migration import Migration
from .migrations.migrator import Migrator
from .migrations.repository import DatabaseMigrationRepository
from .migrations.creator import MigrationCreator

# Eloquent ORM
from .eloquent.model import Model
from .eloquent.builder import Builder as EloquentBuilder

# Relationships
from .eloquent.relations.has_one import HasOne
from .eloquent.relations.has_many import HasMany
from .eloquent.relations.belongs_to import BelongsTo
from .eloquent.relations.belongs_to_many import BelongsToMany

# Factory and Seeding
from .factory import Factory, factory, create, make, define_factory
from .seeder import Seeder, DatabaseSeeder, seed

# Console commands (main ones that exist)
from .console.migrate_command import MigrateCommand
from .console.make_migration_command import MakeMigrationCommand
from .console.seed_command import SeedCommand

# Legacy imports for backward compatibility
from .connections.connection import Connection as DatabaseConnection
from .schema.builder import SchemaBuilder as Schema

__version__ = '0.1.0'

__all__ = [
    # Core
    'DatabaseManager', 'Connection', 'QueryBuilder', 'Grammar', 'Processor',
    
    # Schema
    'SchemaBuilder', 'Blueprint',
    
    # Migrations
    'Migration', 'Migrator', 'DatabaseMigrationRepository', 'MigrationCreator',
    
    # Eloquent
    'Model', 'EloquentBuilder',
    
    # Relationships
    'HasOne', 'HasMany', 'BelongsTo', 'BelongsToMany',
    
    # Factory & Seeding
    'Factory', 'factory', 'create', 'make', 'define_factory',
    'Seeder', 'DatabaseSeeder', 'seed',
    
    # Console Commands
    'MigrateCommand', 'MakeMigrationCommand', 'SeedCommand',
    
    # Legacy (backward compatibility)
    'DatabaseConnection', 'Schema'
]


def configure_database(config: dict = None):
    """Configure the database connection
    
    Args:
        config: Database configuration dictionary
                
    Example:
        configure_database({
            'default': 'sqlite',
            'connections': {
                'sqlite': {
                    'driver': 'sqlite',
                    'database': 'database.sqlite'
                }
            }
        })
    """
    if config is None:
        # Try to load from default config
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            from config.database import CONNECTIONS, DEFAULT
            config = {
                'default': DEFAULT,
                'connections': CONNECTIONS
            }
        except ImportError:
            # Use SQLite as fallback
            config = {
                'default': 'sqlite',
                'connections': {
                    'sqlite': {
                        'driver': 'sqlite',
                        'database': 'database.sqlite'
                    }
                }
            }
    
    manager = DatabaseManager.get_instance()
    manager.set_config(config)
    return manager


def get_database_manager() -> DatabaseManager:
    """Get the database manager instance"""
    return DatabaseManager.get_instance()


def table(name: str) -> QueryBuilder:
    """Get a query builder for a table
    
    Args:
        name: Table name
        
    Returns:
        QueryBuilder instance
    """
    manager = DatabaseManager.get_instance()
    return manager.table(name)


def schema() -> SchemaBuilder:
    """Get a schema builder instance
    
    Returns:
        SchemaBuilder instance
    """
    manager = DatabaseManager.get_instance()
    return manager.schema()


def connection(name: str = None) -> Connection:
    """Get a database connection
    
    Args:
        name: Connection name (uses default if None)
        
    Returns:
        Connection instance
    """
    manager = DatabaseManager.get_instance()
    return manager.connection(name)


def transaction(callback, connection_name: str = None):
    """Run a database transaction
    
    Args:
        callback: Function to execute in transaction
        connection_name: Connection to use (default if None)
        
    Returns:
        Transaction result
    """
    manager = DatabaseManager.get_instance()
    return manager.transaction(callback, connection_name)


def raw(expression: str):
    """Create a raw database expression
    
    Args:
        expression: Raw SQL expression
        
    Returns:
        Raw expression string (simplified implementation)
    """
    return f"RAW({expression})"


def select(query: str, bindings: list = None, connection_name: str = None):
    """Execute a select statement
    
    Args:
        query: SQL query
        bindings: Query bindings
        connection_name: Connection to use
        
    Returns:
        Query results
    """
    manager = DatabaseManager.get_instance()
    conn = manager.connection(connection_name)
    return conn.select(query, bindings or [])


def insert(query: str, bindings: list = None, connection_name: str = None):
    """Execute an insert statement
    
    Args:
        query: SQL query
        bindings: Query bindings
        connection_name: Connection to use
        
    Returns:
        Insert result
    """
    manager = DatabaseManager.get_instance()
    conn = manager.connection(connection_name)
    return conn.insert(query, bindings or [])


def update(query: str, bindings: list = None, connection_name: str = None):
    """Execute an update statement
    
    Args:
        query: SQL query
        bindings: Query bindings
        connection_name: Connection to use
        
    Returns:
        Number of affected rows
    """
    manager = DatabaseManager.get_instance()
    conn = manager.connection(connection_name)
    return conn.update(query, bindings or [])


def delete(query: str, bindings: list = None, connection_name: str = None):
    """Execute a delete statement
    
    Args:
        query: SQL query
        bindings: Query bindings
        connection_name: Connection to use
        
    Returns:
        Number of affected rows
    """
    manager = DatabaseManager.get_instance()
    conn = manager.connection(connection_name)
    return conn.delete(query, bindings or [])
