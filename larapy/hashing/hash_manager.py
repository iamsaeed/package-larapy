"""
Password Hashing Service

Provides Laravel-style password hashing using bcrypt and Argon2.
Supports checking passwords and detecting if rehashing is needed.
"""

import bcrypt
from typing import Optional, Union
from passlib.hash import argon2


class BcryptHasher:
    """
    Bcrypt password hasher
    """
    
    def __init__(self, rounds: int = 12):
        """
        Initialize bcrypt hasher
        
        Args:
            rounds: Number of rounds for bcrypt (default: 12)
        """
        self.rounds = rounds
    
    def make(self, value: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            value: Plain text password
            
        Returns:
            str: Hashed password
        """
        password_bytes = value.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def check(self, value: str, hashed: str) -> bool:
        """
        Check if a password matches its hash
        
        Args:
            value: Plain text password
            hashed: Hashed password
            
        Returns:
            bool: True if password matches
        """
        try:
            password_bytes = value.encode('utf-8')
            hashed_bytes = hashed.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
    def needs_rehash(self, hashed: str) -> bool:
        """
        Check if a hash needs to be rehashed (different cost)
        
        Args:
            hashed: Hashed password
            
        Returns:
            bool: True if rehashing is needed
        """
        try:
            # Extract current cost from hash
            current_cost = int(hashed.split('$')[2])
            return current_cost != self.rounds
        except Exception:
            return True  # If we can't parse, assume rehash is needed


class Argon2Hasher:
    """
    Argon2 password hasher
    """
    
    def __init__(self, memory_cost: int = 65536, time_cost: int = 4, parallelism: int = 3):
        """
        Initialize Argon2 hasher
        
        Args:
            memory_cost: Memory cost in KiB (default: 64MB)
            time_cost: Time cost/iterations (default: 4)
            parallelism: Parallelism factor (default: 3)
        """
        self.memory_cost = memory_cost
        self.time_cost = time_cost
        self.parallelism = parallelism
    
    def make(self, value: str) -> str:
        """
        Hash a password using Argon2
        
        Args:
            value: Plain text password
            
        Returns:
            str: Hashed password
        """
        return argon2.using(
            memory_cost=self.memory_cost,
            time_cost=self.time_cost,
            parallelism=self.parallelism
        ).hash(value)
    
    def check(self, value: str, hashed: str) -> bool:
        """
        Check if a password matches its hash
        
        Args:
            value: Plain text password
            hashed: Hashed password
            
        Returns:
            bool: True if password matches
        """
        try:
            return argon2.verify(value, hashed)
        except Exception:
            return False
    
    def needs_rehash(self, hashed: str) -> bool:
        """
        Check if a hash needs to be rehashed (different parameters)
        
        Args:
            hashed: Hashed password
            
        Returns:
            bool: True if rehashing is needed
        """
        try:
            return argon2.using(
                memory_cost=self.memory_cost,
                time_cost=self.time_cost,
                parallelism=self.parallelism
            ).needs_update(hashed)
        except Exception:
            return True


class HashManager:
    """
    Password hash manager that supports multiple drivers
    """
    
    DRIVERS = {
        'bcrypt': BcryptHasher,
        'argon2': Argon2Hasher,
    }
    
    def __init__(self, driver: str = 'bcrypt', **options):
        """
        Initialize hash manager
        
        Args:
            driver: Hash driver ('bcrypt' or 'argon2')
            **options: Driver-specific options
        """
        self.driver_name = driver
        self.hasher = self._create_hasher(driver, **options)
    
    def _create_hasher(self, driver: str, **options):
        """Create hasher instance"""
        if driver not in self.DRIVERS:
            raise ValueError(f"Unsupported hash driver: {driver}")
        
        hasher_class = self.DRIVERS[driver]
        return hasher_class(**options)
    
    def make(self, value: str) -> str:
        """
        Hash a value
        
        Args:
            value: Value to hash
            
        Returns:
            str: Hashed value
        """
        return self.hasher.make(value)
    
    def check(self, value: str, hashed: str) -> bool:
        """
        Check if a value matches its hash
        
        Args:
            value: Plain value
            hashed: Hashed value
            
        Returns:
            bool: True if value matches
        """
        return self.hasher.check(value, hashed)
    
    def needs_rehash(self, hashed: str) -> bool:
        """
        Check if a hash needs rehashing
        
        Args:
            hashed: Hashed value
            
        Returns:
            bool: True if rehashing is needed
        """
        return self.hasher.needs_rehash(hashed)
    
    def get_driver(self) -> str:
        """Get the current driver name"""
        return self.driver_name


# Default hash manager instance
_default_hash_manager = None


def get_hash_manager() -> HashManager:
    """Get the default hash manager instance"""
    global _default_hash_manager
    if _default_hash_manager is None:
        _default_hash_manager = HashManager('bcrypt')
    return _default_hash_manager