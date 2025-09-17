"""Message bag implementation"""

from typing import Dict, List, Optional, Union, Any
from .contracts import MessageBagContract


class MessageBag(MessageBagContract):
    """Container for validation error messages"""

    def __init__(self, messages: Optional[Dict[str, Union[str, List[str]]]] = None):
        """Create a new message bag instance"""
        self.messages: Dict[str, List[str]] = {}

        if messages:
            for key, value in messages.items():
                if isinstance(value, str):
                    self.messages[key] = [value]
                elif isinstance(value, list):
                    self.messages[key] = value
                else:
                    self.messages[key] = [str(value)]

    def add(self, key: str, message: str) -> None:
        """Add a message to the bag"""
        if key not in self.messages:
            self.messages[key] = []
        self.messages[key].append(message)

    def merge(self, messages: Union[MessageBagContract, Dict[str, List[str]]]) -> None:
        """Merge another message bag or dictionary into this bag"""
        if isinstance(messages, MessageBagContract):
            messages = messages.to_dict()

        for key, value in messages.items():
            if key not in self.messages:
                self.messages[key] = []
            if isinstance(value, list):
                self.messages[key].extend(value)
            else:
                self.messages[key].append(str(value))

    def has(self, key: Optional[str] = None) -> bool:
        """Check if the bag has any messages for a key"""
        if key is None:
            return len(self.messages) > 0

        return key in self.messages and len(self.messages[key]) > 0

    def first(self, key: Optional[str] = None, format_string: Optional[str] = None) -> Optional[str]:
        """Get the first message from the bag for a key"""
        if key is None:
            # Get the first message from any key
            for messages_list in self.messages.values():
                if messages_list:
                    message = messages_list[0]
                    return self._format_message(message, format_string)
            return None

        if key in self.messages and self.messages[key]:
            message = self.messages[key][0]
            return self._format_message(message, format_string)

        return None

    def get(self, key: str, format_string: Optional[str] = None) -> List[str]:
        """Get all messages for a key"""
        if key not in self.messages:
            return []

        messages = self.messages[key]
        if format_string:
            return [self._format_message(msg, format_string) for msg in messages]
        return messages.copy()

    def all(self, format_string: Optional[str] = None) -> Dict[str, List[str]]:
        """Get all messages"""
        if format_string:
            formatted = {}
            for key, messages in self.messages.items():
                formatted[key] = [self._format_message(msg, format_string) for msg in messages]
            return formatted

        return {k: v.copy() for k, v in self.messages.items()}

    def count(self) -> int:
        """Get the number of messages in the bag"""
        return sum(len(messages) for messages in self.messages.values())

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert the message bag to a dictionary"""
        return self.all()

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable format"""
        return {
            'message': self.first() or 'The given data was invalid.',
            'errors': self.to_dict()
        }

    def is_empty(self) -> bool:
        """Check if the message bag is empty"""
        return self.count() == 0

    def any(self) -> bool:
        """
        Check if the message bag has any messages.
        Laravel-compatible alias for has().
        
        Returns:
            bool: True if bag has any messages
        """
        return self.has()

    def keys(self) -> List[str]:
        """Get all the keys in the message bag"""
        return list(self.messages.keys())

    def _format_message(self, message: str, format_string: Optional[str]) -> str:
        """Format a message with the given format string"""
        if format_string is None:
            return message
        return format_string.replace(':message', message)

    def __len__(self) -> int:
        """Get the number of messages"""
        return self.count()

    def __bool__(self) -> bool:
        """Check if the bag has any messages"""
        return not self.is_empty()

    def __iter__(self):
        """Iterate over all messages"""
        for key, messages in self.messages.items():
            for message in messages:
                yield key, message

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the bag"""
        return self.has(key)

    def __getitem__(self, key: str) -> List[str]:
        """Get messages for a key"""
        return self.get(key)

    def __setitem__(self, key: str, value: Union[str, List[str]]) -> None:
        """Set messages for a key"""
        if isinstance(value, str):
            self.messages[key] = [value]
        elif isinstance(value, list):
            self.messages[key] = value
        else:
            self.messages[key] = [str(value)]

    def __repr__(self) -> str:
        """String representation of the message bag"""
        return f"MessageBag({self.messages})"