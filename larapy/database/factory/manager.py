"""Factory Manager for handling model factories"""

from typing import Type, Dict, Any, Optional, Callable
from .factory import Factory


class FactoryManager:
    """
    Manager for handling model factories
    """

    def __init__(self):
        """Initialize the factory manager"""
        self._factories = {}
        self._states = {}
        self._callbacks = {}

    def define(self, model: Type, factory_class: Type[Factory] = None, 
               definition: Callable = None) -> Factory:
        """Define a factory for a model"""
        if factory_class is None and definition is None:
            raise ValueError("Either factory_class or definition must be provided")

        if factory_class:
            factory = factory_class(model=model)
        else:
            # Create a dynamic factory
            factory = self._create_dynamic_factory(model, definition)

        self._factories[model] = factory
        return factory

    def _create_dynamic_factory(self, model: Type, definition: Callable) -> Factory:
        """Create a dynamic factory from a definition function"""
        class DynamicFactory(Factory):
            def __init__(self, **kwargs):
                super().__init__(model=model, **kwargs)

            def definition(self) -> Dict[str, Any]:
                return definition()

            def _get_model_class(self) -> Type:
                return model

        return DynamicFactory()

    def state(self, model: Type, state_name: str, 
              attributes: Dict[str, Any] = None, 
              callback: Callable = None) -> 'FactoryManager':
        """Define a state for a model factory"""
        if model not in self._states:
            self._states[model] = {}

        if attributes:
            self._states[model][state_name] = attributes
        elif callback:
            self._states[model][state_name] = callback
        else:
            raise ValueError("Either attributes or callback must be provided")

        return self

    def after_making(self, model: Type, callback: Callable) -> 'FactoryManager':
        """Register a callback to run after making a model"""
        if model not in self._callbacks:
            self._callbacks[model] = {'after_making': [], 'after_creating': []}

        self._callbacks[model]['after_making'].append(callback)
        return self

    def after_creating(self, model: Type, callback: Callable) -> 'FactoryManager':
        """Register a callback to run after creating a model"""
        if model not in self._callbacks:
            self._callbacks[model] = {'after_making': [], 'after_creating': []}

        self._callbacks[model]['after_creating'].append(callback)
        return self

    def of(self, model: Type, count: int = 1) -> Factory:
        """Get a factory for a model"""
        if model not in self._factories:
            # Try to auto-discover the factory
            factory = self._auto_discover_factory(model)
            if factory:
                self._factories[model] = factory
            else:
                raise ValueError(f"No factory defined for model {model.__name__}")

        factory = self._factories[model]
        
        # Clone the factory with the specified count
        cloned_factory = factory._clone()
        cloned_factory.count = count

        # Apply any registered callbacks
        if model in self._callbacks:
            for callback in self._callbacks[model]['after_making']:
                cloned_factory = cloned_factory.after_making(callback)
            
            for callback in self._callbacks[model]['after_creating']:
                cloned_factory = cloned_factory.after_creating(callback)

        return cloned_factory

    def _auto_discover_factory(self, model: Type) -> Optional[Factory]:
        """Try to auto-discover a factory for the model"""
        # Look for a factory class named ModelFactory
        factory_name = f"{model.__name__}Factory"
        
        # Try to import from common factory locations
        try:
            # Try database.factories module
            import importlib
            factories_module = importlib.import_module('database.factories')
            
            if hasattr(factories_module, factory_name):
                factory_class = getattr(factories_module, factory_name)
                return factory_class(model=model)
        except ImportError:
            pass

        # Try app.factories module
        try:
            import importlib
            factories_module = importlib.import_module('app.factories')
            
            if hasattr(factories_module, factory_name):
                factory_class = getattr(factories_module, factory_name)
                return factory_class(model=model)
        except ImportError:
            pass

        return None

    def create(self, model: Type, count: int = 1, attributes: Dict[str, Any] = None):
        """Create model instances"""
        return self.of(model, count).create(attributes)

    def make(self, model: Type, count: int = 1, attributes: Dict[str, Any] = None):
        """Make model instances without persisting"""
        return self.of(model, count).make(attributes)

    def reset(self):
        """Reset all registered factories"""
        self._factories.clear()
        self._states.clear()
        self._callbacks.clear()

    def has_factory(self, model: Type) -> bool:
        """Check if a factory is registered for a model"""
        return model in self._factories or self._auto_discover_factory(model) is not None

    def get_factories(self) -> Dict[Type, Factory]:
        """Get all registered factories"""
        return self._factories.copy()


# Global factory manager instance
_factory_manager = FactoryManager()


def factory(model: Type = None, count: int = 1):
    """Get a factory for a model or define a new factory"""
    if model is None:
        # Return the factory manager for method chaining
        return _factory_manager
    
    return _factory_manager.of(model, count)


def define_factory(model: Type, factory_class: Type[Factory] = None, 
                  definition: Callable = None) -> Factory:
    """Define a factory for a model"""
    return _factory_manager.define(model, factory_class, definition)


def state(model: Type, state_name: str, attributes: Dict[str, Any] = None, 
         callback: Callable = None):
    """Define a state for a model factory"""
    return _factory_manager.state(model, state_name, attributes, callback)


def after_making(model: Type, callback: Callable):
    """Register a callback to run after making a model"""
    return _factory_manager.after_making(model, callback)


def after_creating(model: Type, callback: Callable):
    """Register a callback to run after creating a model"""
    return _factory_manager.after_creating(model, callback)


def create(model: Type, count: int = 1, attributes: Dict[str, Any] = None):
    """Create model instances"""
    return _factory_manager.create(model, count, attributes)


def make(model: Type, count: int = 1, attributes: Dict[str, Any] = None):
    """Make model instances without persisting"""
    return _factory_manager.make(model, count, attributes)


def reset_factories():
    """Reset all registered factories"""
    _factory_manager.reset()