"""Soft Deletes concern for Eloquent models"""

from typing import Optional, List
from datetime import datetime


class SoftDeletes:
    """
    Provides soft delete functionality for Eloquent models
    """

    # The name of the "deleted at" column
    deleted_at = 'deleted_at'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def force_delete(self) -> bool:
        """Force a hard delete on a soft deleted model"""
        return super().delete()

    def delete(self) -> bool:
        """Delete the model from the database (soft delete)"""
        if self.get_key() is None:
            return False

        if self.fire_model_event('deleting') == False:
            return False

        # Touch the owning relations
        self.touch_owners()

        # Perform the soft delete
        self.run_soft_delete()

        # Fire deleted event
        self.fire_model_event('deleted', False)

        return True

    def run_soft_delete(self):
        """Perform the actual soft delete on the model"""
        query = self.new_query_without_scopes().where(
            self.get_key_name(), self.get_key()
        )

        time = self.fresh_timestamp()
        
        columns = {self.get_deleted_at_column(): self.from_datetime(time)}

        self.set_attribute(self.get_deleted_at_column(), time)

        if self.uses_timestamps() and not self.is_dirty(self.get_updated_at_column()):
            self.set_updated_at(time)
            columns[self.get_updated_at_column()] = self.from_datetime(time)

        query.update(columns)

        self.sync_original()

    def restore(self) -> bool:
        """Restore a soft-deleted model instance"""
        if self.fire_model_event('restoring') == False:
            return False

        # Restore by setting deleted_at to null
        self.set_attribute(self.get_deleted_at_column(), None)

        # Save the model
        result = self.save()

        if result:
            self.fire_model_event('restored', False)

        return result

    def trashed(self) -> bool:
        """Determine if the model instance has been soft-deleted"""
        return self.get_attribute(self.get_deleted_at_column()) is not None

    def get_deleted_at_column(self) -> str:
        """Get the name of the "deleted at" column"""
        return getattr(self, 'deleted_at', 'deleted_at')

    def get_qualified_deleted_at_column(self) -> str:
        """Get the fully qualified "deleted at" column"""
        return f"{self.get_table()}.{self.get_deleted_at_column()}"

    def new_query_without_scopes(self):
        """Get a new query builder that doesn't have any global scopes or constraints"""
        builder = super().new_query_without_scopes()
        
        # Don't apply soft delete constraint
        return builder

    def new_query(self):
        """Get a new query builder for the model's table"""
        builder = super().new_query()
        
        # Apply soft delete constraint
        return self.apply_soft_delete_scope(builder)

    def apply_soft_delete_scope(self, builder):
        """Apply the soft delete scope to the Eloquent builder"""
        return builder.where_null(self.get_qualified_deleted_at_column())

    @classmethod
    def with_trashed(cls):
        """Get a new query builder that includes soft deleted models"""
        return cls().new_query_without_scopes()

    @classmethod
    def only_trashed(cls):
        """Get a new query builder that only includes soft deleted models"""
        return cls().new_query_without_scopes().where_not_null(
            cls().get_qualified_deleted_at_column()
        )

    @classmethod
    def restore_all(cls, ids: List = None):
        """Restore multiple soft-deleted models"""
        query = cls.only_trashed()
        
        if ids:
            query = query.where_in(cls().get_key_name(), ids)
        
        return query.update({cls().get_deleted_at_column(): None})

    @classmethod
    def force_delete_all(cls, ids: List = None):
        """Force delete multiple models"""
        query = cls.with_trashed()
        
        if ids:
            query = query.where_in(cls().get_key_name(), ids)
        
        # Get the actual delete method from the query builder
        return query.delete()

    def get_boot_soft_deletes_trait_methods(self):
        """Get the methods that should be called when booting the soft deletes trait"""
        return ['boot_soft_deletes']

    @classmethod
    def boot_soft_deletes(cls):
        """Boot the soft deleting trait for a model"""
        # This would register global scopes for soft deletes
        # For now, we'll just ensure the trait is booted
        pass