import inspect
from typing import Any, Dict, List, Callable, Optional, Type
from abc import ABC, abstractmethod

class ContainerContract(ABC):
    @abstractmethod
    def bind(self, abstract: str, concrete: Any = None, shared: bool = False):
        pass
    
    @abstractmethod
    def resolve(self, abstract: str):
        pass

class Container(ContainerContract):
    """Service Container - IoC Container implementation like Laravel's Container"""
    
    def __init__(self):
        # The container's bindings
        self._bindings: Dict[str, Dict] = {}
        
        # The container's shared instances (singletons)
        self._instances: Dict[str, Any] = {}
        
        # The registered type aliases
        self._aliases: Dict[str, str] = {}
        
        # The extension closures for services
        self._extenders: Dict[str, List[Callable]] = {}
        
        # The contextual binding map
        self._contextual: Dict[str, Dict] = {}
        
        # All registered tags
        self._tags: Dict[str, List[str]] = {}
        
        # Global resolving callbacks
        self._resolving_callbacks: Dict[str, List[Callable]] = {}
        
        # Current instance
        self._instance = None
        
    @classmethod
    def get_instance(cls):
        """Get the globally available container instance"""
        if not hasattr(cls, '_global_instance'):
            cls._global_instance = cls()
        return cls._global_instance
    
    def bind(self, abstract: str, concrete: Any = None, shared: bool = False):
        """Register a binding with the container"""
        # Remove existing instance if it's a singleton
        if abstract in self._instances:
            del self._instances[abstract]
        
        # If no concrete given, make it abstract
        if concrete is None:
            concrete = abstract
            
        # Store the binding
        self._bindings[abstract] = {
            'concrete': concrete,
            'shared': shared
        }
        
        # If binding is aliased, register alias
        if abstract != concrete and isinstance(concrete, str):
            self.alias(concrete, abstract)
    
    def singleton(self, abstract: str, concrete: Any = None):
        """Register a shared binding in the container"""
        self.bind(abstract, concrete, True)
    
    def instance(self, abstract: str, instance: Any):
        """Register an existing instance as shared in the container"""
        self._instances[abstract] = instance
        return instance
    
    def resolve(self, abstract: str):
        """Resolve the given type from the container"""
        abstract = self.get_alias(abstract)
        
        # If we have a cached instance, return it
        if abstract in self._instances:
            return self._instances[abstract]
        
        # Get the concrete implementation
        concrete = self.get_concrete(abstract)
        
        # We're ready to instantiate
        if self.is_buildable(concrete, abstract):
            object_instance = self.build(concrete)
        else:
            object_instance = self.resolve(concrete)
        
        # If we're supposed to return a singleton, cache it
        if self.is_shared(abstract):
            self._instances[abstract] = object_instance
        
        # Fire resolving callbacks
        self.fire_resolving_callbacks(abstract, object_instance)
        
        return object_instance
    
    def build(self, concrete: Any):
        """Instantiate a concrete instance of the given type"""
        # If concrete is a closure, call it
        if callable(concrete) and not inspect.isclass(concrete):
            return concrete(self)
        
        # If it's a class, try to instantiate it
        if inspect.isclass(concrete):
            return self.resolve_class(concrete)
        
        return concrete
    
    def resolve_class(self, concrete: Type):
        """Resolve all dependencies for a class constructor"""
        try:
            # Get constructor signature
            sig = inspect.signature(concrete.__init__)
            dependencies = []
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                if param.annotation != inspect.Parameter.empty:
                    # Try to resolve from container
                    try:
                        if hasattr(param.annotation, '__name__'):
                            dependency = self.resolve(param.annotation.__name__)
                        else:
                            dependency = self.resolve(str(param.annotation))
                        dependencies.append(dependency)
                    except:
                        if param.default != inspect.Parameter.empty:
                            dependencies.append(param.default)
                        else:
                            raise Exception(f"Cannot resolve dependency {param_name} for {concrete.__name__}")
                else:
                    if param.default != inspect.Parameter.empty:
                        dependencies.append(param.default)
                    else:
                        raise Exception(f"Cannot resolve dependency {param_name} for {concrete.__name__}")
            
            return concrete(*dependencies)
            
        except Exception as e:
            raise Exception(f"Target class [{concrete.__name__}] is not instantiable: {str(e)}")
    
    def get_concrete(self, abstract: str):
        """Get the concrete type for a given abstract"""
        if abstract not in self._bindings:
            return abstract
        
        return self._bindings[abstract]['concrete']
    
    def is_buildable(self, concrete: Any, abstract: str) -> bool:
        """Determine if the given concrete is buildable"""
        return concrete == abstract or callable(concrete)
    
    def is_shared(self, abstract: str) -> bool:
        """Determine if a given type is shared"""
        return (abstract in self._instances or 
                (abstract in self._bindings and self._bindings[abstract]['shared']))
    
    def alias(self, abstract: str, alias: str):
        """Alias a type to a different name"""
        self._aliases[alias] = abstract
    
    def get_alias(self, abstract: str) -> str:
        """Get the alias for an abstract if available"""
        return self._aliases.get(abstract, abstract)
    
    def tag(self, abstracts: List[str], tags: List[str]):
        """Assign a set of tags to a given binding"""
        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = []
            
            for abstract in abstracts:
                if abstract not in self._tags[tag]:
                    self._tags[tag].append(abstract)
    
    def tagged(self, tag: str) -> List[Any]:
        """Resolve all bindings for a given tag"""
        if tag not in self._tags:
            return []
        
        return [self.resolve(abstract) for abstract in self._tags[tag]]
    
    def fire_resolving_callbacks(self, abstract: str, instance: Any):
        """Fire all callbacks for the given abstract type"""
        if abstract in self._resolving_callbacks:
            for callback in self._resolving_callbacks[abstract]:
                callback(instance, self)
    
    def resolving(self, abstract: str, callback: Callable):
        """Register a resolving callback"""
        if abstract not in self._resolving_callbacks:
            self._resolving_callbacks[abstract] = []
        self._resolving_callbacks[abstract].append(callback)

    def __getitem__(self, key: str):
        """Allow array access to the container"""
        return self.resolve(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow array access to the container"""
        self.bind(key, value)
