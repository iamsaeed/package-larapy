"""Belongs To relationship"""

from typing import Optional
from .relation import Relation


class BelongsTo(Relation):
    """
    Many-to-One relationship where this model belongs to another model
    
    Example: Post belongs to User
    """

    def __init__(self, query, child, foreign_key: str, owner_key: str, relation_name: str):
        super().__init__(query, child, foreign_key, owner_key)
        self.child = child
        self.relation_name = relation_name

    def get_results(self):
        """Get the results of the relationship"""
        if self.constraints:
            self.add_constraints()
        
        return self.query.first()

    def add_constraints(self):
        """Set the base constraints on the relation query"""
        if self.constraints:
            # Get the foreign key value from the child model
            foreign_key_value = self.child.get_attribute(self.foreign_key)
            if foreign_key_value is not None:
                self.query.where(self.local_key, foreign_key_value)

    def add_eager_constraints(self, models: list):
        """Set the constraints for an eager load of the relation"""
        keys = self._get_keys(models, self.foreign_key)
        
        if keys:
            self.query.where_in(self.local_key, keys)

    def init_relation(self, models: list, relation: str):
        """Initialize the relation on a set of models"""
        for model in models:
            setattr(model, relation, None)
        
        return models

    def match(self, models: list, results, relation: str):
        """Match the eagerly loaded results to their parents"""
        # Create a dictionary for fast lookup
        dictionary = {}
        for result in results:
            key = result.get_attribute(self.local_key)
            dictionary[key] = result

        # Match results to their child models
        for model in models:
            foreign_key_value = model.get_attribute(self.foreign_key)
            if foreign_key_value in dictionary:
                setattr(model, relation, dictionary[foreign_key_value])

        return models

    def _get_keys(self, models: list, key: str) -> list:
        """Get all the keys for the given models"""
        keys = []
        for model in models:
            value = model.get_attribute(key)
            if value is not None:
                keys.append(value)
        
        return list(set(keys))  # Remove duplicates

    def associate(self, model):
        """Associate the model instance to the parent model"""
        if model is None:
            return self.dissociate()
        
        # Set the foreign key value
        owner_key_value = model.get_attribute(self.local_key)
        self.child.set_attribute(self.foreign_key, owner_key_value)
        
        # Set the relation attribute
        setattr(self.child, self.relation_name, model)
        
        return self.child

    def dissociate(self):
        """Dissociate the model instance from the parent model"""
        self.child.set_attribute(self.foreign_key, None)
        setattr(self.child, self.relation_name, None)
        
        return self.child

    def update(self, attributes: dict) -> int:
        """Update the related model"""
        if self.constraints:
            self.add_constraints()
            
        return self.query.update(attributes)

    def get_child(self):
        """Get the child model of the relation"""
        return self.child

    def get_foreign_key_name(self) -> str:
        """Get the foreign key for the relation"""
        return self.foreign_key

    def get_qualified_foreign_key_name(self) -> str:
        """Get the fully qualified foreign key name"""
        return f"{self.child.get_table()}.{self.foreign_key}"

    def get_owner_key_name(self) -> str:
        """Get the associated key of the relation"""
        return self.local_key

    def get_qualified_owner_key_name(self) -> str:
        """Get the fully qualified associated key of the relation"""
        related_model = self.query.get_model()
        return f"{related_model.get_table()}.{self.local_key}"

    def get_relation_name(self) -> str:
        """Get the name of the relationship"""
        return self.relation_name