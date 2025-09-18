"""Database Factory for generating test data"""

from typing import Any, Dict, List, Optional, Callable, Type, Union
from abc import ABC, abstractmethod
import random
import string
from datetime import datetime, timedelta


class Factory(ABC):
    """
    Base class for model factories
    """

    def __init__(self, count: int = None, model: Type = None):
        """Initialize the factory"""
        self.count = count or 1
        self.model = model or self._get_model_class()
        self.states = []
        self.after_making = []
        self.after_creating = []
        
    @abstractmethod
    def definition(self) -> Dict[str, Any]:
        """Define the model's default state"""
        pass

    def _get_model_class(self) -> Type:
        """Get the model class for this factory"""
        # Default implementation - should be overridden
        from ..eloquent.model import Model
        return Model

    def make(self, attributes: Dict[str, Any] = None) -> Union[object, List[object]]:
        """Create model instances without persisting them"""
        if self.count == 1:
            return self._make_instance(attributes)
        
        return [self._make_instance(attributes) for _ in range(self.count)]

    def create(self, attributes: Dict[str, Any] = None) -> Union[object, List[object]]:
        """Create and persist model instances"""
        if self.count == 1:
            return self._create_instance(attributes)
        
        return [self._create_instance(attributes) for _ in range(self.count)]

    def _make_instance(self, attributes: Dict[str, Any] = None):
        """Make a single model instance"""
        # Get the definition
        definition = self.definition()
        
        # Apply states
        for state in self.states:
            if callable(state):
                state_attrs = state(definition)
                definition.update(state_attrs)
            elif isinstance(state, dict):
                definition.update(state)
        
        # Apply provided attributes
        if attributes:
            definition.update(attributes)
        
        # Create the instance
        instance = self.model(definition)
        
        # Run after making callbacks
        for callback in self.after_making:
            callback(instance)
        
        return instance

    def _create_instance(self, attributes: Dict[str, Any] = None):
        """Create and persist a single model instance"""
        instance = self._make_instance(attributes)
        instance.save()
        
        # Run after creating callbacks
        for callback in self.after_creating:
            callback(instance)
        
        return instance

    def count(self, count: int) -> 'Factory':
        """Set the number of models to generate"""
        new_factory = self._clone()
        new_factory.count = count
        return new_factory

    def times(self, count: int) -> 'Factory':
        """Alias for count method"""
        return self.count(count)

    def state(self, state: Union[str, Dict[str, Any], Callable]) -> 'Factory':
        """Apply a state to the factory"""
        new_factory = self._clone()
        
        if isinstance(state, str):
            # Look for a state method
            state_method = getattr(self, f"state_{state}", None)
            if state_method and callable(state_method):
                new_factory.states.append(state_method)
            else:
                raise ValueError(f"State '{state}' not found on factory")
        else:
            new_factory.states.append(state)
        
        return new_factory

    def after_making(self, callback: Callable) -> 'Factory':
        """Add a callback to run after making an instance"""
        new_factory = self._clone()
        new_factory.after_making.append(callback)
        return new_factory

    def after_creating(self, callback: Callable) -> 'Factory':
        """Add a callback to run after creating an instance"""
        new_factory = self._clone()
        new_factory.after_creating.append(callback)
        return new_factory

    def sequence(self, *attributes) -> 'Factory':
        """Create a sequence of different attribute values"""
        new_factory = self._clone()
        
        def sequence_state(definition: Dict[str, Any]) -> Dict[str, Any]:
            # Get the current sequence index (would need global state)
            index = getattr(self, '_sequence_index', 0)
            self._sequence_index = index + 1
            
            # Apply the sequence value
            if len(attributes) == 1 and callable(attributes[0]):
                return attributes[0](index)
            else:
                sequence_value = attributes[index % len(attributes)]
                if callable(sequence_value):
                    return sequence_value(index)
                return sequence_value
        
        new_factory.states.append(sequence_state)
        return new_factory

    def _clone(self) -> 'Factory':
        """Clone the factory"""
        clone = self.__class__(self.count, self.model)
        clone.states = self.states.copy()
        clone.after_making = self.after_making.copy()
        clone.after_creating = self.after_creating.copy()
        return clone

    # Helper methods for generating fake data
    @staticmethod
    def fake_name() -> str:
        """Generate a fake name"""
        first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def fake_email() -> str:
        """Generate a fake email"""
        domains = ['example.com', 'test.com', 'demo.org', 'sample.net']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@{random.choice(domains)}"

    @staticmethod
    def fake_phone() -> str:
        """Generate a fake phone number"""
        return f"+1-{''.join(random.choices(string.digits, k=3))}-{''.join(random.choices(string.digits, k=3))}-{''.join(random.choices(string.digits, k=4))}"

    @staticmethod
    def fake_address() -> str:
        """Generate a fake address"""
        streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm Dr', 'Cedar Ln']
        return f"{random.randint(100, 9999)} {random.choice(streets)}"

    @staticmethod
    def fake_city() -> str:
        """Generate a fake city"""
        cities = ['Springfield', 'Franklin', 'Georgetown', 'Madison', 'Kingston']
        return random.choice(cities)

    @staticmethod
    def fake_state() -> str:
        """Generate a fake state"""
        states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        return random.choice(states)

    @staticmethod
    def fake_zip() -> str:
        """Generate a fake ZIP code"""
        return ''.join(random.choices(string.digits, k=5))

    @staticmethod
    def fake_company() -> str:
        """Generate a fake company name"""
        prefixes = ['Tech', 'Global', 'Digital', 'Smart', 'Advanced']
        suffixes = ['Solutions', 'Systems', 'Corp', 'Inc', 'LLC']
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"

    @staticmethod
    def fake_sentence(words: int = 10) -> str:
        """Generate a fake sentence"""
        word_list = [
            'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing',
            'elit', 'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore',
            'et', 'dolore', 'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam'
        ]
        sentence_words = random.choices(word_list, k=words)
        sentence = ' '.join(sentence_words)
        return sentence.capitalize() + '.'

    @staticmethod
    def fake_paragraph(sentences: int = 5) -> str:
        """Generate a fake paragraph"""
        return ' '.join([Factory.fake_sentence() for _ in range(sentences)])

    @staticmethod
    def fake_date(start_date: datetime = None, end_date: datetime = None) -> datetime:
        """Generate a fake date"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        time_between = end_date - start_date
        random_days = random.randint(0, time_between.days)
        return start_date + timedelta(days=random_days)

    @staticmethod
    def fake_future_date(days: int = 30) -> datetime:
        """Generate a fake future date"""
        return datetime.now() + timedelta(days=random.randint(1, days))

    @staticmethod
    def fake_past_date(days: int = 30) -> datetime:
        """Generate a fake past date"""
        return datetime.now() - timedelta(days=random.randint(1, days))

    @staticmethod
    def fake_boolean(true_probability: float = 0.5) -> bool:
        """Generate a fake boolean with specified probability of True"""
        return random.random() < true_probability

    @staticmethod
    def fake_number(min_value: int = 1, max_value: int = 100) -> int:
        """Generate a fake number"""
        return random.randint(min_value, max_value)

    @staticmethod
    def fake_float(min_value: float = 0.0, max_value: float = 100.0, 
                   decimals: int = 2) -> float:
        """Generate a fake float"""
        value = random.uniform(min_value, max_value)
        return round(value, decimals)

    @staticmethod
    def fake_uuid() -> str:
        """Generate a fake UUID"""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def fake_choice(choices: List[Any]) -> Any:
        """Choose a random item from a list"""
        return random.choice(choices)

    @staticmethod
    def fake_choices(choices: List[Any], count: int) -> List[Any]:
        """Choose multiple random items from a list"""
        return random.choices(choices, k=count)

    @staticmethod
    def fake_sample(choices: List[Any], count: int) -> List[Any]:
        """Sample items from a list without replacement"""
        return random.sample(choices, min(count, len(choices)))

    @classmethod
    def new(cls, *args, **kwargs) -> 'Factory':
        """Create a new factory instance"""
        return cls(*args, **kwargs)

    @classmethod
    def factory_for_model(cls, model: Type) -> 'Factory':
        """Create a factory for a specific model"""
        return cls(model=model)