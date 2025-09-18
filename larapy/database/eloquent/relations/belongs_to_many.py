"""Belongs To Many relationship"""

from typing import List, Dict, Any
from .relation import Relation


class BelongsToMany(Relation):
    """
    Many-to-Many relationship with a pivot table
    
    Example: User belongs to many Roles (through user_roles pivot table)
    """

    def __init__(self, query, parent, table: str, foreign_pivot_key: str, 
                 related_pivot_key: str, parent_key: str, related_key: str, 
                 relation_name: str = None):
        super().__init__(query, parent, foreign_pivot_key, parent_key)
        self.table = table
        self.foreign_pivot_key = foreign_pivot_key
        self.related_pivot_key = related_pivot_key
        self.parent_key = parent_key
        self.related_key = related_key
        self.relation_name = relation_name or 'pivot'
        self.pivot_columns = []
        self.pivot_wheres = []

    def get_results(self):
        """Get the results of the relationship"""
        if self.constraints:
            self.add_constraints()
        
        return self.query.get()

    def add_constraints(self):
        """Set the base constraints on the relation query"""
        if self.constraints:
            self._perform_join()
            parent_key_value = self.parent.get_attribute(self.parent_key)
            self.query.where(f"{self.table}.{self.foreign_pivot_key}", parent_key_value)

    def add_eager_constraints(self, models: list):
        """Set the constraints for an eager load of the relation"""
        self._perform_join()
        
        keys = self._get_keys(models, self.parent_key)
        if keys:
            self.query.where_in(f"{self.table}.{self.foreign_pivot_key}", keys)

    def init_relation(self, models: list, relation: str):
        """Initialize the relation on a set of models"""
        for model in models:
            setattr(model, relation, [])
        
        return models

    def match(self, models: list, results, relation: str):
        """Match the eagerly loaded results to their parents"""
        # Create a dictionary for fast lookup
        dictionary = {}
        for result in results:
            pivot_key = result.pivot.get_attribute(self.foreign_pivot_key)
            if pivot_key not in dictionary:
                dictionary[pivot_key] = []
            dictionary[pivot_key].append(result)

        # Match results to their parent models
        for model in models:
            key = model.get_attribute(self.parent_key)
            if key in dictionary:
                setattr(model, relation, dictionary[key])

        return models

    def _perform_join(self, query=None):
        """Perform the join for the many-to-many relationship"""
        if query is None:
            query = self.query

        # Get table names
        related_table = self.query.get_model().get_table()
        
        # Perform the join
        query.join(
            self.table,
            f"{related_table}.{self.related_key}",
            "=",
            f"{self.table}.{self.related_pivot_key}"
        )

        return query

    def _get_keys(self, models: list, key: str) -> list:
        """Get all the keys for the given models"""
        keys = []
        for model in models:
            value = model.get_attribute(key)
            if value is not None:
                keys.append(value)
        
        return list(set(keys))  # Remove duplicates

    def with_pivot(self, *columns):
        """Specify additional columns to select from the pivot table"""
        self.pivot_columns.extend(columns)
        return self

    def where_pivot(self, column: str, operator: str = None, value: Any = None):
        """Add a where clause to the pivot table"""
        self.pivot_wheres.append({
            'column': f"{self.table}.{column}",
            'operator': operator or '=',
            'value': value
        })
        return self

    def where_pivot_in(self, column: str, values: List[Any]):
        """Add a where in clause to the pivot table"""
        self.query.where_in(f"{self.table}.{column}", values)
        return self

    def order_by_pivot(self, column: str, direction: str = 'asc'):
        """Add an order by clause to the pivot table"""
        self.query.order_by(f"{self.table}.{column}", direction)
        return self

    def attach(self, id, attributes: Dict[str, Any] = None):
        """Attach a model to the parent"""
        attributes = attributes or {}
        
        parent_key_value = self.parent.get_attribute(self.parent_key)
        
        # Prepare pivot record
        pivot_data = {
            self.foreign_pivot_key: parent_key_value,
            self.related_pivot_key: id,
            **attributes
        }
        
        # Insert into pivot table
        connection = self.parent.get_connection()
        return connection.table(self.table).insert(pivot_data)

    def detach(self, ids=None):
        """Detach models from the parent"""
        parent_key_value = self.parent.get_attribute(self.parent_key)
        
        query = self.parent.get_connection().table(self.table)
        query.where(self.foreign_pivot_key, parent_key_value)
        
        if ids is not None:
            if not isinstance(ids, list):
                ids = [ids]
            query.where_in(self.related_pivot_key, ids)
        
        return query.delete()

    def sync(self, ids: List[int], detaching: bool = True):
        """Sync the intermediate table with a list of IDs"""
        if not isinstance(ids, list):
            ids = [ids]
        
        # Get current attached IDs
        current = self._get_current_ids()
        
        # Determine what to attach and detach
        to_attach = [id for id in ids if id not in current]
        to_detach = [id for id in current if id not in ids] if detaching else []
        
        # Perform operations
        changes = {
            'attached': [],
            'detached': [],
            'updated': []
        }
        
        # Detach models
        if to_detach:
            self.detach(to_detach)
            changes['detached'] = to_detach
        
        # Attach new models
        for id in to_attach:
            self.attach(id)
            changes['attached'].append(id)
        
        return changes

    def sync_without_detaching(self, ids: List[int]):
        """Sync without detaching existing records"""
        return self.sync(ids, detaching=False)

    def toggle(self, ids: List[int]):
        """Toggle the attachment of the given IDs"""
        if not isinstance(ids, list):
            ids = [ids]
        
        current = self._get_current_ids()
        
        changes = {
            'attached': [],
            'detached': []
        }
        
        for id in ids:
            if id in current:
                self.detach(id)
                changes['detached'].append(id)
            else:
                self.attach(id)
                changes['attached'].append(id)
        
        return changes

    def _get_current_ids(self) -> List[int]:
        """Get the currently attached model IDs"""
        parent_key_value = self.parent.get_attribute(self.parent_key)
        
        results = (self.parent.get_connection()
                  .table(self.table)
                  .where(self.foreign_pivot_key, parent_key_value)
                  .pluck(self.related_pivot_key))
        
        return results

    def save(self, model, attributes: Dict[str, Any] = None):
        """Save a model and attach it to the parent"""
        model.save()
        self.attach(model.get_key(), attributes)
        return model

    def save_many(self, models: List, attributes_list: List[Dict[str, Any]] = None):
        """Save multiple models and attach them"""
        attributes_list = attributes_list or [{}] * len(models)
        
        for i, model in enumerate(models):
            attributes = attributes_list[i] if i < len(attributes_list) else {}
            self.save(model, attributes)
        
        return models

    def create(self, attributes: Dict[str, Any] = None, pivot_attributes: Dict[str, Any] = None):
        """Create a new related model and attach it"""
        attributes = attributes or {}
        pivot_attributes = pivot_attributes or {}
        
        # Create the model
        related_model = self.query.get_model()
        instance = related_model.create(attributes)
        
        # Attach it
        self.attach(instance.get_key(), pivot_attributes)
        
        return instance

    def create_many(self, records: List[Dict[str, Any]]):
        """Create multiple related models and attach them"""
        results = []
        for record in records:
            attributes = record.get('attributes', {})
            pivot_attributes = record.get('pivot', {})
            results.append(self.create(attributes, pivot_attributes))
        
        return results

    def get_table(self) -> str:
        """Get the intermediate table for the relationship"""
        return self.table

    def get_foreign_pivot_key_name(self) -> str:
        """Get the foreign key for the parent model on the pivot table"""
        return self.foreign_pivot_key

    def get_related_pivot_key_name(self) -> str:
        """Get the foreign key for the related model on the pivot table"""
        return self.related_pivot_key

    def get_parent_key_name(self) -> str:
        """Get the key name of the parent model"""
        return self.parent_key

    def get_related_key_name(self) -> str:
        """Get the key name of the related model"""
        return self.related_key