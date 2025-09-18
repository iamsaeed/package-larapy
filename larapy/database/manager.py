"""Enhanced Database Manager with Laravel-like functionality"""

from typing import Dict, Any, Optional, Union
from .connections.connection import Connection
from .connections.sqlite_connection import SQLiteConnection
from .query.builder import QueryBuilder


class DatabaseManager:
    """
    Laravel-style Database Manager

    Manages multiple database connections with lazy loading,
    connection pooling, and transaction management.
    """

    def __init__(self, app):
        self.app = app
        self.connections = {}
        self.default_connection = None
        
        # Connection drivers
        self.drivers = {
            'sqlite': SQLiteConnection,
            # 'mysql': MySQLConnection,     # Will implement later
            # 'postgres': PostgreSQLConnection,  # Will implement later
        }

    def connection(self, name: Optional[str] = None) -> Connection:
        """Get a database connection instance"""
        name = name or self.get_default_connection()
        
        if name not in self.connections:
            self.connections[name] = self._make_connection(name)
            
        return self.connections[name]

    def _make_connection(self, name: str) -> Connection:
        """Create a new connection instance"""
        config = self._get_connection_config(name)
        driver = config.get('driver', 'sqlite')
        
        if driver not in self.drivers:
            raise ValueError(f"Unsupported database driver: {driver}")
            
        connection_class = self.drivers[driver]
        connection = connection_class(config, name)
        connection.connect()
        
        return connection

    def _get_connection_config(self, name: str) -> Dict[str, Any]:
        """Get configuration for a specific connection"""
        config = self._get_config()
        connections = config.get('connections', {})
        
        if name not in connections:
            raise ValueError(f"Database connection [{name}] not configured")
            
        return connections[name]

    def _get_config(self) -> Dict[str, Any]:
        """Get database configuration from app"""
        return self.app.config.get('database', {})

    def get_default_connection(self) -> str:
        """Get the default connection name"""
        if self.default_connection:
            return self.default_connection
            
        config = self._get_config()
        return config.get('default', 'sqlite')

    def table(self, table: str, connection: Optional[str] = None) -> QueryBuilder:
        """Get a query builder for a table"""
        return self.connection(connection).table(table)

    def raw(self, sql: str, bindings: list = None, connection: Optional[str] = None):
        """Execute a raw SQL query"""
        return self.connection(connection).select(sql, bindings or [])

    def select(self, sql: str, bindings: list = None, connection: Optional[str] = None):
        """Execute a select statement"""
        return self.connection(connection).select(sql, bindings or [])

    def insert(self, sql: str, bindings: list = None, connection: Optional[str] = None):
        """Execute an insert statement"""
        return self.connection(connection).insert(sql, bindings or [])

    def update(self, sql: str, bindings: list = None, connection: Optional[str] = None):
        """Execute an update statement"""
        return self.connection(connection).update(sql, bindings or [])

    def delete(self, sql: str, bindings: list = None, connection: Optional[str] = None):
        """Execute a delete statement"""
        return self.connection(connection).delete(sql, bindings or [])

    def statement(self, sql: str, bindings: list = None, connection: Optional[str] = None):
        """Execute a general statement"""
        return self.connection(connection).statement(sql, bindings or [])

    def transaction(self, callback, connection: Optional[str] = None, attempts: int = 1):
        """Execute a transaction"""
        return self.connection(connection).transaction(callback, attempts)

    def begin_transaction(self, connection: Optional[str] = None):
        """Begin a transaction"""
        return self.connection(connection).begin_transaction()

    def commit(self, connection: Optional[str] = None):
        """Commit a transaction"""
        return self.connection(connection).commit()

    def rollback(self, connection: Optional[str] = None):
        """Rollback a transaction"""
        return self.connection(connection).rollback()

    def schema(self, connection: Optional[str] = None):
        """Get a schema builder instance"""
        return self.connection(connection).get_schema_builder()

    def disconnect(self, name: Optional[str] = None):
        """Disconnect from a database"""
        name = name or self.get_default_connection()
        
        if name in self.connections:
            self.connections[name].disconnect()
            del self.connections[name]

    def purge(self, name: Optional[str] = None):
        """Purge a connection instance"""
        self.disconnect(name)

    def get_connections(self) -> Dict[str, Connection]:
        """Get all connections"""
        return self.connections

    def set_default_connection(self, name: str):
        """Set the default connection"""
        self.default_connection = name

    def extend(self, name: str, driver_class):
        """Register a custom connection driver"""
        self.drivers[name] = driver_class