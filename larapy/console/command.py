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

    def run(self, args: List[str] = None) -> int:
        """Run the command with arguments"""
        # Store arguments for later use
        self._args = args or []
        
        # Execute the handle method
        try:
            result = self.handle()
            return result if isinstance(result, int) else 0
        except Exception as e:
            print(f"Command error: {e}")
            return 1

    def argument(self, name: str, default: Any = None) -> Any:
        """Get command argument"""
        # Simple argument parsing - first argument is position 0, etc.
        args = getattr(self, '_args', [])
        
        if name == 'name' and len(args) > 0:
            return args[0]
        
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

    def comment(self, message: str):
        """Print a comment"""
        print(f"# {message}")

    def ask(self, question: str) -> str:
        """Ask user for input"""
        return input(f"{question}: ")

    def confirm(self, question: str) -> bool:
        """Ask user for confirmation"""
        answer = input(f"{question} (y/N): ").lower()
        return answer in ['y', 'yes']