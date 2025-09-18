"""Model Events System for Eloquent"""

from typing import Dict, List, Callable, Any, Optional, TYPE_CHECKING
import inspect

if TYPE_CHECKING:
    from .model import Model


class ModelEvent:
    """Represents a model event"""
    
    def __init__(self, event_name: str, model: 'Model'):
        self.event_name = event_name
        self.model = model
        self.halt = False

    def halt_event(self):
        """Halt the event"""
        self.halt = True


class ModelEvents:
    """
    Handles model events and observers
    """
    
    # Global event listeners
    _listeners: Dict[str, Dict[str, List[Callable]]] = {}
    
    # Observer classes
    _observers: Dict[str, List] = {}
    
    # Model event names
    EVENTS = [
        'creating', 'created',
        'updating', 'updated', 
        'saving', 'saved',
        'deleting', 'deleted',
        'restoring', 'restored',
        'replicating'
    ]

    @classmethod
    def register_listener(cls, model_class: str, event: str, callback: Callable):
        """Register an event listener for a model"""
        if model_class not in cls._listeners:
            cls._listeners[model_class] = {}
        
        if event not in cls._listeners[model_class]:
            cls._listeners[model_class][event] = []
        
        cls._listeners[model_class][event].append(callback)

    @classmethod
    def register_observer(cls, model_class: str, observer_class):
        """Register an observer for a model"""
        if model_class not in cls._observers:
            cls._observers[model_class] = []
        
        cls._observers[model_class].append(observer_class)
        
        # Register methods from observer as listeners
        observer_instance = observer_class()
        for event in cls.EVENTS:
            if hasattr(observer_instance, event):
                method = getattr(observer_instance, event)
                cls.register_listener(model_class, event, method)

    @classmethod
    def fire_event(cls, model: 'Model', event: str, halt: bool = True) -> bool:
        """Fire a model event"""
        model_class = model.__class__.__name__
        
        # Create event object
        event_obj = ModelEvent(event, model)
        
        # Get listeners for this model and event
        listeners = cls._listeners.get(model_class, {}).get(event, [])
        
        # Fire each listener
        for listener in listeners:
            try:
                # Get listener signature
                sig = inspect.signature(listener)
                params = list(sig.parameters.keys())
                
                # Call with appropriate parameters
                if len(params) == 0:
                    result = listener()
                elif len(params) == 1:
                    result = listener(model)
                else:
                    result = listener(model, event_obj)
                
                # If result is False and we should halt, stop execution
                if halt and result is False:
                    return False
                    
            except Exception as e:
                # Log the error but continue
                print(f"Error firing event {event} for {model_class}: {e}")
                if halt:
                    return False
        
        return True

    @classmethod
    def clear_listeners(cls, model_class: str = None, event: str = None):
        """Clear event listeners"""
        if model_class is None:
            cls._listeners.clear()
        elif event is None:
            if model_class in cls._listeners:
                del cls._listeners[model_class]
        else:
            if model_class in cls._listeners and event in cls._listeners[model_class]:
                del cls._listeners[model_class][event]

    @classmethod
    def clear_observers(cls, model_class: str = None):
        """Clear observers"""
        if model_class is None:
            cls._observers.clear()
        else:
            if model_class in cls._observers:
                del cls._observers[model_class]


class HasEvents:
    """
    Mixin to add event functionality to models
    """
    
    def fire_model_event(self, event: str, halt: bool = True) -> bool:
        """Fire a model event"""
        return ModelEvents.fire_event(self, event, halt)

    @classmethod
    def observe(cls, observer_class):
        """Register an observer for this model"""
        ModelEvents.register_observer(cls.__name__, observer_class)

    @classmethod
    def creating(cls, callback: Callable):
        """Register a creating event listener"""
        ModelEvents.register_listener(cls.__name__, 'creating', callback)

    @classmethod
    def created(cls, callback: Callable):
        """Register a created event listener"""
        ModelEvents.register_listener(cls.__name__, 'created', callback)

    @classmethod
    def updating(cls, callback: Callable):
        """Register an updating event listener"""
        ModelEvents.register_listener(cls.__name__, 'updating', callback)

    @classmethod
    def updated(cls, callback: Callable):
        """Register an updated event listener"""
        ModelEvents.register_listener(cls.__name__, 'updated', callback)

    @classmethod
    def saving(cls, callback: Callable):
        """Register a saving event listener"""
        ModelEvents.register_listener(cls.__name__, 'saving', callback)

    @classmethod
    def saved(cls, callback: Callable):
        """Register a saved event listener"""
        ModelEvents.register_listener(cls.__name__, 'saved', callback)

    @classmethod
    def deleting(cls, callback: Callable):
        """Register a deleting event listener"""
        ModelEvents.register_listener(cls.__name__, 'deleting', callback)

    @classmethod
    def deleted(cls, callback: Callable):
        """Register a deleted event listener"""
        ModelEvents.register_listener(cls.__name__, 'deleted', callback)

    @classmethod
    def restoring(cls, callback: Callable):
        """Register a restoring event listener"""
        ModelEvents.register_listener(cls.__name__, 'restoring', callback)

    @classmethod
    def restored(cls, callback: Callable):
        """Register a restored event listener"""
        ModelEvents.register_listener(cls.__name__, 'restored', callback)