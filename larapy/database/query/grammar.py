"""SQL Grammar base class"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union


class Grammar(ABC):
    """
    Base SQL grammar class
    
    Handles the compilation of query builder components into SQL.
    """

    # Query components
    select_components = [
        'aggregate', 'columns', 'from', 'joins', 'wheres',
        'groups', 'havings', 'orders', 'limit', 'offset', 'unions'
    ]

    # Operators
    operators = [
        '=', '<', '>', '<=', '>=', '<>', '!=', '<=>',
        'like', 'like binary', 'not like', 'ilike',
        '&', '|', '^', '<<', '>>',
        'rlike', 'not rlike', 'regexp', 'not regexp',
        '~', '~*', '!~', '!~*', 'similar to',
        'not similar to', 'not ilike', '~~*', '!~~*',
    ]

    def compile_select(self, query) -> str:
        """Compile a select query"""
        sql_parts = []
        
        for component in self.select_components:
            method = f'compile_{component}'
            if hasattr(self, method) and hasattr(query, component):
                compiled = getattr(self, method)(query, getattr(query, component))
                if compiled:
                    sql_parts.append(compiled)
                    
        return ' '.join(sql_parts)

    def compile_insert(self, query, values: Dict[str, Any]) -> str:
        """Compile an insert query"""
        table = self.wrap_table(query.from_clause)
        columns = ', '.join([self.wrap(column) for column in values.keys()])
        parameters = ', '.join(['?' for _ in values])
        
        return f"INSERT INTO {table} ({columns}) VALUES ({parameters})"

    def compile_update(self, query, values: Dict[str, Any]) -> str:
        """Compile an update query"""
        table = self.wrap_table(query.from_clause)
        
        columns = []
        for column in values.keys():
            columns.append(f"{self.wrap(column)} = ?")
            
        columns_sql = ', '.join(columns)
        
        where = self.compile_wheres(query, query.wheres)
        
        sql = f"UPDATE {table} SET {columns_sql}"
        if where:
            sql += f" {where}"
            
        return sql

    def compile_delete(self, query) -> str:
        """Compile a delete query"""
        table = self.wrap_table(query.from_clause)
        where = self.compile_wheres(query, query.wheres)
        
        sql = f"DELETE FROM {table}"
        if where:
            sql += f" {where}"
            
        return sql

    def compile_columns(self, query, columns) -> str:
        """Compile the select columns"""
        if not columns:
            return "SELECT *"
            
        select = "SELECT "
        if query.distinct:
            select += "DISTINCT "
            
        column_parts = []
        for column in columns:
            if isinstance(column, dict) and column.get('type') == 'raw':
                column_parts.append(column['expression'])
            else:
                column_parts.append(self.wrap(column))
                
        return select + ', '.join(column_parts)

    def compile_from(self, query, table) -> str:
        """Compile the from clause"""
        if isinstance(table, dict) and table.get('type') == 'raw':
            return f"FROM {table['expression']}"
        return f"FROM {self.wrap_table(table)}"

    def compile_joins(self, query, joins) -> str:
        """Compile join clauses"""
        if not joins:
            return ""
            
        join_parts = []
        for join in joins:
            join_type = join['type'].upper()
            table = self.wrap_table(join['table'])
            
            # Compile join conditions
            conditions = []
            for clause in join['clauses']:
                if clause['type'] == 'basic':
                    left = self.wrap(clause['first'])
                    operator = clause['operator']
                    right = self.wrap(clause['second'])
                    conditions.append(f"{left} {operator} {right}")
                    
            on_clause = ' AND '.join(conditions)
            join_parts.append(f"{join_type} JOIN {table} ON {on_clause}")
            
        return ' '.join(join_parts)

    def compile_wheres(self, query, wheres) -> str:
        """Compile where clauses"""
        if not wheres:
            return ""
            
        where_parts = []
        for i, where in enumerate(wheres):
            boolean = 'AND' if i > 0 else 'WHERE'
            if where.get('boolean') == 'or':
                boolean = 'OR'
                
            method = f"where_{where['type']}"
            if hasattr(self, method):
                compiled = getattr(self, method)(query, where)
                where_parts.append(f"{boolean} {compiled}")
                
        return ' '.join(where_parts)

    def where_basic(self, query, where) -> str:
        """Compile a basic where clause"""
        column = self.wrap(where['column'])
        operator = where['operator']
        return f"{column} {operator} ?"

    def where_in(self, query, where) -> str:
        """Compile a where in clause"""
        column = self.wrap(where['column'])
        values = ', '.join(['?' for _ in where['values']])
        operator = 'NOT IN' if where.get('not', False) else 'IN'
        return f"{column} {operator} ({values})"

    def where_null(self, query, where) -> str:
        """Compile a where null clause"""
        column = self.wrap(where['column'])
        operator = 'IS NOT NULL' if where.get('not', False) else 'IS NULL'
        return f"{column} {operator}"

    def where_between(self, query, where) -> str:
        """Compile a where between clause"""
        column = self.wrap(where['column'])
        operator = 'NOT BETWEEN' if where.get('not', False) else 'BETWEEN'
        return f"{column} {operator} ? AND ?"

    def where_exists(self, query, where) -> str:
        """Compile a where exists clause"""
        operator = 'NOT EXISTS' if where.get('not', False) else 'EXISTS'
        subquery = self.compile_select(where['query'])
        return f"{operator} ({subquery})"

    def compile_groups(self, query, groups) -> str:
        """Compile group by clauses"""
        if not groups:
            return ""
            
        group_parts = []
        for group in groups:
            if isinstance(group, dict) and group.get('type') == 'raw':
                group_parts.append(group['expression'])
            else:
                group_parts.append(self.wrap(group))
                
        return f"GROUP BY {', '.join(group_parts)}"

    def compile_havings(self, query, havings) -> str:
        """Compile having clauses"""
        if not havings:
            return ""
            
        having_parts = []
        for i, having in enumerate(havings):
            boolean = 'AND' if i > 0 else 'HAVING'
            if having.get('boolean') == 'or':
                boolean = 'OR'
                
            column = self.wrap(having['column'])
            operator = having['operator']
            having_parts.append(f"{boolean} {column} {operator} ?")
            
        return ' '.join(having_parts)

    def compile_orders(self, query, orders) -> str:
        """Compile order by clauses"""
        if not orders:
            return ""
            
        order_parts = []
        for order in orders:
            if isinstance(order, dict) and order.get('type') == 'raw':
                order_parts.append(order['expression'])
            else:
                column = self.wrap(order['column'])
                direction = order['direction'].upper()
                order_parts.append(f"{column} {direction}")
                
        return f"ORDER BY {', '.join(order_parts)}"

    def compile_limit(self, query, limit) -> str:
        """Compile limit clause"""
        if limit is None:
            return ""
        return f"LIMIT {limit}"

    def compile_offset(self, query, offset) -> str:
        """Compile offset clause"""
        if offset is None:
            return ""
        return f"OFFSET {offset}"

    def compile_unions(self, query, unions) -> str:
        """Compile union clauses"""
        if not unions:
            return ""
            
        union_parts = []
        for union in unions:
            union_type = 'UNION ALL' if union.get('all', False) else 'UNION'
            subquery = self.compile_select(union['query'])
            union_parts.append(f"{union_type} {subquery}")
            
        return ' '.join(union_parts)

    def compile_aggregate(self, query, aggregate) -> str:
        """Compile aggregate function"""
        if not aggregate:
            return ""
            
        function = aggregate['function'].upper()
        column = '*' if aggregate['columns'] == '*' else self.wrap(aggregate['columns'])
        
        return f"SELECT {function}({column}) AS aggregate"

    def wrap(self, value: str) -> str:
        """Wrap a value in keyword identifiers"""
        if value == '*':
            return value
            
        # Remove table prefix if present
        if '.' in value:
            parts = value.split('.')
            return '.'.join([self.wrap_value(part) for part in parts])
            
        return self.wrap_value(value)

    def wrap_value(self, value: str) -> str:
        """Wrap a single value"""
        return f'`{value}`'

    def wrap_table(self, table: str) -> str:
        """Wrap a table name"""
        return self.wrap(table)

    def parameter(self, value: Any) -> str:
        """Get the appropriate query parameter place-holder"""
        return '?'

    def is_expression(self, value) -> bool:
        """Determine if the given value is a raw expression"""
        return isinstance(value, dict) and value.get('type') == 'raw'