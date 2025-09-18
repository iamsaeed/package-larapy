"""Base relation class for Eloquent relationships"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union


class Relation(ABC):
    """
    Base class for all Eloquent relationships
    
    Provides the common interface and functionality for all relationship types.
    """

    def __init__(self, query, parent, foreign_key: str, local_key: str):
        self.query = query
        self.parent = parent
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.constraints = True

    @abstractmethod
    def get_results(self):
        """Get the results of the relationship"""
        pass

    @abstractmethod
    def add_constraints(self):
        """Set the base constraints on the relation query"""
        pass

    @abstractmethod
    def add_eager_constraints(self, models: List):
        """Set the constraints for an eager load of the relation"""
        pass

    @abstractmethod
    def init_relation(self, models: List, relation: str):
        """Initialize the relation on a set of models"""
        pass

    @abstractmethod
    def match(self, models: List, results, relation: str):
        """Match the eagerly loaded results to their parents"""
        pass

    def get_query(self):
        """Get the underlying query for the relation"""
        return self.query

    def get_base_query(self):
        """Get the base query builder for the relation"""
        return self.query

    def get_parent(self):
        """Get the parent model of the relation"""
        return self.parent

    def get_qualified_parent_key_name(self) -> str:
        """Get the fully qualified parent key name"""
        return f"{self.parent.get_table()}.{self.local_key}"

    def get_foreign_key_name(self) -> str:
        """Get the foreign key for the relation"""
        return self.foreign_key

    def get_local_key_name(self) -> str:
        """Get the local key for the relation"""
        return self.local_key

    def raw_update(self, attributes: Dict[str, Any]) -> int:
        """Run a raw update against the base query"""
        return self.query.update(attributes)

    def where(self, column: str, operator: str = None, value: Any = None):
        """Add a where clause to the relationship query"""
        return self.query.where(column, operator, value)

    def where_in(self, column: str, values: List[Any]):
        """Add a where in clause to the relationship query"""
        return self.query.where_in(column, values)

    def order_by(self, column: str, direction: str = 'asc'):
        """Add an order by clause to the relationship query"""
        return self.query.order_by(column, direction)

    def limit(self, count: int):
        """Set the limit on the relationship query"""
        return self.query.limit(count)

    def get(self):
        """Execute the query and get the results"""
        return self.query.get()

    def first(self):
        """Execute the query and get the first result"""
        return self.query.first()

    def find(self, id: Any):
        """Find a model by its primary key"""
        return self.query.find(id)

    def count(self) -> int:
        """Get the count of the related models"""
        return self.query.count()

    def exists(self) -> bool:
        """Determine if any related models exist"""
        return self.query.exists()

    def is_constraints_enabled(self) -> bool:
        """Determine if constraints are enabled for the relation"""
        return self.constraints

    def no_constraints(self, callback):
        """Run a callback with constraints disabled"""
        previous = self.constraints
        self.constraints = False
        
        try:
            return callback(self)
        finally:
            self.constraints = previous

    def get_relationship_name(self) -> str:
        """Get the name of the relationship"""
        # This would typically be set by the parent model
        return getattr(self, 'relationship_name', 'relation')

    def __call__(self, *args, **kwargs):
        """Allow the relation to be called as a method"""
        return self.get_results()