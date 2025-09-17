"""Log facade for easy access to logging"""

from .facade import Facade

class Log(Facade):
    """Log facade for easy access to logging"""

    @classmethod
    def get_facade_accessor(cls):
        return 'log'

    @classmethod
    def emergency(cls, message, context=None):
        """Log emergency message"""
        return cls.get_facade_root().emergency(message, context)

    @classmethod
    def alert(cls, message, context=None):
        """Log alert message"""
        return cls.get_facade_root().alert(message, context)

    @classmethod
    def critical(cls, message, context=None):
        """Log critical message"""
        return cls.get_facade_root().critical(message, context)

    @classmethod
    def error(cls, message, context=None):
        """Log error message"""
        return cls.get_facade_root().error(message, context)

    @classmethod
    def warning(cls, message, context=None):
        """Log warning message"""
        return cls.get_facade_root().warning(message, context)

    @classmethod
    def notice(cls, message, context=None):
        """Log notice message"""
        return cls.get_facade_root().notice(message, context)

    @classmethod
    def info(cls, message, context=None):
        """Log info message"""
        return cls.get_facade_root().info(message, context)

    @classmethod
    def debug(cls, message, context=None):
        """Log debug message"""
        return cls.get_facade_root().debug(message, context)

    @classmethod
    def log(cls, level, message, context=None):
        """Log message with level"""
        return cls.get_facade_root().log(level, message, context)

    @classmethod
    def channel(cls, channel=None):
        """Get a specific channel"""
        return cls.get_facade_root().channel(channel)