"""Database schema builder"""

from typing import Dict, Any, List, Optional, Callable
from .blueprint import Blueprint


class SchemaBuilder:
    """
    Database schema builder
    
    Provides methods for creating, modifying, and dropping database tables.
    """

    def __init__(self, connection):
        self.connection = connection
        self.grammar = connection.get_query_grammar()

    def has_table(self, table: str) -> bool:
        """Determine if the given table exists"""
        # This will be implemented per database type
        return False

    def has_column(self, table: str, column: str) -> bool:
        """Determine if the given table has the given column"""
        columns = self.get_column_listing(table)
        return column in columns

    def has_columns(self, table: str, columns: List[str]) -> bool:
        """Determine if the given table has all given columns"""
        table_columns = self.get_column_listing(table)
        return all(column in table_columns for column in columns)

    def get_column_listing(self, table: str) -> List[str]:
        """Get the column listing for a given table"""
        return self.connection.get_column_listing(table)

    def get_columns(self, table: str) -> List[Dict[str, Any]]:
        """Get detailed column information for a given table"""
        return self.connection.get_columns(table)

    def create(self, table: str, callback: Callable[[Blueprint], None]):
        """Create a new table on the schema"""
        blueprint = Blueprint(table)
        callback(blueprint)

        self._build(blueprint)

    def table(self, table: str, callback: Callable[[Blueprint], None]):
        """Modify a table on the schema"""
        blueprint = Blueprint(table)
        callback(blueprint)

        self._build(blueprint)

    def drop(self, table: str):
        """Drop a table from the schema"""
        sql = f"DROP TABLE {self.grammar.wrap_table(table)}"
        self.connection.statement(sql)

    def drop_if_exists(self, table: str):
        """Drop a table from the schema if it exists"""
        sql = f"DROP TABLE IF EXISTS {self.grammar.wrap_table(table)}"
        self.connection.statement(sql)

    def rename(self, from_table: str, to_table: str):
        """Rename a table on the schema"""
        sql = f"ALTER TABLE {self.grammar.wrap_table(from_table)} RENAME TO {self.grammar.wrap_table(to_table)}"
        self.connection.statement(sql)

    def drop_all_tables(self):
        """Drop all tables from the database"""
        # This will be implemented per database type
        raise NotImplementedError("Drop all tables not implemented for this database")

    def drop_all_views(self):
        """Drop all views from the database"""
        # This will be implemented per database type
        raise NotImplementedError("Drop all views not implemented for this database")

    def get_tables(self) -> List[str]:
        """Get all table names"""
        # This will be implemented per database type
        raise NotImplementedError("Get tables not implemented for this database")

    def _build(self, blueprint: Blueprint):
        """Execute the blueprint to build/modify the table"""
        statements = blueprint.to_sql(self.connection, self.grammar)

        for statement in statements:
            self.connection.statement(statement)

    def _compile_create(self, blueprint: Blueprint) -> str:
        """Compile a create table statement"""
        columns = []
        
        for column in blueprint.columns:
            column_sql = self._compile_column(column)
            columns.append(column_sql)

        # Add primary key
        if blueprint.primary:
            primary_columns = ', '.join([self.grammar.wrap(col) for col in blueprint.primary])
            columns.append(f"PRIMARY KEY ({primary_columns})")

        # Add unique constraints
        for unique in blueprint.unique_constraints:
            unique_columns = ', '.join([self.grammar.wrap(col) for col in unique['columns']])
            constraint_name = unique.get('name', '')
            if constraint_name:
                columns.append(f"CONSTRAINT {constraint_name} UNIQUE ({unique_columns})")
            else:
                columns.append(f"UNIQUE ({unique_columns})")

        # Add indexes (handled separately in most databases)
        
        # Add foreign keys
        for foreign_key in blueprint.foreign_keys:
            fk_sql = self._compile_foreign_key(foreign_key)
            columns.append(fk_sql)

        table_sql = f"CREATE TABLE {self.grammar.wrap_table(blueprint.table)} (\n"
        table_sql += ',\n'.join(f"    {col}" for col in columns)
        table_sql += "\n)"

        return table_sql

    def _compile_column(self, column: Dict[str, Any]) -> str:
        """Compile a column definition"""
        name = self.grammar.wrap(column['name'])
        type_sql = self._compile_column_type(column)
        
        sql = f"{name} {type_sql}"
        
        # Add modifiers
        if column.get('nullable', True) is False:
            sql += " NOT NULL"
            
        if column.get('default') is not None:
            default_value = column['default']
            if isinstance(default_value, str):
                default_value = f"'{default_value}'"
            sql += f" DEFAULT {default_value}"
            
        if column.get('auto_increment', False):
            sql += " AUTO_INCREMENT"
            
        return sql

    def _compile_column_type(self, column: Dict[str, Any]) -> str:
        """Compile column type"""
        column_type = column['type'].upper()
        
        if column_type == 'STRING':
            length = column.get('length', 255)
            return f"VARCHAR({length})"
        elif column_type == 'TEXT':
            return "TEXT"
        elif column_type == 'INTEGER':
            return "INTEGER"
        elif column_type == 'BIGINTEGER':
            return "BIGINT"
        elif column_type == 'BOOLEAN':
            return "BOOLEAN"
        elif column_type == 'DECIMAL':
            precision = column.get('precision', 8)
            scale = column.get('scale', 2)
            return f"DECIMAL({precision},{scale})"
        elif column_type == 'FLOAT':
            return "FLOAT"
        elif column_type == 'DOUBLE':
            return "DOUBLE"
        elif column_type == 'DATE':
            return "DATE"
        elif column_type == 'DATETIME':
            return "DATETIME"
        elif column_type == 'TIMESTAMP':
            return "TIMESTAMP"
        elif column_type == 'TIME':
            return "TIME"
        elif column_type == 'JSON':
            return "JSON"
        else:
            return column_type

    def _compile_foreign_key(self, foreign_key: Dict[str, Any]) -> str:
        """Compile foreign key constraint"""
        local_columns = ', '.join([self.grammar.wrap(col) for col in foreign_key['columns']])
        foreign_table = self.grammar.wrap_table(foreign_key['references']['table'])
        foreign_columns = ', '.join([self.grammar.wrap(col) for col in foreign_key['references']['columns']])
        
        constraint_name = foreign_key.get('name', '')
        
        sql = ""
        if constraint_name:
            sql += f"CONSTRAINT {constraint_name} "
            
        sql += f"FOREIGN KEY ({local_columns}) REFERENCES {foreign_table} ({foreign_columns})"
        
        if foreign_key.get('on_delete'):
            sql += f" ON DELETE {foreign_key['on_delete'].upper()}"
            
        if foreign_key.get('on_update'):
            sql += f" ON UPDATE {foreign_key['on_update'].upper()}"
            
        return sql