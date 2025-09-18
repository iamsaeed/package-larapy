"""
Encryption Facade

Provides easy access to encryption functionality.
"""

from larapy.support.facades.facade import Facade
from larapy.encryption.encrypter import get_encrypter


class Crypt(Facade):
    """
    Encryption Facade
    """
    
    @staticmethod
    def get_facade_accessor():
        return get_encrypter()
    
    @classmethod
    def encrypt(cls, value, serialize=True):
        """Encrypt a value"""
        return cls.get_facade_accessor().encrypt(value, serialize)
    
    @classmethod
    def decrypt(cls, encrypted_value, unserialize=True):
        """Decrypt a value"""
        return cls.get_facade_accessor().decrypt(encrypted_value, unserialize)
    
    @classmethod
    def encrypt_string(cls, value):
        """Encrypt a string"""
        return cls.get_facade_accessor().encrypt_string(value)
    
    @classmethod
    def decrypt_string(cls, encrypted_value):
        """Decrypt a string"""
        return cls.get_facade_accessor().decrypt_string(encrypted_value)
    
    @classmethod
    def generate_key(cls):
        """Generate a new encryption key"""
        return cls.get_facade_accessor().generate_key()