"""
Hash Facade

Provides easy access to password hashing functionality.
"""

from larapy.support.facades.facade import Facade
from larapy.hashing.hash_manager import get_hash_manager


class Hash(Facade):
    """
    Hash Facade
    """
    
    @staticmethod
    def get_facade_accessor():
        return get_hash_manager()
    
    @classmethod
    def make(cls, value: str):
        """Hash a value"""
        return cls.get_facade_accessor().make(value)
    
    @classmethod
    def check(cls, value: str, hashed: str):
        """Check if a value matches its hash"""
        return cls.get_facade_accessor().check(value, hashed)
    
    @classmethod
    def needs_rehash(cls, hashed: str):
        """Check if a hash needs rehashing"""
        return cls.get_facade_accessor().needs_rehash(hashed)
    
    @classmethod
    def driver(cls):
        """Get the current hash driver"""
        return cls.get_facade_accessor().get_driver()