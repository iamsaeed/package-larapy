"""Enhanced Query Builder with Laravel-like functionality"""

from typing import Any, Dict, List, Optional, Union, Callable
import copy


class QueryBuilder:
    """
    Laravel-style Query Builder with full feature support
    """

    def __init__(self, connection, grammar, processor, table: str = None):
        self.connection = connection
        self.grammar = grammar
        self.processor = processor
        
        # Query components
        self.aggregate = None
        self.columns = []
        self.distinct = False
        self.from_clause = table
        self.joins = []
        self.wheres = []
        self.groups = []
        self.havings = []
        self.orders = []
        self.limit_value = None
        self.offset_value = None
        self.unions = []
        self.bindings = {
            'select': [],
            'from': [],
            'join': [],
            'where': [],
            'having': [],
            'order': [],
            'union': []
        }

    def select(self, *columns) -> 'QueryBuilder':
        """Set the columns to select"""
        if columns:
            self.columns.extend(columns)
        else:
            self.columns = ['*']
        return self

    def select_raw(self, expression: str, bindings: List = None) -> 'QueryBuilder':
        """Add a raw select expression"""
        self.columns.append({'type': 'raw', 'expression': expression})
        self.add_binding(bindings or [], 'select')
        return self

    def distinct(self, *columns) -> 'QueryBuilder':
        """Force the query to only return distinct results"""
        self.distinct = True
        if columns:
            self.columns.extend(columns)
        return self

    def from_table(self, table: str, as_alias: str = None) -> 'QueryBuilder':
        """Set the table for the query"""
        if as_alias:
            self.from_clause = f"{table} AS {as_alias}"
        else:
            self.from_clause = table
        return self

    def from_raw(self, expression: str, bindings: List = None) -> 'QueryBuilder':
        """Set a raw from clause"""
        self.from_clause = {'type': 'raw', 'expression': expression}
        self.add_binding(bindings or [], 'from')
        return self

    def join(self, table: str, first: str, operator: str = None, second: str = None,
             join_type: str = 'inner', where: bool = False) -> 'QueryBuilder':
        """Add a join clause to the query"""
        
        # Handle closure-based joins later
        join_clause = {
            'type': join_type,
            'table': table,
            'clauses': []
        }
        
        if operator is None:
            operator = '='
            
        if second is None:
            second = operator
            operator = '='
            
        join_clause['clauses'].append({
            'type': 'basic',
            'first': first,
            'operator': operator,
            'second': second,
            'boolean': 'and'
        })
        
        self.joins.append(join_clause)
        return self

    def left_join(self, table: str, first: str, operator: str = None, second: str = None) -> 'QueryBuilder':
        """Add a left join to the query"""
        return self.join(table, first, operator, second, 'left')

    def right_join(self, table: str, first: str, operator: str = None, second: str = None) -> 'QueryBuilder':
        """Add a right join to the query"""
        return self.join(table, first, operator, second, 'right')

    def cross_join(self, table: str) -> 'QueryBuilder':
        """Add a cross join to the query"""
        self.joins.append({
            'type': 'cross',
            'table': table,
            'clauses': []
        })
        return self

    def where(self, column: str, operator: str = None, value: Any = None,
              boolean: str = 'and') -> 'QueryBuilder':
        """Add a where clause to the query"""
        
        # Handle different parameter combinations
        if operator is None:
            raise ValueError("Operator cannot be None")
            
        if value is None:
            value = operator
            operator = '='
            
        # Validate operator
        if operator not in self.grammar.operators:
            raise ValueError(f"Invalid operator: {operator}")
            
        self.wheres.append({
            'type': 'basic',
            'column': column,
            'operator': operator,
            'value': value,
            'boolean': boolean
        })
        
        self.add_binding(value, 'where')
        return self

    def or_where(self, column: str, operator: str = None, value: Any = None) -> 'QueryBuilder':
        """Add an or where clause to the query"""
        return self.where(column, operator, value, 'or')

    def where_in(self, column: str, values: List[Any], boolean: str = 'and',
                 not_in: bool = False) -> 'QueryBuilder':
        """Add a where in clause to the query"""
        self.wheres.append({
            'type': 'in',
            'column': column,
            'values': values,
            'boolean': boolean,
            'not': not_in
        })
        
        self.add_binding(values, 'where')
        return self

    def where_not_in(self, column: str, values: List[Any], boolean: str = 'and') -> 'QueryBuilder':
        """Add a where not in clause to the query"""
        return self.where_in(column, values, boolean, True)

    def where_null(self, column: str, boolean: str = 'and', not_null: bool = False) -> 'QueryBuilder':
        """Add a where null clause to the query"""
        self.wheres.append({
            'type': 'null',
            'column': column,
            'boolean': boolean,
            'not': not_null
        })
        return self

    def where_not_null(self, column: str, boolean: str = 'and') -> 'QueryBuilder':
        """Add a where not null clause to the query"""
        return self.where_null(column, boolean, True)

    def where_between(self, column: str, values: List[Any], boolean: str = 'and',
                      not_between: bool = False) -> 'QueryBuilder':
        """Add a where between clause to the query"""
        if len(values) != 2:
            raise ValueError("Between requires exactly 2 values")
            
        self.wheres.append({
            'type': 'between',
            'column': column,
            'values': values,
            'boolean': boolean,
            'not': not_between
        })
        
        self.add_binding(values, 'where')
        return self

    def where_not_between(self, column: str, values: List[Any], boolean: str = 'and') -> 'QueryBuilder':
        """Add a where not between clause to the query"""
        return self.where_between(column, values, boolean, True)

    def where_exists(self, callback: Callable, boolean: str = 'and', not_exists: bool = False) -> 'QueryBuilder':
        """Add a where exists clause to the query"""
        sub_query = self._create_sub_query()
        callback(sub_query)
        
        self.wheres.append({
            'type': 'exists',
            'query': sub_query,
            'boolean': boolean,
            'not': not_exists
        })
        
        self.add_binding(sub_query.get_bindings(), 'where')
        return self

    def where_not_exists(self, callback: Callable, boolean: str = 'and') -> 'QueryBuilder':
        """Add a where not exists clause to the query"""
        return self.where_exists(callback, boolean, True)

    def group_by(self, *groups) -> 'QueryBuilder':
        """Add a group by clause to the query"""
        self.groups.extend(groups)
        return self

    def having(self, column: str, operator: str = None, value: Any = None,
               boolean: str = 'and') -> 'QueryBuilder':
        """Add a having clause to the query"""
        
        if operator is None:
            raise ValueError("Operator cannot be None")
            
        if value is None:
            value = operator
            operator = '='
            
        self.havings.append({
            'column': column,
            'operator': operator,
            'value': value,
            'boolean': boolean
        })
        
        self.add_binding(value, 'having')
        return self

    def order_by(self, column: str, direction: str = 'asc') -> 'QueryBuilder':
        """Add an order by clause to the query"""
        direction = direction.lower()
        if direction not in ['asc', 'desc']:
            direction = 'asc'
            
        self.orders.append({
            'column': column,
            'direction': direction
        })
        return self

    def order_by_desc(self, column: str) -> 'QueryBuilder':
        """Add a descending order by clause to the query"""
        return self.order_by(column, 'desc')

    def latest(self, column: str = 'created_at') -> 'QueryBuilder':
        """Add an order by clause for the latest records"""
        return self.order_by(column, 'desc')

    def oldest(self, column: str = 'created_at') -> 'QueryBuilder':
        """Add an order by clause for the oldest records"""
        return self.order_by(column, 'asc')

    def limit(self, value: int) -> 'QueryBuilder':
        """Set the limit for the query"""
        self.limit_value = max(0, value)
        return self

    def take(self, value: int) -> 'QueryBuilder':
        """Alias for limit"""
        return self.limit(value)

    def offset(self, value: int) -> 'QueryBuilder':
        """Set the offset for the query"""
        self.offset_value = max(0, value)
        return self

    def skip(self, value: int) -> 'QueryBuilder':
        """Alias for offset"""
        return self.offset(value)

    def for_page(self, page: int, per_page: int = 15) -> 'QueryBuilder':
        """Set the limit and offset for a given page"""
        return self.offset((page - 1) * per_page).limit(per_page)

    def union(self, query, all_union: bool = False) -> 'QueryBuilder':
        """Add a union statement to the query"""
        self.unions.append({
            'query': query,
            'all': all_union
        })
        self.add_binding(query.get_bindings(), 'union')
        return self

    def union_all(self, query) -> 'QueryBuilder':
        """Add a union all statement to the query"""
        return self.union(query, True)

    # Execution methods
    def get(self, columns: List[str] = None) -> List[Dict[str, Any]]:
        """Execute the query and get all results"""
        if columns:
            self.select(*columns)
        
        sql, bindings = self.to_sql()
        return self.connection.select(sql, bindings)

    def first(self, columns: List[str] = None) -> Optional[Dict[str, Any]]:
        """Execute the query and get the first result"""
        results = self.limit(1).get(columns)
        return results[0] if results else None

    def find(self, id: Any, columns: List[str] = None) -> Optional[Dict[str, Any]]:
        """Find a record by its primary key"""
        if columns is None:
            columns = ['*']
        return self.select(*columns).where('id', id).first()

    def value(self, column: str) -> Any:
        """Get a single column's value from the first result"""
        result = self.first([column])
        return result[column] if result else None

    def pluck(self, column: str, key: str = None) -> Union[List[Any], Dict[str, Any]]:
        """Get a list of column values"""
        columns = [column]
        if key:
            columns.append(key)
            
        results = self.get(columns)
        
        if key:
            return {row[key]: row[column] for row in results}
        else:
            return [row[column] for row in results]

    def count(self, columns: str = '*') -> int:
        """Get the count of results"""
        return self.aggregate('count', columns)

    def min(self, column: str) -> Any:
        """Get the minimum value of a column"""
        return self.aggregate('min', column)

    def max(self, column: str) -> Any:
        """Get the maximum value of a column"""
        return self.aggregate('max', column)

    def sum(self, column: str) -> Any:
        """Get the sum of a column"""
        return self.aggregate('sum', column)

    def avg(self, column: str) -> Any:
        """Get the average value of a column"""
        return self.aggregate('avg', column)

    def aggregate(self, function: str, column: str = '*') -> Any:
        """Execute an aggregate function"""
        original_columns = self.columns[:]
        
        self.aggregate = {
            'function': function,
            'columns': column
        }
        
        sql, bindings = self.to_sql()
        result = self.connection.select(sql, bindings)
        
        # Restore original columns
        self.columns = original_columns
        self.aggregate = None
        
        return result[0]['aggregate'] if result else None

    def exists(self) -> bool:
        """Determine if any rows exist for the current query"""
        return self.count() > 0

    def doesnt_exist(self) -> bool:
        """Determine if no rows exist for the current query"""
        return not self.exists()

    def chunk(self, count: int, callback: Callable) -> bool:
        """Chunk the results of the query"""
        page = 1
        
        while True:
            results = self.for_page(page, count).get()
            
            if not results:
                break
                
            if callback(results) is False:
                return False
                
            page += 1
            
        return True

    def paginate(self, per_page: int = 15, page: int = 1) -> Dict[str, Any]:
        """Paginate the query results"""
        # Get total count
        total = self.count()
        
        # Calculate pagination info
        last_page = max(1, (total + per_page - 1) // per_page)
        from_record = (page - 1) * per_page + 1 if total > 0 else None
        to_record = min(page * per_page, total) if total > 0 else None
        
        # Get results for current page
        results = self.for_page(page, per_page).get()
        
        return {
            'data': results,
            'current_page': page,
            'last_page': last_page,
            'per_page': per_page,
            'total': total,
            'from': from_record,
            'to': to_record
        }

    # Modification methods
    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[bool, int]:
        """Insert new records into the table"""
        if isinstance(data, list):
            return self.insert_multiple(data)
            
        sql = self.grammar.compile_insert(self, data)
        bindings = list(data.values())
        
        result = self.connection.insert(sql, bindings)
        return result

    def insert_multiple(self, data: List[Dict[str, Any]]) -> bool:
        """Insert multiple records"""
        if not data:
            return True
            
        # All records should have the same keys
        columns = list(data[0].keys())
        values = []
        
        for record in data:
            values.extend(record.values())
            
        # Build SQL for multiple inserts
        table = self.grammar.wrap_table(self.from_clause)
        columns_sql = ', '.join([self.grammar.wrap(col) for col in columns])
        
        placeholders = ', '.join(['?' for _ in columns])
        values_sql = ', '.join([f"({placeholders})" for _ in data])
        
        sql = f"INSERT INTO {table} ({columns_sql}) VALUES {values_sql}"
        
        return self.connection.insert(sql, values)

    def insert_get_id(self, data: Dict[str, Any], sequence: str = None) -> int:
        """Insert a record and get the ID"""
        sql = self.grammar.compile_insert(self, data)
        bindings = list(data.values())
        
        return self.processor.process_insert_get_id(
            self, sql, bindings, sequence
        )

    def update(self, data: Dict[str, Any]) -> int:
        """Update records in the table"""
        sql = self.grammar.compile_update(self, data)
        bindings = list(data.values()) + self.get_bindings()
        
        return self.connection.update(sql, bindings)

    def increment(self, column: str, amount: int = 1, extra: Dict[str, Any] = None) -> int:
        """Increment a column's value"""
        data = {column: f"{self.grammar.wrap(column)} + {amount}"}
        if extra:
            data.update(extra)
        return self.update(data)

    def decrement(self, column: str, amount: int = 1, extra: Dict[str, Any] = None) -> int:
        """Decrement a column's value"""
        return self.increment(column, -amount, extra)

    def delete(self, id: Any = None) -> int:
        """Delete records from the table"""
        if id is not None:
            self.where('id', id)
            
        sql = self.grammar.compile_delete(self)
        return self.connection.delete(sql, self.get_bindings())

    def truncate(self) -> bool:
        """Truncate the table"""
        sql = f"TRUNCATE TABLE {self.grammar.wrap_table(self.from_clause)}"
        return self.connection.statement(sql)

    # Helper methods
    def to_sql(self) -> tuple:
        """Get the SQL representation of the query"""
        sql = self.grammar.compile_select(self)
        bindings = self.get_bindings()
        return sql, bindings

    def get_bindings(self) -> List[Any]:
        """Get the current query bindings"""
        all_bindings = []
        for binding_type in ['select', 'from', 'join', 'where', 'having', 'order', 'union']:
            all_bindings.extend(self.bindings[binding_type])
        return all_bindings

    def add_binding(self, value: Any, type_: str = 'where'):
        """Add a binding to the query"""
        if not isinstance(value, list):
            value = [value]
            
        for val in value:
            if val is not None:
                self.bindings[type_].append(val)

    def clone(self) -> 'QueryBuilder':
        """Create a copy of the query"""
        return copy.deepcopy(self)

    def _raw(self, expression: str):
        """Create a raw expression"""
        return {'type': 'raw', 'expression': expression}

    def _create_sub_query(self) -> 'QueryBuilder':
        """Create a new query for subqueries"""
        return QueryBuilder(self.connection, self.grammar, self.processor)