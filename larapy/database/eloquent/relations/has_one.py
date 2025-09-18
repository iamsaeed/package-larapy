"""Has One relationship"""

from typing import Optional
from .relation import Relation


class HasOne(Relation):
    """
    One-to-One relationship where this model has one related model
    
    Example: User has one Profile
    """

    def get_results(self):
        """Get the results of the relationship"""
        if self.constraints:
            self.add_constraints()
        
        return self.query.first()

    def add_constraints(self):
        """Set the base constraints on the relation query"""
        if self.constraints:
            parent_key = self.parent.get_attribute(self.local_key)
            self.query.where(self.foreign_key, parent_key)

    def add_eager_constraints(self, models: list):
        """Set the constraints for an eager load of the relation"""
        keys = self._get_keys(models, self.local_key)
        
        if keys:
            self.query.where_in(self.foreign_key, keys)

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
            key = result.get_attribute(self.foreign_key)
            dictionary[key] = result

        # Match results to their parent models
        for model in models:
            key = model.get_attribute(self.local_key)
            if key in dictionary:
                setattr(model, relation, dictionary[key])

        return models

    def _get_keys(self, models: list, key: str) -> list:
        """Get all the keys for the given models"""
        keys = []
        for model in models:
            value = model.get_attribute(key)
            if value is not None:
                keys.append(value)
        
        return list(set(keys))  # Remove duplicates

    def save(self, model):
        """Save a model and set the foreign key"""
        # Set the foreign key on the related model
        foreign_key_value = self.parent.get_attribute(self.local_key)
        model.set_attribute(self.foreign_key, foreign_key_value)
        
        return model.save()

    def create(self, attributes: dict = None):
        """Create a new related model"""
        attributes = attributes or {}
        
        # Set the foreign key
        foreign_key_value = self.parent.get_attribute(self.local_key)
        attributes[self.foreign_key] = foreign_key_value
        
        # Get the related model class
        related_model = self.query.model
        
        return related_model.create(attributes)

    def update(self, attributes: dict) -> int:
        """Update the related model"""
        if self.constraints:
            self.add_constraints()
            
        return self.query.update(attributes)

    def delete(self) -> int:
        """Delete the related model"""
        if self.constraints:
            self.add_constraints()
            
        return self.query.delete()

    def get_foreign_key_name(self) -> str:
        """Get the foreign key for the relation"""
        return self.foreign_key

    def get_qualified_foreign_key_name(self) -> str:
        """Get the fully qualified foreign key name"""
        return f"{self.query.get_model().get_table()}.{self.foreign_key}"