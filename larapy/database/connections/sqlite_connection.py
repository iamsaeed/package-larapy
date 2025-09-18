"""SQLite database connection"""

import sqlite3
import os
from typing import Dict, Any, List, Optional, Union
from .connection import Connection
from ..query.grammar import Grammar
from ..query.processor import Processor


class SQLiteGrammar(Grammar):
    """SQLite-specific SQL grammar"""
    
    def wrap_value(self, value: str) -> str:
        """Wrap a single value for SQLite"""
        return f'"{value}"'


class SQLiteProcessor(Processor):
    """SQLite-specific result processor"""
    
    def process_insert_get_id(self, query, sql: str, values: List[Any], sequence: str = None) -> int:
        """Process insert and get ID for SQLite"""
        cursor = query.connection.connection.cursor()
        cursor.execute(sql, values)
        return cursor.lastrowid


class SQLiteConnection(Connection):
    """SQLite database connection"""
    
    def connect(self):
        """Establish SQLite connection"""
        if self.connection is not None:
            return
            
        database_path = self.config.get('database')
        
        # Create directory if it doesn't exist
        if database_path and database_path != ':memory:':
            os.makedirs(os.path.dirname(database_path), exist_ok=True)
            
        self.connection = sqlite3.connect(
            database_path,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        
        # Enable foreign key constraints
        if self.config.get('foreign_key_constraints', True):
            self.connection.execute('PRAGMA foreign_keys = ON')
            
        # Set row factory to return dict-like objects
        self.connection.row_factory = sqlite3.Row
        
    def disconnect(self):
        """Close SQLite connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def select(self, query: str, bindings: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a select statement"""
        bindings = self.prepare_bindings(bindings)
        
        try:
            cursor = self.connection.cursor()
            self.log_query(query, bindings)
            
            if bindings:
                cursor.execute(query, bindings)
            else:
                cursor.execute(query)
                
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            raise Exception(f"SQLite select error: {e}")
            
    def insert(self, query: str, bindings: List[Any] = None) -> Union[bool, int]:
        """Execute an insert statement"""
        bindings = self.prepare_bindings(bindings)
        
        try:
            cursor = self.connection.cursor()
            self.log_query(query, bindings)
            
            if bindings:
                cursor.execute(query, bindings)
            else:
                cursor.execute(query)
                
            return cursor.lastrowid if cursor.lastrowid else True
            
        except sqlite3.Error as e:
            raise Exception(f"SQLite insert error: {e}")
            
    def update(self, query: str, bindings: List[Any] = None) -> int:
        """Execute an update statement"""
        bindings = self.prepare_bindings(bindings)
        
        try:
            cursor = self.connection.cursor()
            self.log_query(query, bindings)
            
            if bindings:
                cursor.execute(query, bindings)
            else:
                cursor.execute(query)
                
            return cursor.rowcount
            
        except sqlite3.Error as e:
            raise Exception(f"SQLite update error: {e}")
            
    def delete(self, query: str, bindings: List[Any] = None) -> int:
        """Execute a delete statement"""
        bindings = self.prepare_bindings(bindings)
        
        try:
            cursor = self.connection.cursor()
            self.log_query(query, bindings)
            
            if bindings:
                cursor.execute(query, bindings)
            else:
                cursor.execute(query)
                
            return cursor.rowcount
            
        except sqlite3.Error as e:
            raise Exception(f"SQLite delete error: {e}")
            
    def statement(self, query: str, bindings: List[Any] = None) -> bool:
        """Execute a general statement"""
        bindings = self.prepare_bindings(bindings)
        
        try:
            cursor = self.connection.cursor()
            self.log_query(query, bindings)
            
            if bindings:
                cursor.execute(query, bindings)
            else:
                cursor.execute(query)
                
            return True
            
        except sqlite3.Error as e:
            raise Exception(f"SQLite statement error: {e}")
            
    def _begin_transaction(self):
        """Begin SQLite transaction"""
        self.connection.execute('BEGIN TRANSACTION')
        
    def _commit(self):
        """Commit SQLite transaction"""
        self.connection.execute('COMMIT')
        
    def _rollback(self):
        """Rollback SQLite transaction"""
        self.connection.execute('ROLLBACK')
        
    def get_query_grammar(self):
        """Get SQLite query grammar"""
        return SQLiteGrammar()
        
    def get_post_processor(self):
        """Get SQLite post processor"""
        return SQLiteProcessor()
        
    def get_schema_builder(self):
        """Get SQLite schema builder"""
        from ..schema.builder import SchemaBuilder
        return SchemaBuilder(self)
        
    def get_column_listing(self, table: str) -> List[str]:
        """Get column listing for a table"""
        query = f"PRAGMA table_info({self.get_query_grammar().wrap_table(table)})"
        results = self.select(query)
        return [row['name'] for row in results]
        
    def get_columns(self, table: str) -> List[Dict[str, Any]]:
        """Get detailed column information"""
        query = f"PRAGMA table_info({self.get_query_grammar().wrap_table(table)})"
        results = self.select(query)
        
        columns = []
        for row in results:
            columns.append({
                'name': row['name'],
                'type': row['type'],
                'nullable': not row['notnull'],
                'default': row['dflt_value'],
                'primary': bool(row['pk'])
            })
            
        return columns