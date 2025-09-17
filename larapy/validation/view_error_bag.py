"""Laravel-compatible ViewErrorBag for managing multiple error bags."""

from typing import Dict, Any, Optional, Union, List
from .message_bag import MessageBag


class ViewErrorBag:
    """
    Laravel-compatible ViewErrorBag that holds multiple MessageBag instances.
    
    This class manages multiple named error bags and provides convenient
    access to the default bag through magic methods.
    """
    
    def __init__(self):
        """Initialize ViewErrorBag with empty bags dict."""
        self._bags: Dict[str, MessageBag] = {}
        self._default_bag = 'default'
    
    def hasBag(self, key: str = None) -> bool:
        """
        Check if a specific error bag exists.
        
        Args:
            key: The bag name to check for
            
        Returns:
            bool: True if the bag exists
        """
        if key is None:
            key = self._default_bag
        return key in self._bags
    
    def getBag(self, key: str = None) -> MessageBag:
        """
        Get a specific error bag or create empty one if it doesn't exist.
        
        Args:
            key: The bag name to retrieve
            
        Returns:
            MessageBag: The requested error bag
        """
        if key is None:
            key = self._default_bag
            
        if key not in self._bags:
            self._bags[key] = MessageBag()
            
        return self._bags[key]
    
    def getBags(self) -> Dict[str, MessageBag]:
        """
        Get all error bags.
        
        Returns:
            Dict[str, MessageBag]: All error bags
        """
        return self._bags.copy()
    
    def put(self, key: str, bag: Union[MessageBag, Dict, List]) -> 'ViewErrorBag':
        """
        Put an error bag into the collection.
        
        Args:
            key: The bag name
            bag: MessageBag instance or data to create one
            
        Returns:
            ViewErrorBag: Self for chaining
        """
        if isinstance(bag, MessageBag):
            self._bags[key] = bag
        elif isinstance(bag, dict):
            message_bag = MessageBag()
            for field, messages in bag.items():
                if isinstance(messages, list):
                    for message in messages:
                        message_bag.add(field, message)
                else:
                    message_bag.add(field, messages)
            self._bags[key] = message_bag
        elif isinstance(bag, list):
            # If it's a list, treat as general messages
            message_bag = MessageBag()
            for message in bag:
                message_bag.add('general', message)
            self._bags[key] = message_bag
        else:
            # Create empty bag for other types
            self._bags[key] = MessageBag()
            
        return self
    
    def count(self) -> int:
        """
        Get total count of messages in the default bag.
        
        Returns:
            int: Total number of messages in default bag
        """
        return self.getBag().count()
    
    def any(self) -> bool:
        """
        Check if the default bag has any messages.
        
        Returns:
            bool: True if default bag has messages
        """
        return self.getBag().has()
    
    def isEmpty(self) -> bool:
        """
        Check if the default bag is empty.
        
        Returns:
            bool: True if default bag is empty
        """
        return self.getBag().is_empty()
    
    def isNotEmpty(self) -> bool:
        """
        Check if the default bag is not empty.
        
        Returns:
            bool: True if default bag has messages
        """
        return not self.getBag().is_empty()
    
    def has(self, key: str) -> bool:
        """
        Check if the default bag has messages for a specific key.
        
        Args:
            key: The field key to check
            
        Returns:
            bool: True if default bag has messages for the key
        """
        return self.getBag().has(key)
    
    def first(self, key: str = None, format_str: str = None) -> Optional[str]:
        """
        Get the first message for a key from the default bag.
        
        Args:
            key: The field key (if None, gets first overall message)
            format_str: Format string for message
            
        Returns:
            Optional[str]: First message or None
        """
        return self.getBag().first(key, format_str)
    
    def get(self, key: str, format_str: str = None) -> List[str]:
        """
        Get all messages for a key from the default bag.
        
        Args:
            key: The field key
            format_str: Format string for messages
            
        Returns:
            List[str]: All messages for the key
        """
        return self.getBag().get(key, format_str)
    
    def all(self, format_str: str = None) -> Dict[str, List[str]]:
        """
        Get all messages from the default bag.
        
        Args:
            format_str: Format string for messages
            
        Returns:
            Dict[str, List[str]]: All messages grouped by key
        """
        return self.getBag().all(format_str)
    
    def toArray(self) -> Dict[str, List[str]]:
        """
        Convert the default bag to array format.
        
        Returns:
            Dict[str, List[str]]: All messages as arrays
        """
        return self.getBag().toArray()
    
    def toJson(self) -> str:
        """
        Convert the default bag to JSON format.
        
        Returns:
            str: JSON representation of messages
        """
        return self.getBag().toJson()
    
    def __getattr__(self, key: str) -> MessageBag:
        """
        Magic method to access error bags as attributes.
        
        Args:
            key: The bag name
            
        Returns:
            MessageBag: The requested error bag
        """
        return self.getBag(key)
    
    def __getitem__(self, key: str) -> MessageBag:
        """
        Magic method to access error bags as dictionary items.
        
        Args:
            key: The bag name
            
        Returns:
            MessageBag: The requested error bag
        """
        return self.getBag(key)
    
    def __setitem__(self, key: str, bag: Union[MessageBag, Dict, List]):
        """
        Magic method to set error bags as dictionary items.
        
        Args:
            key: The bag name
            bag: The error bag or data
        """
        self.put(key, bag)
    
    def __contains__(self, key: str) -> bool:
        """
        Magic method to check if a bag exists using 'in' operator.
        
        Args:
            key: The bag name
            
        Returns:
            bool: True if bag exists
        """
        return self.hasBag(key)
    
    def __bool__(self) -> bool:
        """
        Magic method for boolean evaluation (check if any bags have messages).
        
        Returns:
            bool: True if any bag has messages
        """
        return any(bag.any() for bag in self._bags.values())
    
    def __len__(self) -> int:
        """
        Magic method to get total message count across all bags.
        
        Returns:
            int: Total number of messages in all bags
        """
        return sum(bag.count() for bag in self._bags.values())
    
    def __str__(self) -> str:
        """
        String representation of the ViewErrorBag.
        
        Returns:
            str: String representation
        """
        if not self._bags:
            return "ViewErrorBag(empty)"
        
        bag_info = []
        for name, bag in self._bags.items():
            count = bag.count()
            bag_info.append(f"{name}({count})")
        
        return f"ViewErrorBag({', '.join(bag_info)})"
    
    def __repr__(self) -> str:
        """
        Developer representation of the ViewErrorBag.
        
        Returns:
            str: Developer representation
        """
        return self.__str__()
    
    @classmethod
    def make(cls, bags: Dict[str, Union[MessageBag, Dict, List]] = None) -> 'ViewErrorBag':
        """
        Create a ViewErrorBag with initial bags.
        
        Args:
            bags: Dictionary of bag names and their data
            
        Returns:
            ViewErrorBag: New instance with the provided bags
        """
        instance = cls()
        if bags:
            for name, bag_data in bags.items():
                instance.put(name, bag_data)
        return instance