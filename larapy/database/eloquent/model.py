"""Enhanced Eloquent Model class"""

from typing import Any, Dict, List, Optional, Union, Type
from abc import ABC
from datetime import datetime
from .concerns.has_attributes import HasAttributes
from .concerns.has_timestamps import HasTimestamps
from .concerns.has_relationships import HasRelationships
from .concerns.soft_deletes import SoftDeletes
from .events import HasEvents
from .scopes import HasGlobalScopes, HasQueryScopes
from ..query.builder import QueryBuilder


class Model(HasAttributes, HasTimestamps, HasRelationships, HasEvents, HasGlobalScopes, HasQueryScopes):
    """
    Enhanced Eloquent Model with Laravel-like functionality
    """

    # The connection name for the model
    connection = None

    # The table associated with the model
    table = None

    # The primary key for the model
    primary_key = 'id'

    # The "type" of the primary key ID
    key_type = 'int'

    # Indicates if the IDs are auto-incrementing
    incrementing = True

    # Indicates if the model exists
    exists = False

    # Indicates if the model was inserted during this request
    was_recently_created = False

    # The attributes that are mass assignable
    fillable = []

    # The attributes that aren't mass assignable
    guarded = ['*']

    # The attributes that should be hidden for serialization
    hidden = []

    # The attributes that should be visible in serialization
    visible = []

    # The accessors to append to the model's array form
    appends = []

    # The attributes that should be cast
    casts = {}

    # The attributes that should be mutated to dates
    dates = []

    # The storage format of the model's date columns
    date_format = '%Y-%m-%d %H:%M:%S'

    # The relations to eager load on every query
    with_ = []

    # The relationship count's that should be eager loaded on every query
    with_count = []

    # The number of models to return for pagination
    per_page = 15

    # The default attributes
    attributes = {}

    def __init__(self, attributes: Dict[str, Any] = None):
        """Create a new Eloquent model instance"""
        super().__init__(attributes or {})
        self.sync_original()
        self.boot_if_not_booted()

    @classmethod
    def boot_if_not_booted(cls):
        """Check if the model needs to be booted and boot it"""
        if not hasattr(cls, '_booted') or not cls._booted:
            cls._booted = True
            cls.boot()

    @classmethod
    def boot(cls):
        """Boot the model"""
        pass

    def new_instance(self, attributes: Dict[str, Any] = None, exists: bool = False):
        """Create a new instance of the model"""
        instance = self.__class__(attributes)
        instance.exists = exists
        instance.set_connection(self.get_connection_name())
        
        return instance

    def new_from_builder(self, attributes: Dict[str, Any] = None, connection: str = None):
        """Create a new model instance from the query builder"""
        instance = self.new_instance({}, True)
        instance.set_raw_attributes(attributes or {}, True)
        instance.set_connection(connection or self.get_connection_name())
        instance.fire_model_event('retrieved', False)

        return instance

    def save(self, options: Dict[str, Any] = None) -> bool:
        """Save the model to the database"""
        query = self.new_query_without_scopes()

        # Fire saving event
        if self.fire_model_event('saving') == False:
            return False

        # Update timestamps if needed
        if self.uses_timestamps():
            self.update_timestamps()

        # Determine if this is a create or update
        if self.exists:
            saved = self.is_dirty() and self.perform_update(query)
        else:
            saved = self.perform_insert(query)

        # Fire saved event
        if saved:
            self.finish_save(options)

        return saved

    def perform_insert(self, query: QueryBuilder) -> bool:
        """Perform a model insert operation"""
        if self.fire_model_event('creating') == False:
            return False

        # Prepare timestamps
        if self.uses_timestamps():
            self.update_timestamps()

        # Get attributes to insert
        attributes = self.get_attributes_for_insert()

        if self.get_incrementing():
            # Insert and get the new ID
            inserted_id = query.insert_get_id(attributes, self.get_key_name())
            if inserted_id:
                self.set_attribute(self.get_key_name(), inserted_id)
        else:
            # Just insert
            query.insert(attributes)

        # Mark as existing
        self.exists = True
        self.was_recently_created = True

        # Fire created event
        self.fire_model_event('created', False)

        return True

    def perform_update(self, query: QueryBuilder) -> bool:
        """Perform a model update operation"""
        if self.fire_model_event('updating') == False:
            return False

        # Get dirty attributes
        dirty = self.get_dirty()

        if len(dirty) > 0:
            # Perform the update
            self.set_keys_for_save_query(query).update(dirty)
            
            # Sync changes
            self.sync_changes()

        # Fire updated event
        self.fire_model_event('updated', False)

        return True

    def delete(self) -> bool:
        """Delete the model from the database"""
        if self.get_key() is None:
            return False

        if self.fire_model_event('deleting') == False:
            return False

        # Touch the owning relations
        self.touch_owners()

        # Perform the delete
        result = self.new_query_without_scopes().where(
            self.get_key_name(), self.get_key()
        ).delete()

        # Fire deleted event
        self.fire_model_event('deleted', False)

        return result > 0

    def force_delete(self) -> bool:
        """Force a hard delete on a soft deleted model"""
        return self.delete()

    def fresh(self, with_: List[str] = None):
        """Reload a fresh model instance from the database"""
        if not self.exists:
            return None

        instance = self.new_query_without_scopes().where(
            self.get_key_name(), self.get_key()
        )

        if with_:
            instance = instance.with_(*with_)

        return instance.first()

    def refresh(self):
        """Reload the current model instance with fresh attributes from the database"""
        if not self.exists:
            return self

        fresh_instance = self.fresh()
        if fresh_instance:
            self.set_raw_attributes(fresh_instance.get_attributes(), True)
            self.set_relations(fresh_instance.get_relations())

        return self

    def replicate(self, except_: List[str] = None):
        """Clone the model into a new, non-existing instance"""
        except_ = except_ or []
        
        attributes = self.get_attributes()
        
        # Remove the primary key and except attributes
        for attr in [self.get_key_name()] + except_:
            if attr in attributes:
                del attributes[attr]

        instance = self.new_instance()
        instance.set_raw_attributes(attributes)

        return instance

    def is_(self, model) -> bool:
        """Determine if two models have the same ID and belong to the same table"""
        return (self.get_key() is not None and 
                model.get_key() is not None and
                self.get_key() == model.get_key() and
                self.get_table() == model.get_table() and
                self.get_connection_name() == model.get_connection_name())

    def is_not(self, model) -> bool:
        """Determine if two models are not the same"""
        return not self.is_(model)

    def get_connection_name(self) -> Optional[str]:
        """Get the database connection for the model"""
        return self.connection

    def set_connection(self, name: str):
        """Set the connection associated with the model"""
        self.connection = name

    def get_table(self) -> str:
        """Get the table associated with the model"""
        if self.table is not None:
            return self.table

        return self._snake_case(self.__class__.__name__) + 's'

    def set_table(self, table: str):
        """Set the table associated with the model"""
        self.table = table

    def get_key_name(self) -> str:
        """Get the primary key for the model"""
        return self.primary_key

    def set_key_name(self, key: str):
        """Set the primary key for the model"""
        self.primary_key = key

    def get_qualified_key_name(self) -> str:
        """Get the table qualified key name"""
        return f"{self.get_table()}.{self.get_key_name()}"

    def get_key_type(self) -> str:
        """Get the auto-incrementing key type"""
        return self.key_type

    def set_key_type(self, type_: str):
        """Set the data type for the primary key"""
        self.key_type = type_

    def get_incrementing(self) -> bool:
        """Get the value indicating whether the IDs are incrementing"""
        return self.incrementing

    def set_incrementing(self, value: bool):
        """Set whether IDs are incrementing"""
        self.incrementing = value

    def get_key(self) -> Any:
        """Get the value of the model's primary key"""
        return self.get_attribute(self.get_key_name())

    def get_queued_key(self) -> Any:
        """Get the queueable identity for the entity"""
        return self.get_key()

    def get_route_key(self) -> Any:
        """Get the route key for the model"""
        return self.get_attribute(self.get_route_key_name())

    def get_route_key_name(self) -> str:
        """Get the route key name for the model"""
        return self.get_key_name()

    def get_attributes_for_insert(self) -> Dict[str, Any]:
        """Get the attributes that should be used for insert"""
        return self.get_attributes()

    def set_keys_for_save_query(self, query: QueryBuilder) -> QueryBuilder:
        """Set the keys for a save update query"""
        query.where(self.get_key_name(), '=', self.get_key_for_save_query())
        return query

    def get_key_for_save_query(self) -> Any:
        """Get the primary key value for a save query"""
        return self.original.get(self.get_key_name()) or self.get_key()

    def fill(self, attributes: Dict[str, Any]):
        """Fill the model with an array of attributes"""
        total_guarded = self.total_guarded()

        for key, value in attributes.items():
            if self.is_fillable(key):
                self.set_attribute(key, value)
            elif total_guarded:
                raise Exception(f"Add [{key}] to fillable property to allow mass assignment on [{self.__class__.__name__}].")

        return self

    def force_fill(self, attributes: Dict[str, Any]):
        """Fill the model with an array of attributes. Force mass assignment"""
        for key, value in attributes.items():
            self.set_attribute(key, value)

        return self

    def new_query(self) -> QueryBuilder:
        """Get a new query builder for the model's table"""
        return self.register_global_scopes(self.new_query_without_scopes())

    def new_query_without_scopes(self) -> QueryBuilder:
        """Get a new query builder that doesn't have any global scopes"""
        # This would return an actual QueryBuilder connected to the database
        # For now, we'll return a basic QueryBuilder
        from ..manager import DatabaseManager
        
        manager = DatabaseManager.get_instance()
        return manager.table(self.get_table())

    def new_query_for_restoration(self):
        """Get a new query to restore one or more models by their primary keys"""
        return self.new_query_without_scopes().use_write_pdo()

    def register_global_scopes(self, builder: QueryBuilder) -> QueryBuilder:
        """Register the global scopes for this builder instance"""
        # Global scopes would be applied here
        return builder

    def is_fillable(self, key: str) -> bool:
        """Determine if the given attribute may be mass assigned"""
        if key in self.fillable:
            return True

        if self.is_guarded(key):
            return False

        return self.fillable == [] and not key.startswith('_')

    def is_guarded(self, key: str) -> bool:
        """Determine if the given key is guarded"""
        return key in self.guarded or self.guarded == ['*']

    def total_guarded(self) -> bool:
        """Determine if the model is totally guarded"""
        return self.fillable == [] and self.guarded == ['*']

    def fillable_from_array(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Get the fillable attributes from the given array"""
        if len(self.fillable) > 0 and not '*' in self.guarded:
            return {k: v for k, v in attributes.items() if k in self.fillable}

        return {k: v for k, v in attributes.items() if not self.is_guarded(k)}

    def fire_model_event(self, event: str, halt: bool = True) -> bool:
        """Fire the given event for the model"""
        # Event system would be implemented here
        # For now, just return True to continue
        return True

    def finish_save(self, options: Dict[str, Any] = None):
        """Finish processing on a successful save operation"""
        self.fire_model_event('saved', False)
        self.sync_original()

        if options and options.get('touch', True):
            self.touch_owners()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary"""
        return self.attributes_to_dict()

    def attributes_to_dict(self) -> Dict[str, Any]:
        """Convert the model's attributes to a dictionary"""
        attributes = self.get_arrayable_attributes()
        
        # Add mutated attributes
        attributes.update(self.get_mutated_attributes())
        
        return attributes

    def get_arrayable_attributes(self) -> Dict[str, Any]:
        """Get an attribute array of all arrayable attributes"""
        return self.get_arrayable_items(self.get_attributes())

    def get_arrayable_items(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Get an attribute array of all arrayable values"""
        if len(self.visible) > 0:
            values = {k: v for k, v in values.items() if k in self.visible}

        if len(self.hidden) > 0:
            values = {k: v for k, v in values.items() if k not in self.hidden}

        return values

    def get_mutated_attributes(self) -> Dict[str, Any]:
        """Get the mutated attributes for the instance"""
        mutated = {}
        
        for key in self.get_appends():
            mutated[key] = self.mutate_attribute_for_array(key, None)

        return mutated

    def get_appends(self) -> List[str]:
        """Get the accessors that are being appended to the model's array form"""
        return self.appends

    def mutate_attribute_for_array(self, key: str, value: Any) -> Any:
        """Get the value of an attribute using its mutator for array conversion"""
        value = self.mutate_attribute(key, value)
        
        # Convert dates to strings for JSON serialization
        if isinstance(value, datetime):
            return value.strftime(self.date_format)

        return value

    def mutate_attribute(self, key: str, value: Any) -> Any:
        """Get the value of an attribute using its mutator"""
        return self.get_attribute(key)

    def __str__(self) -> str:
        """Get the string representation of the model"""
        return str(self.to_dict())

    def __repr__(self) -> str:
        """Get the representation of the model"""
        return f"<{self.__class__.__name__}: {self.get_key()}>"

    @classmethod
    def query(cls) -> QueryBuilder:
        """Begin querying the model"""
        return cls().new_query()

    @classmethod
    def all(cls, columns: List[str] = None):
        """Get all of the models from the database"""
        return cls.query().get(columns or ['*'])

    @classmethod
    def find(cls, id_, columns: List[str] = None):
        """Find a model by its primary key"""
        if isinstance(id_, list):
            return cls.find_many(id_, columns)

        return cls.query().where(cls().get_key_name(), '=', id_).first(columns)

    @classmethod
    def find_many(cls, ids: List[Any], columns: List[str] = None):
        """Find multiple models by their primary keys"""
        return cls.query().where_in(cls().get_key_name(), ids).get(columns or ['*'])

    @classmethod
    def find_or_fail(cls, id_, columns: List[str] = None):
        """Find a model by its primary key or throw an exception"""
        result = cls.find(id_, columns)
        
        if result is None:
            raise Exception(f"No query results for model [{cls.__name__}] {id_}")
        
        return result

    @classmethod
    def first_or_fail(cls, columns: List[str] = None):
        """Execute the query and get the first result or throw an exception"""
        result = cls.query().first(columns)
        
        if result is None:
            raise Exception(f"No query results for model [{cls.__name__}]")
        
        return result

    @classmethod
    def create(cls, attributes: Dict[str, Any] = None):
        """Save a new model and return the instance"""
        instance = cls(attributes)
        instance.save()
        
        return instance

    @classmethod
    def force_create(cls, attributes: Dict[str, Any] = None):
        """Save a new model and return the instance. Allow mass assignment"""
        instance = cls()
        instance.force_fill(attributes or {})
        instance.save()
        
        return instance

    @classmethod
    def update_or_create(cls, attributes: Dict[str, Any], values: Dict[str, Any] = None):
        """Create or update a record matching the attributes, and fill it with values"""
        instance = cls.query().where(attributes).first()
        
        if instance:
            instance.fill(values or {})
            instance.save()
        else:
            attributes.update(values or {})
            instance = cls.create(attributes)
        
        return instance

    @classmethod
    def first_or_create(cls, attributes: Dict[str, Any], values: Dict[str, Any] = None):
        """Get the first record matching the attributes or create it"""
        instance = cls.query().where(attributes).first()
        
        if instance is None:
            attributes.update(values or {})
            instance = cls.create(attributes)
        
        return instance

    @classmethod
    def first_or_new(cls, attributes: Dict[str, Any], values: Dict[str, Any] = None):
        """Get the first record matching the attributes or instantiate it"""
        instance = cls.query().where(attributes).first()
        
        if instance is None:
            attributes.update(values or {})
            instance = cls(attributes)
        
        return instance