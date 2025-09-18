"""
Encryption Service

Provides Laravel-style encryption and decryption using Python's cryptography library.
Supports both Fernet (symmetric) and AES encryption with serialization.
"""

import json
import base64
import pickle
from typing import Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app


class Encrypter:
    """
    Handles encryption and decryption of data
    """
    
    def __init__(self, key: Optional[str] = None, cipher: str = 'fernet'):
        """
        Initialize the encrypter
        
        Args:
            key: Encryption key (base64 encoded)
            cipher: Cipher type ('fernet' or 'aes')
        """
        self.cipher = cipher
        self.key = key or self._get_app_key()
        self._fernet = None
        
        if self.cipher == 'fernet':
            self._setup_fernet()
    
    def _get_app_key(self) -> str:
        """Get encryption key from app config"""
        if hasattr(current_app, 'config'):
            return current_app.config.get('SECRET_KEY', '')
        return ''
    
    def _setup_fernet(self):
        """Setup Fernet encryption"""
        if not self.key:
            raise ValueError("Encryption key is required")
        
        # Generate Fernet key from app key
        key_bytes = self.key.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'larapy_salt',  # In production, use random salt
            iterations=100000,
        )
        fernet_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        self._fernet = Fernet(fernet_key)
    
    def encrypt(self, value: Any, serialize: bool = True) -> str:
        """
        Encrypt a value
        
        Args:
            value: Value to encrypt
            serialize: Whether to serialize the value first
            
        Returns:
            str: Base64 encoded encrypted value
        """
        if serialize:
            # Serialize the value (support for complex data types)
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value)
            elif not isinstance(value, (str, bytes)):
                value = pickle.dumps(value)
        
        if isinstance(value, str):
            value = value.encode('utf-8')
        
        if self.cipher == 'fernet':
            encrypted = self._fernet.encrypt(value)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        
        raise ValueError(f"Unsupported cipher: {self.cipher}")
    
    def decrypt(self, encrypted_value: str, unserialize: bool = True) -> Any:
        """
        Decrypt a value
        
        Args:
            encrypted_value: Base64 encoded encrypted value
            unserialize: Whether to unserialize the decrypted value
            
        Returns:
            Any: Decrypted value
        """
        try:
            # Decode from base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_value.encode('utf-8'))
            
            if self.cipher == 'fernet':
                decrypted = self._fernet.decrypt(encrypted_data)
                
                if unserialize:
                    try:
                        # Try JSON first
                        return json.loads(decrypted.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        try:
                            # Try pickle
                            return pickle.loads(decrypted)
                        except (pickle.PickleError, TypeError):
                            # Return as string
                            return decrypted.decode('utf-8')
                
                return decrypted.decode('utf-8')
            
            raise ValueError(f"Unsupported cipher: {self.cipher}")
            
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {str(e)}")
    
    def encrypt_string(self, value: str) -> str:
        """
        Encrypt a string value
        
        Args:
            value: String to encrypt
            
        Returns:
            str: Encrypted value
        """
        return self.encrypt(value, serialize=False)
    
    def decrypt_string(self, encrypted_value: str) -> str:
        """
        Decrypt a string value
        
        Args:
            encrypted_value: Encrypted string
            
        Returns:
            str: Decrypted string
        """
        return self.decrypt(encrypted_value, unserialize=False)
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            str: Base64 encoded key
        """
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode('utf-8')


# Default encrypter instance
_default_encrypter = None


def get_encrypter() -> Encrypter:
    """Get the default encrypter instance"""
    global _default_encrypter
    if _default_encrypter is None:
        _default_encrypter = Encrypter()
    return _default_encrypter