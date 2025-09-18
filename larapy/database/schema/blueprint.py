"""Database table blueprint"""

from typing import Dict, Any, List, Optional, Union


class Blueprint:
    """
    Database table blueprint
    
    Defines the structure of a database table with columns,
    indexes, foreign keys, and other constraints.
    """

    def __init__(self, table: str):
        self.table = table
        self.columns = []
        self.commands = []
        self.indexes = []
        self.foreign_keys = []
        self.unique_constraints = []
        self.primary = None
        self.auto_increment = False

    # Column definition methods
    def id(self, column: str = 'id'):
        """Create an auto-incrementing primary key column"""
        self.big_increments(column)
        return self

    def increments(self, column: str):
        """Create an auto-incrementing integer primary key"""
        col = self.integer(column, auto_increment=True, nullable=False)
        self.primary([column])
        return col

    def big_increments(self, column: str):
        """Create an auto-incrementing big integer primary key"""
        col = self.big_integer(column, auto_increment=True, nullable=False)
        self.primary([column])
        return col

    def string(self, column: str, length: int = 255):
        """Create a string column"""
        return self._add_column('string', column, length=length)

    def char(self, column: str, length: int = 4):
        """Create a char column"""
        return self._add_column('char', column, length=length)

    def text(self, column: str):
        """Create a text column"""
        return self._add_column('text', column)

    def medium_text(self, column: str):
        """Create a medium text column"""
        return self._add_column('medium_text', column)

    def long_text(self, column: str):
        """Create a long text column"""
        return self._add_column('long_text', column)

    def integer(self, column: str, auto_increment: bool = False, nullable: bool = True):
        """Create an integer column"""
        return self._add_column('integer', column, auto_increment=auto_increment, nullable=nullable)

    def big_integer(self, column: str, auto_increment: bool = False, nullable: bool = True):
        """Create a big integer column"""
        return self._add_column('big_integer', column, auto_increment=auto_increment, nullable=nullable)

    def medium_integer(self, column: str):
        """Create a medium integer column"""
        return self._add_column('medium_integer', column)

    def small_integer(self, column: str):
        """Create a small integer column"""
        return self._add_column('small_integer', column)

    def tiny_integer(self, column: str):
        """Create a tiny integer column"""
        return self._add_column('tiny_integer', column)

    def boolean(self, column: str):
        """Create a boolean column"""
        return self._add_column('boolean', column)

    def decimal(self, column: str, precision: int = 8, scale: int = 2):
        """Create a decimal column"""
        return self._add_column('decimal', column, precision=precision, scale=scale)

    def double(self, column: str, precision: int = None, scale: int = None):
        """Create a double column"""
        return self._add_column('double', column, precision=precision, scale=scale)

    def float(self, column: str, precision: int = 8, scale: int = 2):
        """Create a float column"""
        return self._add_column('float', column, precision=precision, scale=scale)

    def date(self, column: str):
        """Create a date column"""
        return self._add_column('date', column)

    def datetime(self, column: str):
        """Create a datetime column"""
        return self._add_column('datetime', column)

    def timestamp(self, column: str):
        """Create a timestamp column"""
        return self._add_column('timestamp', column)

    def time(self, column: str):
        """Create a time column"""
        return self._add_column('time', column)

    def timestamps(self, nullable: bool = False):
        """Add created_at and updated_at timestamp columns"""
        self.timestamp('created_at').nullable(nullable).default('CURRENT_TIMESTAMP')
        self.timestamp('updated_at').nullable(nullable).default('CURRENT_TIMESTAMP')

    def json(self, column: str):
        """Create a JSON column"""
        return self._add_column('json', column)

    def binary(self, column: str):
        """Create a binary column"""
        return self._add_column('binary', column)

    def enum(self, column: str, allowed: List[str]):
        """Create an enum column"""
        return self._add_column('enum', column, allowed=allowed)

    # Foreign key methods
    def foreign(self, columns: Union[str, List[str]], name: str = None):
        """Create a foreign key constraint"""
        if isinstance(columns, str):
            columns = [columns]

        foreign_key = {
            'columns': columns,
            'name': name
        }

        self.foreign_keys.append(foreign_key)
        return ForeignKeyDefinition(foreign_key)

    def foreign_id(self, column: str = None):
        """Create a foreign ID column"""
        if column is None:
            # Extract table name from column name (e.g., user_id -> users)
            pass  # Implementation depends on naming conventions
        
        col = self.unsignedBigInteger(column)
        return self.foreign([column])

    def foreign_id_for(self, model, column: str = None):
        """Create a foreign ID column for a specific model"""
        if column is None:
            # Generate column name from model
            pass
        
        return self.foreign_id(column)

    # Index methods
    def index(self, columns: Union[str, List[str]], name: str = None):
        """Create an index"""
        if isinstance(columns, str):
            columns = [columns]

        self.indexes.append({
            'type': 'index',
            'columns': columns,
            'name': name
        })
        return self

    def unique(self, columns: Union[str, List[str]], name: str = None):
        """Create a unique constraint"""
        if isinstance(columns, str):
            columns = [columns]

        self.unique_constraints.append({
            'columns': columns,
            'name': name
        })
        return self

    def primary(self, columns: Union[str, List[str]]):
        """Set the primary key"""
        if isinstance(columns, str):
            columns = [columns]
        self.primary = columns
        return self

    # Table modification methods
    def drop_column(self, column: str):
        """Drop a column"""
        self.commands.append({
            'type': 'drop_column',
            'column': column
        })
        return self

    def drop_columns(self, columns: List[str]):
        """Drop multiple columns"""
        for column in columns:
            self.drop_column(column)
        return self

    def rename_column(self, from_name: str, to_name: str):
        """Rename a column"""
        self.commands.append({
            'type': 'rename_column',
            'from': from_name,
            'to': to_name
        })
        return self

    def drop_index(self, name: str):
        """Drop an index"""
        self.commands.append({
            'type': 'drop_index',
            'name': name
        })
        return self

    def drop_foreign(self, name: str):
        """Drop a foreign key constraint"""
        self.commands.append({
            'type': 'drop_foreign',
            'name': name
        })
        return self

    def drop_primary(self):
        """Drop the primary key"""
        self.commands.append({
            'type': 'drop_primary'
        })
        return self

    def drop_unique(self, name: str):
        """Drop a unique constraint"""
        self.commands.append({
            'type': 'drop_unique',
            'name': name
        })
        return self

    # Helper methods
    def _add_column(self, type_: str, name: str, **attributes):
        """Add a column to the blueprint"""
        column = ColumnDefinition(type_, name, **attributes)
        self.columns.append(column.attributes)
        return column

    def to_sql(self, connection, grammar):
        """Convert the blueprint to SQL statements"""
        statements = []
        
        # Check if this is a create or alter operation
        if self._is_create():
            statements.append(self._compile_create(connection, grammar))
        else:
            statements.extend(self._compile_alter(connection, grammar))
            
        return statements

    def _is_create(self) -> bool:
        """Determine if this is a create table operation"""
        return len(self.columns) > 0 and len(self.commands) == 0

    def _compile_create(self, connection, grammar):
        """Compile create table statement"""
        schema_builder = connection.get_schema_builder()
        return schema_builder._compile_create(self)

    def _compile_alter(self, connection, grammar):
        """Compile alter table statements"""
        statements = []
        
        for command in self.commands:
            if command['type'] == 'drop_column':
                statements.append(f"ALTER TABLE {grammar.wrap_table(self.table)} DROP COLUMN {grammar.wrap(command['column'])}")
            elif command['type'] == 'rename_column':
                statements.append(f"ALTER TABLE {grammar.wrap_table(self.table)} RENAME COLUMN {grammar.wrap(command['from'])} TO {grammar.wrap(command['to'])}")
            # Add more command types as needed
            
        return statements


class ColumnDefinition:
    """Column definition with fluent interface"""

    def __init__(self, type_: str, name: str, **attributes):
        self.attributes = {
            'type': type_,
            'name': name,
            'nullable': True,
            **attributes
        }

    def nullable(self, nullable: bool = True):
        """Set column as nullable"""
        self.attributes['nullable'] = nullable
        return self

    def default(self, value: Any):
        """Set default value"""
        self.attributes['default'] = value
        return self

    def unsigned(self):
        """Set column as unsigned (for numeric types)"""
        self.attributes['unsigned'] = True
        return self

    def auto_increment(self):
        """Set column as auto increment"""
        self.attributes['auto_increment'] = True
        return self

    def first(self):
        """Place column first in table"""
        self.attributes['first'] = True
        return self

    def after(self, column: str):
        """Place column after another column"""
        self.attributes['after'] = column
        return self

    def comment(self, comment: str):
        """Add comment to column"""
        self.attributes['comment'] = comment
        return self

    def charset(self, charset: str):
        """Set character set (for string columns)"""
        self.attributes['charset'] = charset
        return self

    def collation(self, collation: str):
        """Set collation (for string columns)"""
        self.attributes['collation'] = collation
        return self


class ForeignKeyDefinition:
    """Foreign key definition with fluent interface"""

    def __init__(self, foreign_key: Dict[str, Any]):
        self.foreign_key = foreign_key

    def references(self, columns: Union[str, List[str]]):
        """Set the referenced columns"""
        if isinstance(columns, str):
            columns = [columns]
        
        if 'references' not in self.foreign_key:
            self.foreign_key['references'] = {}
        
        self.foreign_key['references']['columns'] = columns
        return self

    def on(self, table: str):
        """Set the referenced table"""
        if 'references' not in self.foreign_key:
            self.foreign_key['references'] = {}
            
        self.foreign_key['references']['table'] = table
        return self

    def on_delete(self, action: str):
        """Set the on delete action"""
        self.foreign_key['on_delete'] = action
        return self

    def on_update(self, action: str):
        """Set the on update action"""
        self.foreign_key['on_update'] = action
        return self

    def cascade_on_delete(self):
        """Set cascade on delete"""
        return self.on_delete('cascade')

    def restrict_on_delete(self):
        """Set restrict on delete"""
        return self.on_delete('restrict')

    def null_on_delete(self):
        """Set null on delete"""
        return self.on_delete('set null')