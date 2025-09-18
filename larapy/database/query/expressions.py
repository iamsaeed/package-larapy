"""Raw expressions for database queries"""

from typing import Any, Union, Dict, List


class Expression:
    """Represents a raw database expression"""
    
    def __init__(self, value: str):
        self.value = value

    def get_value(self) -> str:
        """Get the raw expression value"""
        return self.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Expression('{self.value}')"


class Raw(Expression):
    """Raw SQL expression"""
    
    def __init__(self, sql: str, bindings: List[Any] = None):
        super().__init__(sql)
        self.bindings = bindings or []

    def get_bindings(self) -> List[Any]:
        """Get the parameter bindings for this raw expression"""
        return self.bindings


def raw(sql: str, bindings: List[Any] = None) -> Raw:
    """Create a raw SQL expression"""
    return Raw(sql, bindings)


class QueryExpression:
    """Helper class for building complex query expressions"""
    
    @staticmethod
    def case(column: str = None) -> 'CaseExpression':
        """Create a CASE expression"""
        return CaseExpression(column)

    @staticmethod
    def exists(query) -> Raw:
        """Create an EXISTS expression"""
        if hasattr(query, 'to_sql'):
            sql, bindings = query.to_sql()
            return Raw(f"EXISTS ({sql})", bindings)
        return Raw(f"EXISTS ({query})")

    @staticmethod
    def not_exists(query) -> Raw:
        """Create a NOT EXISTS expression"""
        if hasattr(query, 'to_sql'):
            sql, bindings = query.to_sql()
            return Raw(f"NOT EXISTS ({sql})", bindings)
        return Raw(f"NOT EXISTS ({query})")

    @staticmethod
    def concat(*columns) -> Raw:
        """Create a CONCAT expression"""
        column_list = ', '.join(str(col) for col in columns)
        return Raw(f"CONCAT({column_list})")

    @staticmethod
    def coalesce(*columns) -> Raw:
        """Create a COALESCE expression"""
        column_list = ', '.join(str(col) for col in columns)
        return Raw(f"COALESCE({column_list})")

    @staticmethod
    def count(column: str = '*') -> Raw:
        """Create a COUNT expression"""
        return Raw(f"COUNT({column})")

    @staticmethod
    def sum(column: str) -> Raw:
        """Create a SUM expression"""
        return Raw(f"SUM({column})")

    @staticmethod
    def avg(column: str) -> Raw:
        """Create an AVG expression"""
        return Raw(f"AVG({column})")

    @staticmethod
    def max(column: str) -> Raw:
        """Create a MAX expression"""
        return Raw(f"MAX({column})")

    @staticmethod
    def min(column: str) -> Raw:
        """Create a MIN expression"""
        return Raw(f"MIN({column})")

    @staticmethod
    def date_format(column: str, format_str: str) -> Raw:
        """Create a DATE_FORMAT expression (MySQL)"""
        return Raw(f"DATE_FORMAT({column}, '{format_str}')")

    @staticmethod
    def strftime(format_str: str, column: str) -> Raw:
        """Create a strftime expression (SQLite)"""
        return Raw(f"strftime('{format_str}', {column})")

    @staticmethod
    def extract(part: str, column: str) -> Raw:
        """Create an EXTRACT expression (PostgreSQL)"""
        return Raw(f"EXTRACT({part} FROM {column})")


class CaseExpression:
    """Builder for CASE expressions"""
    
    def __init__(self, column: str = None):
        self.column = column
        self.conditions = []
        self.else_value = None

    def when(self, condition: Union[str, Dict], value: Any = None) -> 'CaseExpression':
        """Add a WHEN condition"""
        if isinstance(condition, dict):
            # Multiple conditions as dict
            for col, val in condition.items():
                self.conditions.append((f"{col} = ?", [val], value))
        elif value is not None:
            # Simple condition with value
            if self.column:
                self.conditions.append((f"{self.column} = ?", [condition], value))
            else:
                self.conditions.append((condition, [], value))
        else:
            # Raw condition
            self.conditions.append((condition, [], None))
        
        return self

    def else_(self, value: Any) -> 'CaseExpression':
        """Set the ELSE value"""
        self.else_value = value
        return self

    def end(self) -> Raw:
        """Build the final CASE expression"""
        parts = ["CASE"]
        bindings = []
        
        if self.column:
            parts.append(self.column)
        
        for condition, condition_bindings, value in self.conditions:
            parts.append(f"WHEN {condition}")
            bindings.extend(condition_bindings)
            
            if value is not None:
                parts.append(f"THEN ?")
                bindings.append(value)
        
        if self.else_value is not None:
            parts.append(f"ELSE ?")
            bindings.append(self.else_value)
        
        parts.append("END")
        
        return Raw(" ".join(parts), bindings)


class SubQuery:
    """Represents a subquery expression"""
    
    def __init__(self, query, alias: str = None):
        self.query = query
        self.alias = alias

    def as_(self, alias: str) -> 'SubQuery':
        """Set an alias for the subquery"""
        self.alias = alias
        return self

    def to_raw(self) -> Raw:
        """Convert to a raw expression"""
        if hasattr(self.query, 'to_sql'):
            sql, bindings = self.query.to_sql()
        else:
            sql = str(self.query)
            bindings = []
        
        if self.alias:
            sql = f"({sql}) AS {self.alias}"
        else:
            sql = f"({sql})"
        
        return Raw(sql, bindings)


class JsonExpression:
    """Helper for JSON operations"""
    
    @staticmethod
    def extract(column: str, path: str, database_type: str = 'mysql') -> Raw:
        """Extract value from JSON column"""
        if database_type.lower() == 'mysql':
            return Raw(f"JSON_EXTRACT({column}, '$.{path}')")
        elif database_type.lower() == 'postgresql':
            return Raw(f"{column}->'{path}'")
        elif database_type.lower() == 'sqlite':
            return Raw(f"JSON_EXTRACT({column}, '$.{path}')")
        else:
            return Raw(f"JSON_EXTRACT({column}, '$.{path}')")

    @staticmethod
    def contains(column: str, value: Any, database_type: str = 'mysql') -> Raw:
        """Check if JSON contains value"""
        if database_type.lower() == 'mysql':
            return Raw(f"JSON_CONTAINS({column}, ?)", [value])
        elif database_type.lower() == 'postgresql':
            return Raw(f"{column} @> ?", [value])
        else:
            return Raw(f"JSON_EXTRACT({column}, '$') LIKE ?", [f'%{value}%'])

    @staticmethod
    def length(column: str, path: str = None, database_type: str = 'mysql') -> Raw:
        """Get length of JSON array or object"""
        if path:
            if database_type.lower() == 'mysql':
                return Raw(f"JSON_LENGTH(JSON_EXTRACT({column}, '$.{path}'))")
            elif database_type.lower() == 'postgresql':
                return Raw(f"JSON_ARRAY_LENGTH({column}->'{path}')")
            else:
                return Raw(f"JSON_ARRAY_LENGTH(JSON_EXTRACT({column}, '$.{path}'))")
        else:
            if database_type.lower() == 'mysql':
                return Raw(f"JSON_LENGTH({column})")
            elif database_type.lower() == 'postgresql':
                return Raw(f"JSON_ARRAY_LENGTH({column})")
            else:
                return Raw(f"JSON_ARRAY_LENGTH({column})")


# Convenience functions
def case(column: str = None) -> CaseExpression:
    """Create a CASE expression"""
    return QueryExpression.case(column)


def exists(query) -> Raw:
    """Create an EXISTS expression"""
    return QueryExpression.exists(query)


def not_exists(query) -> Raw:
    """Create a NOT EXISTS expression"""
    return QueryExpression.not_exists(query)


def subquery(query, alias: str = None) -> SubQuery:
    """Create a subquery"""
    return SubQuery(query, alias)