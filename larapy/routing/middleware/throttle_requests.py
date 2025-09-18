"""
Throttle Requests Middleware

Implements rate limiting for routes using token bucket algorithm.
Supports different limits for authenticated/guest users and custom keys.
"""

import re
import time
from typing import Optional, Tuple, Dict, Any
from flask import request, abort, g, current_app
from functools import wraps

from larapy.cache.rate_limiter import get_rate_limiter


class ThrottleRequests:
    """
    Middleware for throttling requests
    """
    
    def __init__(self, limiter_name: str = 'default', max_attempts: Optional[int] = None, 
                 decay_minutes: Optional[int] = None):
        """
        Initialize throttle middleware
        
        Args:
            limiter_name: Name of the rate limiter configuration
            max_attempts: Maximum attempts (overrides config)
            decay_minutes: Decay time in minutes (overrides config)
        """
        self.limiter_name = limiter_name
        self.max_attempts = max_attempts
        self.decay_minutes = decay_minutes
        self.rate_limiter = get_rate_limiter()
    
    def __call__(self, f=None, **kwargs):
        """
        Decorator for route functions or direct call with parameters
        """
        if f is None:
            # Called with parameters: @throttle('api', 100, 60)
            return lambda func: self._create_decorator(func, **kwargs)
        else:
            # Called without parameters: @throttle
            return self._create_decorator(f)
    
    def _create_decorator(self, f, **kwargs):
        """Create the actual decorator"""
        @wraps(f)
        def decorated_function(*args, **func_kwargs):
            # Parse rate limit configuration
            max_attempts, decay_minutes = self._resolve_rate_limit(**kwargs)
            
            # Generate rate limit key
            key = self._resolve_request_signature(max_attempts, decay_minutes)
            
            # Check rate limit
            if self.rate_limiter.too_many_attempts(key, max_attempts, decay_minutes):
                self._build_too_many_attempts_response(key, max_attempts, decay_minutes)
            
            # Add rate limit headers to response
            response = f(*args, **func_kwargs)
            return self._add_headers(response, key, max_attempts, decay_minutes)
        
        return decorated_function
    
    def _resolve_rate_limit(self, **kwargs) -> Tuple[int, int]:
        """
        Resolve rate limit parameters from config or parameters
        
        Returns:
            Tuple[int, int]: (max_attempts, decay_minutes)
        """
        # Use provided parameters first
        if self.max_attempts is not None and self.decay_minutes is not None:
            return self.max_attempts, self.decay_minutes
        
        # Get from app config
        config = getattr(current_app, 'config', {})
        rate_limits = config.get('RATE_LIMITS', {})
        
        # Default rate limits
        default_limits = {
            'default': (60, 1),  # 60 requests per minute
            'api': (1000, 60),   # 1000 requests per hour
            'login': (5, 1),     # 5 login attempts per minute
        }
        
        limit_config = rate_limits.get(self.limiter_name, 
                                     default_limits.get(self.limiter_name, (60, 1)))
        
        if isinstance(limit_config, str):
            # Parse "max,minutes" format
            parts = limit_config.split(',')
            return int(parts[0]), int(parts[1])
        elif isinstance(limit_config, (list, tuple)) and len(limit_config) == 2:
            return limit_config[0], limit_config[1]
        
        return 60, 1  # Default fallback
    
    def _resolve_request_signature(self, max_attempts: int, decay_minutes: int) -> str:
        """
        Generate a unique key for rate limiting
        
        Args:
            max_attempts: Maximum attempts
            decay_minutes: Decay time in minutes
            
        Returns:
            str: Unique rate limit key
        """
        # Start with route and method
        key_parts = [
            request.method,
            request.endpoint or request.path,
        ]
        
        # Add user identifier if authenticated
        if hasattr(g, 'user') and g.user:
            key_parts.append(f"user:{g.user.id}")
        else:
            # Use IP address for unauthenticated users
            key_parts.append(f"ip:{self._get_client_ip()}")
        
        # Add rate limit parameters
        key_parts.extend([str(max_attempts), str(decay_minutes)])
        
        return ':'.join(key_parts)
    
    def _get_client_ip(self) -> str:
        """
        Get the client IP address, considering proxies
        
        Returns:
            str: Client IP address
        """
        # Check for forwarded headers (behind proxy)
        forwarded_ips = request.headers.get('X-Forwarded-For')
        if forwarded_ips:
            return forwarded_ips.split(',')[0].strip()
        
        # Check other common headers
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return request.remote_addr or '127.0.0.1'
    
    def _build_too_many_attempts_response(self, key: str, max_attempts: int, 
                                        decay_minutes: int):
        """
        Build response for too many attempts
        
        Args:
            key: Rate limit key
            max_attempts: Maximum attempts
            decay_minutes: Decay time in minutes
        """
        retry_after = self.rate_limiter.available_in(key)
        
        # Return 429 Too Many Requests
        response = {
            'message': 'Too many attempts. Please try again later.',
            'retry_after': retry_after,
        }
        
        # Add Retry-After header
        headers = {
            'Retry-After': str(retry_after),
            'X-RateLimit-Limit': str(max_attempts),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': str(int(time.time()) + retry_after),
        }
        
        abort(429, description=response, response=headers)
    
    def _add_headers(self, response, key: str, max_attempts: int, decay_minutes: int):
        """
        Add rate limit headers to response
        
        Args:
            response: Flask response object
            key: Rate limit key
            max_attempts: Maximum attempts
            decay_minutes: Decay time in minutes
            
        Returns:
            Response with rate limit headers
        """
        from flask import make_response
        
        if not hasattr(response, 'headers'):
            response = make_response(response)
        
        current_hits = self.rate_limiter.hits(key)
        remaining = max(0, max_attempts - current_hits)
        reset_time = int(time.time()) + self.rate_limiter.available_in(key)
        
        response.headers['X-RateLimit-Limit'] = str(max_attempts)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        response.headers['X-RateLimit-Reset'] = str(reset_time)
        
        return response


# Convenience functions for creating throttle decorators
def throttle(limiter_name: str = 'default', max_attempts: Optional[int] = None, 
            decay_minutes: Optional[int] = None):
    """
    Create a throttle decorator
    
    Args:
        limiter_name: Name of rate limiter config
        max_attempts: Maximum attempts
        decay_minutes: Decay time in minutes
        
    Returns:
        Throttle decorator
    """
    return ThrottleRequests(limiter_name, max_attempts, decay_minutes)


# Pre-configured throttle decorators
throttle_api = throttle('api')
throttle_login = throttle('login')
throttle_default = throttle('default')