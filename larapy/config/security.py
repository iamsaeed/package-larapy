"""
Security Configuration

Centralized security configuration for Larapy applications.
Follows Laravel's security configuration structure.
"""

import os
from typing import Dict, Any, List


def get_security_config() -> Dict[str, Any]:
    """
    Get security configuration with environment-based settings
    
    Returns:
        Dict[str, Any]: Security configuration
    """
    return {
        # Encryption settings
        'encryption': {
            'key': os.getenv('APP_KEY', ''),
            'cipher': 'fernet',  # or 'aes'
        },
        
        # CSRF protection settings
        'csrf': {
            'enabled': True,
            'cookie_name': 'XSRF-TOKEN',
            'header_name': 'X-CSRF-TOKEN',
            'field_name': '_token',
            'exclude': [
                'api/*',
                'webhooks/*',
                'stripe/webhook',
            ]
        },
        
        # CORS settings
        'cors': {
            'paths': ['api/*', 'sanctum/csrf-cookie'],
            'allowed_origins': _parse_env_list('CORS_ALLOWED_ORIGINS', ['*']),
            'allowed_methods': _parse_env_list('CORS_ALLOWED_METHODS', ['*']),
            'allowed_headers': _parse_env_list('CORS_ALLOWED_HEADERS', ['*']),
            'exposed_headers': _parse_env_list('CORS_EXPOSED_HEADERS', []),
            'max_age': int(os.getenv('CORS_MAX_AGE', '0')),
            'supports_credentials': os.getenv('CORS_SUPPORTS_CREDENTIALS', 'false').lower() == 'true',
        },
        
        # Rate limiting settings
        'rate_limiting': {
            'default': os.getenv('RATE_LIMIT_DEFAULT', '60,1'),  # 60 requests per minute
            'api': os.getenv('RATE_LIMIT_API', '1000,60'),       # 1000 per hour
            'login': os.getenv('RATE_LIMIT_LOGIN', '5,1'),       # 5 login attempts per minute
            'register': os.getenv('RATE_LIMIT_REGISTER', '10,1'), # 10 registrations per minute
        },
        
        # Cookie encryption settings
        'cookies': {
            'encrypt': os.getenv('ENCRYPT_COOKIES', 'true').lower() == 'true',
            'exclude': [
                'cookie_consent',
                'session',
                '_ga',  # Google Analytics
                '_gid',
                '_gat',
                '__utma',  # Legacy Google Analytics
                '__utmb',
                '__utmc',
                '__utmz',
            ]
        },
        
        # Security headers
        'security_headers': {
            'x_frame_options': os.getenv('X_FRAME_OPTIONS', 'SAMEORIGIN'),
            'x_content_type_options': os.getenv('X_CONTENT_TYPE_OPTIONS', 'nosniff'),
            'x_xss_protection': os.getenv('X_XSS_PROTECTION', '1; mode=block'),
            'strict_transport_security': os.getenv('HSTS_HEADER', 'max-age=31536000; includeSubDomains'),
            'content_security_policy': os.getenv('CSP_HEADER', "default-src 'self'"),
            'referrer_policy': os.getenv('REFERRER_POLICY', 'strict-origin-when-cross-origin'),
            'permissions_policy': os.getenv('PERMISSIONS_POLICY', 'geolocation=(), microphone=(), camera=()'),
        },
        
        # Password hashing
        'hashing': {
            'driver': os.getenv('HASH_DRIVER', 'bcrypt'),
            'bcrypt': {
                'rounds': int(os.getenv('BCRYPT_ROUNDS', '12')),
            },
            'argon2': {
                'memory_cost': int(os.getenv('ARGON2_MEMORY', '65536')),  # 64MB
                'time_cost': int(os.getenv('ARGON2_TIME', '4')),
                'parallelism': int(os.getenv('ARGON2_THREADS', '3')),
            },
        },
        
        # Authentication settings
        'auth': {
            'defaults': {
                'guard': 'web',
                'passwords': 'users',
            },
            'guards': {
                'web': {
                    'driver': 'session',
                    'provider': 'users',
                },
                'api': {
                    'driver': 'token',
                    'provider': 'users',
                    'hash': False,
                },
            },
            'providers': {
                'users': {
                    'driver': 'eloquent',
                    'model': 'app.Models.User',
                },
            },
            'passwords': {
                'users': {
                    'provider': 'users',
                    'table': 'password_resets',
                    'expire': 60,
                    'throttle': 60,
                },
            },
            'password_timeout': int(os.getenv('AUTH_PASSWORD_TIMEOUT', '10800')),  # 3 hours
        },
        
        # Session security
        'session': {
            'encrypt': os.getenv('SESSION_ENCRYPT', 'false').lower() == 'true',
            'fingerprint': os.getenv('SESSION_FINGERPRINT', 'true').lower() == 'true',
            'ip_validation': os.getenv('SESSION_IP_VALIDATION', 'true').lower() == 'true',
            'user_agent_validation': os.getenv('SESSION_USER_AGENT_VALIDATION', 'true').lower() == 'true',
            'regenerate_on_login': True,
        },
        
        # Trusted proxies
        'trusted_proxies': {
            'proxies': _parse_env_list('TRUSTED_PROXIES', []),
            'headers': _parse_env_list('TRUSTED_PROXY_HEADERS', [
                'REMOTE_ADDR',
                'FORWARDED',
                'X_FORWARDED_FOR',
                'X_FORWARDED_HOST',
                'X_FORWARDED_PORT',
                'X_FORWARDED_PROTO',
            ]),
        },
        
        # URL signing
        'signed_urls': {
            'lifetime': int(os.getenv('SIGNED_URL_LIFETIME', '3600')),  # 1 hour
        },
        
        # Content Security Policy presets
        'csp_presets': {
            'strict': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self';",
            'moderate': "default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;",
            'permissive': "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:;",
        },
    }


def _parse_env_list(env_var: str, default: List[str]) -> List[str]:
    """
    Parse comma-separated environment variable into list
    
    Args:
        env_var: Environment variable name
        default: Default value if not set
        
    Returns:
        List[str]: Parsed list
    """
    value = os.getenv(env_var)
    if not value:
        return default
    
    return [item.strip() for item in value.split(',') if item.strip()]


def get_csp_policy(preset: str = 'moderate') -> str:
    """
    Get Content Security Policy by preset name
    
    Args:
        preset: CSP preset name ('strict', 'moderate', 'permissive')
        
    Returns:
        str: CSP policy string
    """
    config = get_security_config()
    presets = config['csp_presets']
    return presets.get(preset, presets['moderate'])


# Environment variable configuration template
SECURITY_ENV_TEMPLATE = """
# Security Configuration
APP_KEY=your-32-character-secret-key-here

# CSRF Protection
CSRF_ENABLED=true

# CORS Configuration
CORS_ALLOWED_ORIGINS=*
CORS_ALLOWED_METHODS=*
CORS_ALLOWED_HEADERS=*
CORS_EXPOSED_HEADERS=
CORS_MAX_AGE=0
CORS_SUPPORTS_CREDENTIALS=false

# Rate Limiting
RATE_LIMIT_DEFAULT=60,1
RATE_LIMIT_API=1000,60
RATE_LIMIT_LOGIN=5,1
RATE_LIMIT_REGISTER=10,1

# Cookie Encryption
ENCRYPT_COOKIES=true

# Security Headers
X_FRAME_OPTIONS=SAMEORIGIN
X_CONTENT_TYPE_OPTIONS=nosniff
X_XSS_PROTECTION=1; mode=block
HSTS_HEADER=max-age=31536000; includeSubDomains
CSP_HEADER=default-src 'self'
REFERRER_POLICY=strict-origin-when-cross-origin
PERMISSIONS_POLICY=geolocation=(), microphone=(), camera=()

# Password Hashing
HASH_DRIVER=bcrypt
BCRYPT_ROUNDS=12
ARGON2_MEMORY=65536
ARGON2_TIME=4
ARGON2_THREADS=3

# Session Security
SESSION_ENCRYPT=false
SESSION_FINGERPRINT=true
SESSION_IP_VALIDATION=true
SESSION_USER_AGENT_VALIDATION=true

# Trusted Proxies
TRUSTED_PROXIES=
TRUSTED_PROXY_HEADERS=REMOTE_ADDR,FORWARDED,X_FORWARDED_FOR,X_FORWARDED_HOST,X_FORWARDED_PORT,X_FORWARDED_PROTO

# Authentication
AUTH_PASSWORD_TIMEOUT=10800

# Signed URLs
SIGNED_URL_LIFETIME=3600
"""