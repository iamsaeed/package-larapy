"""
Laravel-style ORM Implementation for Larapy
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
import sqlite3
import json
from datetime import datetime


class DatabaseConnection:
    """Database connection wrapper"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        driver = self.config.get('driver', 'sqlite')
        
        if driver == 'sqlite':
            database = self.config.get('database', ':memory:')
            self.connection = sqlite3.connect(database, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        else:
            raise NotImplementedError(f"Driver {driver} not implemented yet")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        return self.connection.execute(query, params)
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all results from a query"""
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one result from a query"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def commit(self):
        """Commit the transaction"""
        self.connection.commit()
    
    def rollback(self):
        """Rollback the transaction"""
        self.connection.rollback()
    
    def close(self):
        """Close the connection"""
        if self.connection:
            self.connection.close()


class QueryBuilder:
    """Laravel-style Query Builder"""
    
    def __init__(self, connection: DatabaseConnection, table: str):
        self.connection = connection
        self.table = table
        self._select = ['*']
        self._where = []
        self._joins = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._limit = None
        self._offset = None
        
    def select(self, *columns):
        """Set the columns to select"""
        self._select = list(columns) if columns else ['*']
        return self
    
    def where(self, column: str, operator: str = '=', value: Any = None):
        """Add a where clause"""
        if value is None:
            value = operator
            operator = '='
        
        self._where.append((column, operator, value))
        return self
    
    def where_in(self, column: str, values: List[Any]):
        """Add a where in clause"""
        placeholders = ','.join(['?' for _ in values])
        self._where.append((f"{column} IN ({placeholders})", None, values))
        return self
    
    def order_by(self, column: str, direction: str = 'ASC'):
        """Add an order by clause"""
        self._order_by.append((column, direction.upper()))
        return self
    
    def limit(self, count: int):
        """Set the limit"""
        self._limit = count
        return self
    
    def offset(self, count: int):
        """Set the offset"""
        self._offset = count
        return self
    
    def join(self, table: str, first: str, operator: str = '=', second: str = None):
        """Add a join clause"""
        if second is None:
            second = operator
            operator = '='
        
        self._joins.append(('INNER JOIN', table, first, operator, second))
        return self
    
    def left_join(self, table: str, first: str, operator: str = '=', second: str = None):
        """Add a left join clause"""
        if second is None:
            second = operator
            operator = '='
        
        self._joins.append(('LEFT JOIN', table, first, operator, second))
        return self
    
    def _build_query(self) -> tuple:
        """Build the SQL query"""
        # SELECT clause
        select_clause = f"SELECT {', '.join(self._select)}"
        
        # FROM clause
        from_clause = f"FROM {self.table}"
        
        # JOIN clauses
        join_clauses = []
        for join_type, table, first, operator, second in self._joins:
            join_clauses.append(f"{join_type} {table} ON {first} {operator} {second}")
        
        # WHERE clause
        where_clauses = []
        params = []
        for where_item in self._where:
            if len(where_item) == 3 and where_item[1] is None:
                # Special case for IN clauses
                where_clauses.append(where_item[0])
                params.extend(where_item[2])
            else:
                column, operator, value = where_item
                where_clauses.append(f"{column} {operator} ?")
                params.append(value)
        
        # ORDER BY clause
        order_clauses = []
        for column, direction in self._order_by:
            order_clauses.append(f"{column} {direction}")
        
        # Build final query
        query_parts = [select_clause, from_clause]
        
        if join_clauses:
            query_parts.extend(join_clauses)
        
        if where_clauses:
            query_parts.append(f"WHERE {' AND '.join(where_clauses)}")
        
        if order_clauses:
            query_parts.append(f"ORDER BY {', '.join(order_clauses)}")
        
        if self._limit:
            query_parts.append(f"LIMIT {self._limit}")
        
        if self._offset:
            query_parts.append(f"OFFSET {self._offset}")
        
        return ' '.join(query_parts), tuple(params)
    
    def get(self) -> List[Dict]:
        """Execute the query and get results"""
        query, params = self._build_query()
        return self.connection.fetch_all(query, params)
    
    def first(self) -> Optional[Dict]:
        """Get the first result"""
        query, params = self._build_query()
        return self.connection.fetch_one(query, params)
    
    def count(self) -> int:
        """Get the count of results"""
        original_select = self._select
        self._select = ['COUNT(*) as count']
        query, params = self._build_query()
        result = self.connection.fetch_one(query, params)
        self._select = original_select
        return result['count'] if result else 0
    
    def insert(self, data: Dict[str, Any]) -> int:
        """Insert a new record"""
        columns = list(data.keys())
        placeholders = ','.join(['?' for _ in columns])
        values = list(data.values())
        
        query = f"INSERT INTO {self.table} ({','.join(columns)}) VALUES ({placeholders})"
        cursor = self.connection.execute(query, tuple(values))
        self.connection.commit()
        return cursor.lastrowid
    
    def update(self, data: Dict[str, Any]) -> int:
        """Update records"""
        set_clauses = []
        params = []
        
        for column, value in data.items():
            set_clauses.append(f"{column} = ?")
            params.append(value)
        
        # Add where parameters
        where_clauses = []
        for where_item in self._where:
            if len(where_item) == 3 and where_item[1] is None:
                where_clauses.append(where_item[0])
                params.extend(where_item[2])
            else:
                column, operator, value = where_item
                where_clauses.append(f"{column} {operator} ?")
                params.append(value)
        
        query = f"UPDATE {self.table} SET {', '.join(set_clauses)}"
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        cursor = self.connection.execute(query, tuple(params))
        self.connection.commit()
        return cursor.rowcount
    
    def delete(self) -> int:
        """Delete records"""
        where_clauses = []
        params = []
        
        for where_item in self._where:
            if len(where_item) == 3 and where_item[1] is None:
                where_clauses.append(where_item[0])
                params.extend(where_item[2])
            else:
                column, operator, value = where_item
                where_clauses.append(f"{column} {operator} ?")
                params.append(value)
        
        query = f"DELETE FROM {self.table}"
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        cursor = self.connection.execute(query, tuple(params))
        self.connection.commit()
        return cursor.rowcount


class ModelMeta(type):
    """Metaclass for Model to handle class creation"""
    
    def __new__(cls, name, bases, attrs):
        # Set table name if not specified
        if 'table' not in attrs and name != 'Model':
            attrs['table'] = name.lower() + 's'
        
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    """Laravel-style Eloquent Model"""
    
    table = None
    primary_key = 'id'
    fillable = []
    guarded = ['id']
    timestamps = True
    created_at = 'created_at'
    updated_at = 'updated_at'
    
    _connection = None
    
    def __init__(self, **attributes):
        self.attributes = {}
        self.original = {}
        self.exists = False
        
        # Set attributes
        for key, value in attributes.items():
            self.attributes[key] = value
    
    @classmethod
    def set_connection(cls, connection: DatabaseConnection):
        """Set the database connection"""
        cls._connection = connection
    
    @classmethod
    def query(cls) -> QueryBuilder:
        """Get a query builder instance"""
        if not cls._connection:
            raise RuntimeError("No database connection set")
        return QueryBuilder(cls._connection, cls.table)
    
    @classmethod
    def all(cls) -> List['Model']:
        """Get all records"""
        results = cls.query().get()
        return [cls._hydrate(result) for result in results]
    
    @classmethod
    def find(cls, id: Any) -> Optional['Model']:
        """Find a record by primary key"""
        result = cls.query().where(cls.primary_key, id).first()
        return cls._hydrate(result) if result else None
    
    @classmethod
    def where(cls, column: str, operator: str = '=', value: Any = None):
        """Add a where clause and return query builder"""
        return cls.query().where(column, operator, value)
    
    @classmethod
    def create(cls, **attributes) -> 'Model':
        """Create a new record"""
        instance = cls(**attributes)
        instance.save()
        return instance
    
    @classmethod
    def _hydrate(cls, data: Dict) -> 'Model':
        """Create a model instance from database data"""
        if not data:
            return None
        
        instance = cls()
        instance.attributes = data.copy()
        instance.original = data.copy()
        instance.exists = True
        return instance
    
    def save(self) -> bool:
        """Save the model"""
        if self.exists:
            return self._update()
        else:
            return self._insert()
    
    def _insert(self) -> bool:
        """Insert a new record"""
        # Add timestamps
        if self.timestamps:
            now = datetime.now().isoformat()
            self.attributes[self.created_at] = now
            self.attributes[self.updated_at] = now
        
        # Filter fillable attributes
        data = self._get_fillable_attributes()
        
        if not data:
            return False
        
        # Insert the record
        id = self.query().insert(data)
        
        if id:
            self.attributes[self.primary_key] = id
            self.original = self.attributes.copy()
            self.exists = True
            return True
        
        return False
    
    def _update(self) -> bool:
        """Update an existing record"""
        # Get dirty attributes
        dirty = self._get_dirty()
        
        if not dirty:
            return True
        
        # Add updated timestamp
        if self.timestamps:
            dirty[self.updated_at] = datetime.now().isoformat()
        
        # Update the record
        rows_affected = (self.query()
                        .where(self.primary_key, self.get_key())
                        .update(dirty))
        
        if rows_affected > 0:
            self.original.update(dirty)
            return True
        
        return False
    
    def delete(self) -> bool:
        """Delete the model"""
        if not self.exists:
            return False
        
        rows_affected = (self.query()
                        .where(self.primary_key, self.get_key())
                        .delete())
        
        if rows_affected > 0:
            self.exists = False
            return True
        
        return False
    
    def get_key(self) -> Any:
        """Get the primary key value"""
        return self.attributes.get(self.primary_key)
    
    def _get_fillable_attributes(self) -> Dict[str, Any]:
        """Get fillable attributes"""
        if self.fillable:
            return {k: v for k, v in self.attributes.items() if k in self.fillable}
        else:
            return {k: v for k, v in self.attributes.items() if k not in self.guarded}
    
    def _get_dirty(self) -> Dict[str, Any]:
        """Get dirty (changed) attributes"""
        dirty = {}
        for key, value in self.attributes.items():
            if key not in self.original or self.original[key] != value:
                dirty[key] = value
        return dirty
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.attributes.copy()
    
    def to_json(self) -> str:
        """Convert model to JSON"""
        return json.dumps(self.to_dict(), default=str)
    
    def __getattr__(self, name):
        """Get attribute value"""
        if name in self.attributes:
            return self.attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """Set attribute value"""
        if name.startswith('_') or name in ['attributes', 'original', 'exists']:
            super().__setattr__(name, value)
        else:
            if not hasattr(self, 'attributes'):
                super().__setattr__(name, value)
            else:
                self.attributes[name] = value
    
    def __repr__(self):
        """String representation"""
        return f"<{self.__class__.__name__}({self.attributes})>"


# Database Manager for handling multiple connections
class DatabaseManager:
    """Database Manager for handling multiple database connections"""
    
    def __init__(self):
        self.connections = {}
        self.default = 'default'
    
    def add_connection(self, name: str, config: Dict[str, Any]):
        """Add a database connection"""
        self.connections[name] = DatabaseConnection(config)
    
    def connection(self, name: str = None) -> DatabaseConnection:
        """Get a database connection"""
        name = name or self.default
        if name not in self.connections:
            raise ValueError(f"Database connection '{name}' not found")
        return self.connections[name]
    
    def set_default(self, name: str):
        """Set the default connection"""
        self.default = name
    
    def table(self, table_name: str, connection: str = None) -> QueryBuilder:
        """Get a query builder for a table"""
        conn = self.connection(connection)
        return QueryBuilder(conn, table_name)


# Schema Builder for migrations
class Schema:
    """Schema Builder for database migrations"""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
    
    def create_table(self, table_name: str, callback):
        """Create a new table"""
        blueprint = Blueprint(table_name)
        callback(blueprint)
        
        query = blueprint.to_sql()
        self.connection.execute(query)
        self.connection.commit()
    
    def drop_table(self, table_name: str):
        """Drop a table"""
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.connection.execute(query)
        self.connection.commit()
    
    def has_table(self, table_name: str) -> bool:
        """Check if table exists"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.connection.fetch_one(query, (table_name,))
        return result is not None


class Blueprint:
    """Blueprint for table creation"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.columns = []
    
    def id(self, name: str = 'id'):
        """Add an auto-incrementing ID column"""
        self.columns.append(f"{name} INTEGER PRIMARY KEY AUTOINCREMENT")
        return self
    
    def string(self, name: str, length: int = 255):
        """Add a string column"""
        self.columns.append(f"{name} VARCHAR({length})")
        return self
    
    def text(self, name: str):
        """Add a text column"""
        self.columns.append(f"{name} TEXT")
        return self
    
    def integer(self, name: str):
        """Add an integer column"""
        self.columns.append(f"{name} INTEGER")
        return self
    
    def float(self, name: str):
        """Add a float column"""
        self.columns.append(f"{name} REAL")
        return self
    
    def boolean(self, name: str):
        """Add a boolean column"""
        self.columns.append(f"{name} BOOLEAN")
        return self
    
    def timestamp(self, name: str):
        """Add a timestamp column"""
        self.columns.append(f"{name} TIMESTAMP")
        return self
    
    def timestamps(self):
        """Add created_at and updated_at columns"""
        self.timestamp('created_at')
        self.timestamp('updated_at')
        return self
    
    def nullable(self):
        """Make the last column nullable"""
        if self.columns:
            self.columns[-1] += " NULL"
        return self
    
    def default(self, value):
        """Set default value for the last column"""
        if self.columns:
            if isinstance(value, str):
                self.columns[-1] += f" DEFAULT '{value}'"
            else:
                self.columns[-1] += f" DEFAULT {value}"
        return self
    
    def to_sql(self) -> str:
        """Generate SQL for table creation"""
        columns_sql = ', '.join(self.columns)
        return f"CREATE TABLE {self.table_name} ({columns_sql})"
