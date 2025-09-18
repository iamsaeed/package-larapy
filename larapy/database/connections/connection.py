"""Base database connection class"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
import logging


class Connection(ABC):
    """
    Base database connection class
    
    Provides the interface that all database connections must implement,
    including query execution, transaction management, and schema operations.
    """

    def __init__(self, config: Dict[str, Any], name: str):
        self.config = config
        self.name = name
        self.connection = None
        self.transactions = 0
        self.query_log = []
        self.logging_queries = False
        self.pretending = False
        
    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass
        
    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass
        
    @abstractmethod
    def select(self, query: str, bindings: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a select statement"""
        pass
        
    @abstractmethod
    def insert(self, query: str, bindings: List[Any] = None) -> Union[bool, int]:
        """Execute an insert statement"""
        pass
        
    @abstractmethod
    def update(self, query: str, bindings: List[Any] = None) -> int:
        """Execute an update statement"""
        pass
        
    @abstractmethod
    def delete(self, query: str, bindings: List[Any] = None) -> int:
        """Execute a delete statement"""
        pass
        
    @abstractmethod
    def statement(self, query: str, bindings: List[Any] = None) -> bool:
        """Execute a general statement"""
        pass
        
    def prepare_bindings(self, bindings: List[Any]) -> List[Any]:
        """Prepare the query bindings"""
        if bindings is None:
            return []
        return bindings
        
    def bind_values(self, query: str, bindings: List[Any]) -> str:
        """Bind values to the query"""
        if not bindings:
            return query
        return query
        
    def log_query(self, query: str, bindings: List[Any], time: float = None):
        """Log a query"""
        if self.logging_queries:
            self.query_log.append({
                'query': query,
                'bindings': bindings,
                'time': time
            })
            
    def get_query_log(self) -> List[Dict[str, Any]]:
        """Get the query log"""
        return self.query_log
        
    def flush_query_log(self):
        """Clear the query log"""
        self.query_log = []
        
    def enable_query_log(self):
        """Enable query logging"""
        self.logging_queries = True
        
    def disable_query_log(self):
        """Disable query logging"""
        self.logging_queries = False
        
    def transaction(self, callback: Callable, attempts: int = 1):
        """Execute a transaction"""
        for attempt in range(attempts):
            try:
                self.begin_transaction()
                result = callback(self)
                self.commit()
                return result
            except Exception as e:
                self.rollback()
                if attempt == attempts - 1:
                    raise e
                
    def begin_transaction(self):
        """Begin a transaction"""
        self.transactions += 1
        if self.transactions == 1:
            self._begin_transaction()
            
    def commit(self):
        """Commit a transaction"""
        if self.transactions == 1:
            self._commit()
        self.transactions = max(0, self.transactions - 1)
        
    def rollback(self):
        """Rollback a transaction"""
        if self.transactions == 1:
            self._rollback()
        self.transactions = max(0, self.transactions - 1)
        
    @abstractmethod
    def _begin_transaction(self):
        """Implementation-specific begin transaction"""
        pass
        
    @abstractmethod
    def _commit(self):
        """Implementation-specific commit"""
        pass
        
    @abstractmethod
    def _rollback(self):
        """Implementation-specific rollback"""
        pass
        
    def table(self, table: str):
        """Get a query builder for a table"""
        from ..query.builder import QueryBuilder
        from ..query.grammar import Grammar
        from ..query.processor import Processor
        
        grammar = self.get_query_grammar()
        processor = self.get_post_processor()
        
        return QueryBuilder(self, grammar, processor, table)
        
    @abstractmethod
    def get_query_grammar(self):
        """Get the query grammar"""
        pass
        
    @abstractmethod
    def get_post_processor(self):
        """Get the post processor"""
        pass
        
    @abstractmethod
    def get_schema_builder(self):
        """Get a schema builder instance"""
        pass
        
    def get_config(self, option: str = None):
        """Get configuration option"""
        if option is None:
            return self.config
        return self.config.get(option)
        
    def get_name(self) -> str:
        """Get the connection name"""
        return self.name
        
    def get_database_name(self) -> str:
        """Get the database name"""
        return self.config.get('database')
        
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connection is not None
        
    def reconnect(self):
        """Reconnect to the database"""
        self.disconnect()
        self.connect()
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()