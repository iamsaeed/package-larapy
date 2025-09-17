"""Cookie support for responses."""

import json
import base64
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib
import hmac


class Cookie:
    """Represents a cookie with all its properties."""
    
    def __init__(self, name: str, value: str = '', max_age: Optional[int] = None,
                 expires: Optional[datetime] = None, path: str = '/', domain: Optional[str] = None,
                 secure: bool = False, httponly: bool = False, samesite: Optional[str] = None):
        """Initialize a cookie."""
        self.name = name
        self.value = value
        self.max_age = max_age
        self.expires = expires
        self.path = path
        self.domain = domain
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
    
    def to_dict(self) -> Dict:
        """Convert cookie to dictionary for Flask."""
        data = {
            'key': self.name,
            'value': self.value,
            'path': self.path,
            'secure': self.secure,
            'httponly': self.httponly
        }
        
        if self.max_age is not None:
            data['max_age'] = self.max_age
        if self.expires is not None:
            data['expires'] = self.expires
        if self.domain is not None:
            data['domain'] = self.domain
        if self.samesite is not None:
            data['samesite'] = self.samesite
        
        return data


class CookieJar:
    """Cookie jar for queuing cookies."""
    
    def __init__(self):
        """Initialize the cookie jar."""
        self._cookies: List[Cookie] = []
    
    def add(self, cookie: Cookie):
        """Add a cookie to the jar."""
        # Remove existing cookie with same name and path
        self._cookies = [c for c in self._cookies if not (c.name == cookie.name and c.path == cookie.path)]
        self._cookies.append(cookie)
    
    def make(self, name: str, value: str = '', **kwargs) -> Cookie:
        """Create and add a cookie."""
        cookie = Cookie(name, value, **kwargs)
        self.add(cookie)
        return cookie
    
    def forget(self, name: str, path: str = '/'):
        """Remove a cookie by setting it to expire."""
        cookie = Cookie(name, '', expires=datetime.utcnow() - timedelta(days=1), path=path)
        self.add(cookie)
    
    def has(self, name: str, path: str = '/') -> bool:
        """Check if a cookie exists."""
        return any(c.name == name and c.path == path for c in self._cookies)
    
    def get(self, name: str, path: str = '/') -> Optional[Cookie]:
        """Get a cookie by name and path."""
        for cookie in self._cookies:
            if cookie.name == name and cookie.path == path:
                return cookie
        return None
    
    def all(self) -> List[Cookie]:
        """Get all cookies."""
        return self._cookies.copy()
    
    def clear(self):
        """Clear all cookies from jar."""
        self._cookies.clear()


class CookieEncryption:
    """Cookie encryption/decryption utilities."""
    
    def __init__(self, key: Optional[str] = None):
        """Initialize with encryption key."""
        if key:
            # Use provided key (should be base64 encoded)
            try:
                self.cipher = Fernet(key.encode())
            except:
                # Generate key from provided string
                key_hash = hashlib.sha256(key.encode()).digest()
                key_b64 = base64.urlsafe_b64encode(key_hash)
                self.cipher = Fernet(key_b64)
        else:
            # Generate a new key
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, value: str) -> str:
        """Encrypt a cookie value."""
        try:
            encrypted = self.cipher.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception:
            return value  # Return original if encryption fails
    
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt a cookie value."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return encrypted_value  # Return original if decryption fails


class CookieSigner:
    """Cookie signing for integrity verification."""
    
    def __init__(self, secret_key: str):
        """Initialize with secret key."""
        self.secret_key = secret_key
    
    def sign(self, value: str) -> str:
        """Sign a cookie value."""
        signature = hmac.new(
            self.secret_key.encode(),
            value.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{value}.{signature}"
    
    def unsign(self, signed_value: str) -> Optional[str]:
        """Unsign and verify a cookie value."""
        try:
            value, signature = signed_value.rsplit('.', 1)
            expected_signature = hmac.new(
                self.secret_key.encode(),
                value.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return value
        except ValueError:
            pass
        
        return None


class SecureCookie:
    """Secure cookie with encryption and signing."""
    
    def __init__(self, encryption_key: Optional[str] = None, secret_key: Optional[str] = None):
        """Initialize secure cookie handler."""
        self.encryptor = CookieEncryption(encryption_key) if encryption_key else None
        self.signer = CookieSigner(secret_key) if secret_key else None
    
    def make_secure_value(self, value: Any) -> str:
        """Create a secure cookie value."""
        # Convert value to JSON if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value, default=str)
        
        # Encrypt if encryption is enabled
        if self.encryptor:
            value = self.encryptor.encrypt(value)
        
        # Sign if signing is enabled
        if self.signer:
            value = self.signer.sign(value)
        
        return value
    
    def get_secure_value(self, secure_value: str) -> Any:
        """Extract value from secure cookie."""
        value = secure_value
        
        # Unsign if signing is enabled
        if self.signer:
            unsigned_value = self.signer.unsign(value)
            if unsigned_value is None:
                return None  # Invalid signature
            value = unsigned_value
        
        # Decrypt if encryption is enabled
        if self.encryptor:
            value = self.encryptor.decrypt(value)
        
        # Try to parse as JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


class CookieManager:
    """Main cookie manager for the application."""
    
    def __init__(self, encryption_key: Optional[str] = None, secret_key: Optional[str] = None):
        """Initialize the cookie manager."""
        self.jar = CookieJar()
        self.secure_cookie = SecureCookie(encryption_key, secret_key)
    
    def make(self, name: str, value: Any = '', encrypted: bool = False, 
             max_age: Optional[int] = None, expires: Optional[datetime] = None,
             path: str = '/', domain: Optional[str] = None,
             secure: bool = False, httponly: bool = False, 
             samesite: Optional[str] = None) -> Cookie:
        """Create a cookie."""
        # Prepare value
        if encrypted and self.secure_cookie:
            cookie_value = self.secure_cookie.make_secure_value(value)
        else:
            cookie_value = str(value) if not isinstance(value, str) else value
        
        return self.jar.make(
            name, cookie_value, max_age=max_age, expires=expires,
            path=path, domain=domain, secure=secure, httponly=httponly,
            samesite=samesite
        )
    
    def get(self, name: str, default: Any = None, path: str = '/', encrypted: bool = False) -> Any:
        """Get a cookie value."""
        from flask import request
        
        if not request or not hasattr(request, 'cookies'):
            return default
        
        cookie_value = request.cookies.get(name)
        if cookie_value is None:
            return default
        
        if encrypted and self.secure_cookie:
            return self.secure_cookie.get_secure_value(cookie_value)
        
        return cookie_value
    
    def forget(self, name: str, path: str = '/'):
        """Remove a cookie."""
        self.jar.forget(name, path)
    
    def has(self, name: str, path: str = '/') -> bool:
        """Check if a cookie exists."""
        from flask import request
        
        if not request or not hasattr(request, 'cookies'):
            return False
        
        return name in request.cookies
    
    def forever(self, name: str, value: Any = '', encrypted: bool = False, **kwargs):
        """Create a cookie that lasts "forever" (5 years)."""
        expires = datetime.utcnow() + timedelta(days=365 * 5)
        return self.make(name, value, encrypted=encrypted, expires=expires, **kwargs)
    
    def queue_cookies_to_response(self, response):
        """Apply queued cookies to a Flask response."""
        for cookie in self.jar.all():
            cookie_dict = cookie.to_dict()
            response.set_cookie(**cookie_dict)
        
        # Clear the jar after applying
        self.jar.clear()
        
        return response