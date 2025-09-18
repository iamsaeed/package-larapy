"""Base command class for console commands"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Command(ABC):
    """
    Base command class
    
    Provides a simplified interface for console commands
    compatible with the database migration system.
    """

    signature: str = ""
    description: str = ""

    def __init__(self, app=None):
        self.app = app

    @abstractmethod
    def handle(self) -> int:
        """Execute the command"""
        pass

    def argument(self, name: str, default: Any = None) -> Any:
        """Get command argument"""
        # Simplified implementation for now
        return default

    def option(self, name: str, default: Any = False) -> Any:
        """Get command option"""
        # Simplified implementation for now
        return default

    def info(self, message: str):
        """Print info message"""
        print(f"INFO: {message}")

    def error(self, message: str):
        """Print error message"""
        print(f"ERROR: {message}")

    def success(self, message: str):
        """Print success message"""
        print(f"SUCCESS: {message}")

    def line(self, message: str):
        """Print a line"""
        print(message)