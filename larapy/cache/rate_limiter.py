"""
Rate Limiting Service

Implements token bucket algorithm for rate limiting requests.
Supports per-user, per-IP, and custom key rate limiting.
"""

import time
from typing import Optional, Dict, Any, Tuple
from flask import request, current_app, g


class RateLimiter:
    """
    Token bucket rate limiter implementation
    """
    
    def __init__(self, cache_store=None):
        """
        Initialize rate limiter
        
        Args:
            cache_store: Cache backend for storing rate limit data
        """
        self.cache = cache_store or {}  # Simple dict cache for now
    
    def attempt(self, key: str, max_attempts: int, decay_minutes: int = 1) -> bool:
        """
        Attempt to perform an action within rate limits
        
        Args:
            key: Unique key for rate limiting
            max_attempts: Maximum attempts allowed
            decay_minutes: Time window in minutes
            
        Returns:
            bool: True if attempt is allowed
        """
        now = time.time()
        decay_seconds = decay_minutes * 60
        
        # Get current attempts data
        attempts_data = self.cache.get(key, {
            'attempts': 0,
            'reset_time': now + decay_seconds
        })
        
        # Check if window has expired
        if now >= attempts_data['reset_time']:
            attempts_data = {
                'attempts': 0,
                'reset_time': now + decay_seconds
            }
        
        # Check if under limit
        if attempts_data['attempts'] < max_attempts:
            attempts_data['attempts'] += 1
            self.cache[key] = attempts_data
            return True
        
        return False
    
    def too_many_attempts(self, key: str, max_attempts: int, decay_minutes: int = 1) -> bool:
        """
        Check if there are too many attempts for a key
        
        Args:
            key: Unique key for rate limiting
            max_attempts: Maximum attempts allowed
            decay_minutes: Time window in minutes
            
        Returns:
            bool: True if too many attempts
        """
        return not self.attempt(key, max_attempts, decay_minutes)
    
    def hits(self, key: str) -> int:
        """
        Get the number of hits for a key
        
        Args:
            key: Rate limit key
            
        Returns:
            int: Number of hits
        """
        attempts_data = self.cache.get(key, {'attempts': 0})
        return attempts_data['attempts']
    
    def available_in(self, key: str) -> int:
        """
        Get seconds until rate limit resets
        
        Args:
            key: Rate limit key
            
        Returns:
            int: Seconds until reset
        """
        attempts_data = self.cache.get(key)
        if not attempts_data:
            return 0
        
        now = time.time()
        reset_time = attempts_data.get('reset_time', now)
        return max(0, int(reset_time - now))
    
    def clear(self, key: str):
        """
        Clear rate limit for a key
        
        Args:
            key: Rate limit key to clear
        """
        self.cache.pop(key, None)
    
    def reset_attempts(self, key: str):
        """
        Reset attempts for a key
        
        Args:
            key: Rate limit key to reset
        """
        self.clear(key)


# Default rate limiter instance
_default_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get the default rate limiter instance"""
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter()
    return _default_rate_limiter