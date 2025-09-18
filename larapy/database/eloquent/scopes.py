"""Global Scopes for Eloquent models"""

from typing import Dict, List, Any, Optional, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .model import Model
    from ..query.builder import Builder


class Scope(ABC):
    """Abstract base class for global scopes"""
    
    @abstractmethod
    def apply(self, builder: 'Builder', model: 'Model'):
        """Apply the scope to a given Eloquent query builder"""
        pass


class SoftDeletingScope(Scope):
    """Global scope for soft deleting models"""
    
    def apply(self, builder: 'Builder', model: 'Model'):
        """Apply the soft deleting scope to the Eloquent builder"""
        builder.where_null(model.get_qualified_deleted_at_column())

    def extend(self, builder: 'Builder'):
        """Extend the query builder with the scope methods"""
        for method in ['with_trashed', 'without_trashed', 'only_trashed']:
            builder.macro(method, getattr(self, f'_{method}'))

    def _with_trashed(self, builder: 'Builder'):
        """Include soft deleted models in the query"""
        return builder.without_global_scope(self)

    def _without_trashed(self, builder: 'Builder'):
        """Exclude soft deleted models from the query"""
        return builder.with_global_scope(self.__class__.__name__, self)

    def _only_trashed(self, builder: 'Builder'):
        """Only include soft deleted models in the query"""
        return builder.without_global_scope(self).where_not_null(
            builder.get_model().get_qualified_deleted_at_column()
        )


class GlobalScopes:
    """
    Manages global scopes for Eloquent models
    """
    
    # Registered global scopes
    _scopes: Dict[str, Dict[str, Scope]] = {}

    @classmethod
    def register(cls, model_class: str, scope_name: str, scope: Scope):
        """Register a global scope for a model"""
        if model_class not in cls._scopes:
            cls._scopes[model_class] = {}
        
        cls._scopes[model_class][scope_name] = scope

    @classmethod
    def get_scopes(cls, model_class: str) -> Dict[str, Scope]:
        """Get all global scopes for a model"""
        return cls._scopes.get(model_class, {})

    @classmethod
    def get_scope(cls, model_class: str, scope_name: str) -> Optional[Scope]:
        """Get a specific global scope for a model"""
        return cls._scopes.get(model_class, {}).get(scope_name)

    @classmethod
    def remove(cls, model_class: str, scope_name: str = None):
        """Remove global scope(s) for a model"""
        if model_class not in cls._scopes:
            return
        
        if scope_name is None:
            del cls._scopes[model_class]
        else:
            if scope_name in cls._scopes[model_class]:
                del cls._scopes[model_class][scope_name]

    @classmethod
    def apply_scopes(cls, builder: 'Builder', model: 'Model'):
        """Apply all global scopes to a query builder"""
        model_class = model.__class__.__name__
        scopes = cls.get_scopes(model_class)
        
        for scope_name, scope in scopes.items():
            scope.apply(builder, model)
            # Store applied scope on builder for removal later
            builder._applied_global_scopes = getattr(builder, '_applied_global_scopes', {})
            builder._applied_global_scopes[scope_name] = scope

    @classmethod
    def clear_all(cls):
        """Clear all registered global scopes"""
        cls._scopes.clear()


class HasGlobalScopes:
    """
    Mixin to add global scope functionality to models
    """
    
    @classmethod
    def add_global_scope(cls, scope_name: str, scope: Scope):
        """Add a global scope to this model"""
        GlobalScopes.register(cls.__name__, scope_name, scope)

    @classmethod
    def remove_global_scope(cls, scope_name: str):
        """Remove a global scope from this model"""
        GlobalScopes.remove(cls.__name__, scope_name)

    def new_query(self):
        """Get a new query builder for the model's table with global scopes applied"""
        builder = super().new_query() if hasattr(super(), 'new_query') else self._new_base_query_builder()
        
        # Apply global scopes
        GlobalScopes.apply_scopes(builder, self)
        
        return builder

    def new_query_without_scopes(self):
        """Get a new query builder that doesn't have any global scopes"""
        return super().new_query() if hasattr(super(), 'new_query') else self._new_base_query_builder()

    def new_query_without_scope(self, scope_name: str):
        """Get a new query builder without a specific global scope"""
        builder = self.new_query_without_scopes()
        
        # Apply all scopes except the specified one
        model_class = self.__class__.__name__
        scopes = GlobalScopes.get_scopes(model_class)
        
        for name, scope in scopes.items():
            if name != scope_name:
                scope.apply(builder, self)
        
        return builder


class QueryScope:
    """
    Local query scope functionality
    """
    
    @staticmethod
    def scope_of_type(builder: 'Builder', type_value: str):
        """Example scope: filter by type"""
        return builder.where('type', type_value)

    @staticmethod
    def scope_active(builder: 'Builder'):
        """Example scope: filter active records"""
        return builder.where('active', True)

    @staticmethod
    def scope_published(builder: 'Builder'):
        """Example scope: filter published records"""
        return builder.where('published', True)


class HasQueryScopes:
    """
    Mixin to add query scope functionality to models
    """
    
    def __getattr__(self, name):
        """Handle dynamic scope method calls"""
        if name.startswith('scope_'):
            # This is a scope method call on the model class
            scope_name = name[6:]  # Remove 'scope_' prefix
            
            def scope_wrapper(*args, **kwargs):
                builder = self.new_query()
                scope_method = getattr(self, f'scope_{scope_name}', None)
                if scope_method:
                    return scope_method(builder, *args, **kwargs)
                return builder
            
            return scope_wrapper
        
        # Try to call parent __getattr__ if it exists
        if hasattr(super(), '__getattr__'):
            return super().__getattr__(name)
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")