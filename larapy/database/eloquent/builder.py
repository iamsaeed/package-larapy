"""Eloquent Builder for model-specific queries"""

from typing import Any, Dict, List, Optional, Union, Callable
from ..query.builder import QueryBuilder


class Builder(QueryBuilder):
    """
    Eloquent Query Builder for model-specific operations
    """

    def __init__(self, query: QueryBuilder, model=None):
        """Initialize the Eloquent builder"""
        super().__init__(
            query.connection,
            query.grammar,
            query.processor
        )
        
        # Copy the query state
        self._select = query._select.copy()
        self._from = query._from
        self._joins = query._joins.copy()
        self._wheres = query._wheres.copy()
        self._groups = query._groups.copy()
        self._havings = query._havings.copy()
        self._orders = query._orders.copy()
        self._limit_value = query._limit_value
        self._offset_value = query._offset_value
        self._unions = query._unions.copy()
        self._bindings = query._bindings.copy()
        
        self.model = model
        self._eager_load = {}
        self._removed_scopes = []
        self._local_macros = {}
        self._global_macros = {}

    def with_(self, *relations) -> 'Builder':
        """Set the relationships that should be eager loaded"""
        if len(relations) == 1 and isinstance(relations[0], dict):
            # Handle dictionary format: {'relation': constraints}
            for relation, constraints in relations[0].items():
                self._eager_load[relation] = constraints
        else:
            # Handle string format
            for relation in relations:
                if isinstance(relation, str):
                    self._eager_load[relation] = None
                elif isinstance(relation, dict):
                    for key, constraints in relation.items():
                        self._eager_load[key] = constraints

        return self

    def without(self, *relations) -> 'Builder':
        """Prevent the specified relations from being eager loaded"""
        for relation in relations:
            if relation in self._eager_load:
                del self._eager_load[relation]

        return self

    def with_only(self, *relations) -> 'Builder':
        """Set the relationships that should be eager loaded, clearing any existing"""
        self._eager_load = {}
        return self.with_(*relations)

    def with_count(self, *relations) -> 'Builder':
        """Add subselect queries to count the relations"""
        for relation in relations:
            if isinstance(relation, str):
                # Add count column
                self.select_sub(
                    self._get_relation_count_query(relation),
                    f"{relation}_count"
                )
            elif isinstance(relation, dict):
                for key, constraints in relation.items():
                    self.select_sub(
                        self._get_relation_count_query(key, constraints),
                        f"{key}_count"
                    )

        return self

    def has(self, relation: str, operator: str = '>=', count: int = 1, 
            boolean: str = 'and', callback: Callable = None) -> 'Builder':
        """Add a relationship count/exists condition to the query"""
        if callable(operator):
            callback = operator
            operator = '>='
            count = 1

        # Get the relation instance
        relation_instance = self.model.get_relation(relation)
        if not relation_instance:
            raise ValueError(f"Relation '{relation}' not found on model")

        # Build the has query
        has_query = relation_instance.get_relation_exists_query(
            self, self, operator, count
        )

        if callback:
            callback(has_query)

        return self.add_where_exists_query(has_query, boolean)

    def has_not(self, relation: str, boolean: str = 'and', 
                callback: Callable = None) -> 'Builder':
        """Add a relationship count/exists condition to the query"""
        return self.has(relation, '<', 1, boolean, callback)

    def where_has(self, relation: str, callback: Callable = None, 
                  operator: str = '>=', count: int = 1) -> 'Builder':
        """Add a relationship count/exists condition to the query with where"""
        return self.has(relation, operator, count, 'and', callback)

    def where_has_not(self, relation: str, callback: Callable = None) -> 'Builder':
        """Add a relationship count/exists condition to the query with where not"""
        return self.has_not(relation, 'and', callback)

    def or_has(self, relation: str, operator: str = '>=', count: int = 1) -> 'Builder':
        """Add an "or where" relationship count/exists condition"""
        return self.has(relation, operator, count, 'or')

    def or_has_not(self, relation: str) -> 'Builder':
        """Add an "or where not" relationship count/exists condition"""
        return self.has_not(relation, 'or')

    def where_belongs_to(self, related, column: str = None) -> 'Builder':
        """Add a polymorphic relationship condition to the query"""
        if column is None:
            column = related.get_foreign_key()

        return self.where(column, related.get_key())

    def where_morphed_to(self, relation: str, model, boolean: str = 'and') -> 'Builder':
        """Add a polymorphic relationship condition to the query"""
        # This would handle polymorphic relationships
        # For now, just return self
        return self

    def scopes(self, *scopes) -> 'Builder':
        """Apply the given scopes to the current builder instance"""
        for scope in scopes:
            if isinstance(scope, str) and hasattr(self.model, f'scope_{scope}'):
                scope_method = getattr(self.model, f'scope_{scope}')
                scope_method(self)
            elif callable(scope):
                scope(self)

        return self

    def apply_scopes(self) -> 'Builder':
        """Apply all global scopes to the builder"""
        if not self.model:
            return self

        # Apply global scopes
        for scope in getattr(self.model, '_global_scopes', []):
            scope.apply(self, self.model)

        return self

    def without_global_scope(self, scope) -> 'Builder':
        """Remove a global scope from the builder"""
        if isinstance(scope, str):
            self._removed_scopes.append(scope)
        else:
            self._removed_scopes.append(scope.__class__.__name__)

        return self

    def without_global_scopes(self, scopes: List = None) -> 'Builder':
        """Remove all or some global scopes from the builder"""
        if scopes is None:
            self._removed_scopes = ['*']
        else:
            self._removed_scopes.extend(scopes)

        return self

    def find(self, id_, columns: List[str] = None):
        """Find a model by its primary key"""
        if isinstance(id_, list):
            return self.find_many(id_, columns)

        return self.where(self.model.get_key_name(), '=', id_).first(columns)

    def find_many(self, ids: List[Any], columns: List[str] = None):
        """Find multiple models by their primary keys"""
        return self.where_in(self.model.get_key_name(), ids).get(columns or ['*'])

    def find_or_fail(self, id_, columns: List[str] = None):
        """Find a model by its primary key or throw an exception"""
        result = self.find(id_, columns)
        
        if result is None:
            raise Exception(f"No query results for model [{self.model.__class__.__name__}] {id_}")
        
        return result

    def first_or_fail(self, columns: List[str] = None):
        """Execute the query and get the first result or throw an exception"""
        result = self.first(columns)
        
        if result is None:
            raise Exception(f"No query results for model [{self.model.__class__.__name__}]")
        
        return result

    def first_or_create(self, attributes: Dict[str, Any], 
                       values: Dict[str, Any] = None):
        """Get the first record matching the attributes or create it"""
        instance = self.where(attributes).first()
        
        if instance is None:
            attributes.update(values or {})
            instance = self.model.create(attributes)
        
        return instance

    def first_or_new(self, attributes: Dict[str, Any], 
                    values: Dict[str, Any] = None):
        """Get the first record matching the attributes or instantiate it"""
        instance = self.where(attributes).first()
        
        if instance is None:
            attributes.update(values or {})
            instance = self.model.__class__(attributes)
        
        return instance

    def update_or_create(self, attributes: Dict[str, Any], 
                        values: Dict[str, Any] = None):
        """Create or update a record matching the attributes"""
        instance = self.where(attributes).first()
        
        if instance:
            instance.fill(values or {})
            instance.save()
        else:
            attributes.update(values or {})
            instance = self.model.create(attributes)
        
        return instance

    def create(self, attributes: Dict[str, Any] = None):
        """Save a new model and return the instance"""
        return self.model.__class__.create(attributes)

    def force_create(self, attributes: Dict[str, Any] = None):
        """Save a new model and return the instance. Allow mass assignment"""
        return self.model.__class__.force_create(attributes)

    def get(self, columns: List[str] = None):
        """Execute the query as a "select" statement"""
        builder = self.apply_scopes()
        
        # If we have eager loads, we need to fetch them
        if self._eager_load:
            models = builder._get_models(columns)
            models = builder.eager_load_relations(models)
            return models
        
        return builder._get_models(columns)

    def first(self, columns: List[str] = None):
        """Execute the query and get the first result"""
        return self.take(1).get(columns)[0] if self.get(columns) else None

    def _get_models(self, columns: List[str] = None):
        """Get the hydrated models without eager loading"""
        results = super().get(columns or ['*'])
        
        return [self._hydrate(row) for row in results]

    def _hydrate(self, row: Dict[str, Any]):
        """Create a model instance from a database row"""
        if self.model:
            return self.model.new_from_builder(
                row, self.connection.get_name()
            )
        
        return row

    def eager_load_relations(self, models: List):
        """Eager load the relationships for the models"""
        for relation, constraints in self._eager_load.items():
            models = self._eager_load_relation(models, relation, constraints)
        
        return models

    def _eager_load_relation(self, models: List, name: str, constraints: Callable = None):
        """Eagerly load the relationship on a set of models"""
        if not models:
            return models

        # Get the relation instance
        relation = models[0].get_relation(name)
        if not relation:
            return models

        # Load the relation
        relation.add_eager_constraints(models)
        
        if constraints:
            constraints(relation)

        # Match the eager loaded models to their parents
        return relation.match(
            relation.init_relation(models, name),
            relation.get_eager(),
            name
        )

    def _get_relation_count_query(self, relation: str, constraints: Callable = None):
        """Get the relationship count query"""
        # This would build a count subquery for the relation
        # For now, return a basic count query
        return self.select_raw('COUNT(*)')

    def chunk(self, count: int, callback: Callable) -> bool:
        """Chunk the results of the query"""
        page = 1
        
        while True:
            # Clone the query for this chunk
            clone = self._clone()
            results = clone.for_page(page, count).get()
            
            count_results = len(results)
            
            if count_results == 0:
                break
            
            # Call the callback with the chunk
            if callback(results, page) == False:
                return False
            
            if count_results < count:
                break
            
            page += 1
        
        return True

    def for_page(self, page: int, per_page: int = 15) -> 'Builder':
        """Constrain the query to a given page"""
        return self.skip((page - 1) * per_page).take(per_page)

    def paginate(self, per_page: int = None, columns: List[str] = None, 
                page: int = 1) -> Dict[str, Any]:
        """Paginate the given query"""
        per_page = per_page or getattr(self.model, 'per_page', 15)
        
        # Get total count
        total = self.to_base().get_count_for_pagination()
        
        # Get the items for this page
        results = self.for_page(page, per_page).get(columns)
        
        # Calculate pagination info
        last_page = max(1, int((total + per_page - 1) / per_page))
        
        return {
            'data': results,
            'current_page': page,
            'per_page': per_page,
            'total': total,
            'last_page': last_page,
            'from': (page - 1) * per_page + 1 if results else None,
            'to': (page - 1) * per_page + len(results) if results else None,
            'has_more_pages': page < last_page
        }

    def simple_paginate(self, per_page: int = None, columns: List[str] = None, 
                       page: int = 1) -> Dict[str, Any]:
        """Get a simple paginator instance for the given query"""
        per_page = per_page or getattr(self.model, 'per_page', 15)
        
        # Get one extra to check if there are more pages
        results = self.for_page(page, per_page + 1).get(columns)
        
        has_more_pages = len(results) > per_page
        
        # Remove the extra item if we got it
        if has_more_pages:
            results = results[:-1]
        
        return {
            'data': results,
            'current_page': page,
            'per_page': per_page,
            'from': (page - 1) * per_page + 1 if results else None,
            'to': (page - 1) * per_page + len(results) if results else None,
            'has_more_pages': has_more_pages
        }

    def to_base(self) -> QueryBuilder:
        """Get the underlying query builder instance"""
        return QueryBuilder(self.connection, self.grammar, self.processor)

    def _clone(self) -> 'Builder':
        """Clone the Eloquent query builder"""
        clone = Builder(self.to_base(), self.model)
        clone._eager_load = self._eager_load.copy()
        clone._removed_scopes = self._removed_scopes.copy()
        
        return clone