"""Has Relationships concern for Eloquent models"""

from typing import Any, Dict, List, Optional, Type, Union
from ..relations.relation import Relation
from ..relations.has_one import HasOne
from ..relations.has_many import HasMany
from ..relations.belongs_to import BelongsTo
from ..relations.belongs_to_many import BelongsToMany


class HasRelationships:
    """
    Provides relationship management functionality for Eloquent models
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._relations = {}
        self._loaded_relations = {}

    def has_one(self, related: Union[str, Type], foreign_key: str = None, 
                local_key: str = None) -> HasOne:
        """Define a one-to-one relationship"""
        instance = self._new_related_instance(related)
        
        foreign_key = foreign_key or self._get_foreign_key()
        local_key = local_key or self.get_key_name()

        return HasOne(instance.new_query(), self, 
                     instance.get_table() + '.' + foreign_key, local_key)

    def has_many(self, related: Union[str, Type], foreign_key: str = None, 
                 local_key: str = None) -> HasMany:
        """Define a one-to-many relationship"""
        instance = self._new_related_instance(related)
        
        foreign_key = foreign_key or self._get_foreign_key()
        local_key = local_key or self.get_key_name()

        return HasMany(instance.new_query(), self, 
                      instance.get_table() + '.' + foreign_key, local_key)

    def belongs_to(self, related: Union[str, Type], foreign_key: str = None, 
                   owner_key: str = None, relation: str = None) -> BelongsTo:
        """Define an inverse one-to-one or one-to-many relationship"""
        if relation is None:
            # Get the calling method name from the stack
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                relation = frame.f_back.f_code.co_name

        instance = self._new_related_instance(related)
        
        foreign_key = foreign_key or self._get_foreign_key_name(relation)
        owner_key = owner_key or instance.get_key_name()

        return BelongsTo(instance.new_query(), self, foreign_key, 
                        owner_key, relation)

    def belongs_to_many(self, related: Union[str, Type], table: str = None, 
                       foreign_pivot_key: str = None, related_pivot_key: str = None,
                       parent_key: str = None, related_key: str = None, 
                       relation: str = None) -> BelongsToMany:
        """Define a many-to-many relationship"""
        if relation is None:
            # Get the calling method name from the stack
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                relation = frame.f_back.f_code.co_name

        instance = self._new_related_instance(related)

        foreign_pivot_key = foreign_pivot_key or self._get_foreign_key()
        related_pivot_key = related_pivot_key or instance._get_foreign_key()

        table = table or self._join_table(related, instance)

        return BelongsToMany(
            instance.new_query(), self, table, foreign_pivot_key,
            related_pivot_key, parent_key or self.get_key_name(),
            related_key or instance.get_key_name(), relation
        )

    def _new_related_instance(self, cls: Union[str, Type]):
        """Create a new instance of the related model"""
        if isinstance(cls, str):
            # Import and instantiate the class by name
            # This would need proper model resolution in a full implementation
            from ..model import Model
            return Model()
        return cls()

    def _get_foreign_key(self) -> str:
        """Get the default foreign key name for the model"""
        return self._snake_case(self.__class__.__name__) + '_id'

    def _get_foreign_key_name(self, relation: str) -> str:
        """Get the foreign key for a belongs to relationship"""
        return f"{relation}_id"

    def _join_table(self, related: Union[str, Type], instance) -> str:
        """Get the joining table name for a many-to-many relationship"""
        # Get table names
        base_table = self.get_table()
        related_table = instance.get_table()
        
        # Sort alphabetically
        tables = sorted([base_table, related_table])
        return f"{tables[0]}_{tables[1]}"

    def _snake_case(self, string: str) -> str:
        """Convert a string to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_relation(self, relation: str) -> Optional[Relation]:
        """Get a relationship instance"""
        if relation in self._relations:
            return self._relations[relation]

        if hasattr(self, relation):
            method = getattr(self, relation)
            if callable(method):
                result = method()
                if isinstance(result, Relation):
                    self._relations[relation] = result
                    return result

        return None

    def set_relation(self, relation: str, value: Any):
        """Set the given relationship on the model"""
        self._loaded_relations[relation] = value

    def unset_relation(self, relation: str):
        """Unset a loaded relationship"""
        if relation in self._loaded_relations:
            del self._loaded_relations[relation]

    def get_relations(self) -> Dict[str, Any]:
        """Get all the loaded relations for the instance"""
        return self._loaded_relations

    def set_relations(self, relations: Dict[str, Any]):
        """Set the entire relations array on the model"""
        self._loaded_relations = relations

    def touch_owners(self) -> bool:
        """Touch the owning relations of the model"""
        owners = []

        for relation in self._get_touching_relationships():
            owners.append(self.get_relation(relation).get_results())

        for owner in owners:
            if owner:
                owner.touch()

        return True

    def _get_touching_relationships(self) -> List[str]:
        """Get the relationships that should be touched on save"""
        return getattr(self, 'touches', [])

    def load(self, *relations) -> 'Model':
        """Eager load relations on the model"""
        if len(relations) == 1 and isinstance(relations[0], list):
            relations = relations[0]

        query = self.new_query_for_restoration()

        for relation in relations:
            if isinstance(relation, str):
                query = query.with_(relation)
            elif isinstance(relation, dict):
                for key, constraints in relation.items():
                    query = query.with_(key, constraints)

        return query.first_or_fail()

    def load_missing(self, *relations) -> 'Model':
        """Eager load relations on the model if they are not already loaded"""
        missing_relations = []

        for relation in relations:
            if relation not in self._loaded_relations:
                missing_relations.append(relation)

        if missing_relations:
            return self.load(*missing_relations)

        return self

    def relation_loaded(self, key: str) -> bool:
        """Determine if the given relation is loaded"""
        return key in self._loaded_relations

    def get_relationship_from_method(self, method: str) -> Optional[Relation]:
        """Get the relationship from the given method"""
        if hasattr(self, method):
            relation = getattr(self, method)()
            if isinstance(relation, Relation):
                return relation

        return None