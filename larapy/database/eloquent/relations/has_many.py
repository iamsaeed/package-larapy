"""Has Many relationship"""

from typing import List
from .relation import Relation


class HasMany(Relation):
    """
    One-to-Many relationship where this model has many related models
    
    Example: User has many Posts
    """

    def get_results(self):
        """Get the results of the relationship"""
        if self.constraints:
            self.add_constraints()
        
        return self.query.get()

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
            setattr(model, relation, [])
        
        return models

    def match(self, models: list, results, relation: str):
        """Match the eagerly loaded results to their parents"""
        # Create a dictionary for fast lookup
        dictionary = {}
        for result in results:
            key = result.get_attribute(self.foreign_key)
            if key not in dictionary:
                dictionary[key] = []
            dictionary[key].append(result)

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

    def save_many(self, models: List):
        """Save multiple models and set their foreign keys"""
        results = []
        for model in models:
            results.append(self.save(model))
        return results

    def create(self, attributes: dict = None):
        """Create a new related model"""
        attributes = attributes or {}
        
        # Set the foreign key
        foreign_key_value = self.parent.get_attribute(self.local_key)
        attributes[self.foreign_key] = foreign_key_value
        
        # Get the related model class
        related_model = self.query.model
        
        return related_model.create(attributes)

    def create_many(self, attributes_list: List[dict]):
        """Create multiple related models"""
        results = []
        for attributes in attributes_list:
            results.append(self.create(attributes))
        return results

    def find_or_new(self, id):
        """Find a related model by ID or return a new instance"""
        if id is not None:
            result = self.find(id)
            if result:
                return result
        
        # Create new instance with foreign key set
        related_model = self.query.model
        instance = related_model()
        
        foreign_key_value = self.parent.get_attribute(self.local_key)
        instance.set_attribute(self.foreign_key, foreign_key_value)
        
        return instance

    def first_or_new(self, attributes: dict = None, values: dict = None):
        """Get the first related model or create a new one"""
        attributes = attributes or {}
        values = values or {}
        
        # Add foreign key to search criteria
        foreign_key_value = self.parent.get_attribute(self.local_key)
        attributes[self.foreign_key] = foreign_key_value
        
        # Search for existing model
        for key, value in attributes.items():
            self.query.where(key, value)
        
        result = self.query.first()
        if result:
            return result
        
        # Create new instance
        all_attributes = {**attributes, **values}
        related_model = self.query.model
        return related_model(all_attributes)

    def first_or_create(self, attributes: dict = None, values: dict = None):
        """Get the first related model or create and save a new one"""
        instance = self.first_or_new(attributes, values)
        
        if not instance.exists:
            instance.save()
        
        return instance

    def update_or_create(self, attributes: dict, values: dict = None):
        """Update the first related model or create a new one"""
        values = values or {}
        
        # Add foreign key to search criteria
        foreign_key_value = self.parent.get_attribute(self.local_key)
        attributes[self.foreign_key] = foreign_key_value
        
        instance = self.first_or_new(attributes, values)
        
        if instance.exists:
            # Update existing model
            for key, value in values.items():
                instance.set_attribute(key, value)
            instance.save()
        else:
            # Create new model
            instance.save()
        
        return instance

    def update(self, attributes: dict) -> int:
        """Update all related models"""
        if self.constraints:
            self.add_constraints()
            
        return self.query.update(attributes)

    def delete(self) -> int:
        """Delete all related models"""
        if self.constraints:
            self.add_constraints()
            
        return self.query.delete()

    def get_foreign_key_name(self) -> str:
        """Get the foreign key for the relation"""
        return self.foreign_key

    def get_qualified_foreign_key_name(self) -> str:
        """Get the fully qualified foreign key name"""
        return f"{self.query.get_model().get_table()}.{self.foreign_key}"