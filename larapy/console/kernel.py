"""
Console Kernel for Larapy Applications.

Provides console bootstrapping, command registration, and application lifecycle
management for console operations.
"""

import os
from typing import List, TYPE_CHECKING
from ..foundation.application import Application

if TYPE_CHECKING:
    from .command import Command


class ConsoleKernel:
    """
    Base Console Kernel for Larapy Applications.
    
    Similar to Laravel's Illuminate\\Foundation\\Console\\Kernel.
    """
    
    # Application-specific commands (override in subclasses)
    command_classes: List[str] = []
    
    def __init__(self, app: Application):
        """
        Initialize the console kernel.
        
        Args:
            app: Larapy application instance
        """
        self.app = app
        
    def schedule(self, schedule):
        """
        Define the application's command schedule.
        
        Override this method in application kernels to define
        scheduled commands.
        
        Args:
            schedule: Schedule object for defining scheduled commands
        """
        pass
    
    def commands(self):
        """
        Register the application's commands.
        
        This method is called automatically during bootstrap.
        Override to add custom command registration logic.
        """
        pass
    
    def load_commands_from_directory(self, directory: str):
        """
        Load all commands from a directory.
        
        Automatically discovers and registers command classes
        from Python files in the specified directory.
        
        Args:
            directory: Directory path to scan for commands
        """
        import os
        import importlib.util
        import inspect
        from .command import Command
        
        if not os.path.exists(directory):
            return
        
        for file in os.listdir(directory):
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(directory, file)
                self._load_commands_from_file(file_path)
    
    def _load_commands_from_file(self, file_path: str):
        """
        Load commands from a specific file.
        
        Args:
            file_path: Path to Python file containing commands
        """
        import importlib.util
        import inspect
        from .command import Command
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("command_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find Command classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Command) and 
                        obj != Command):
                        # Register the command
                        self._register_command_class(obj)
                        
        except Exception as e:
            # Log error but don't fail the entire bootstrap
            print(f"Warning: Could not load commands from {file_path}: {e}")
    
    def _register_command_class(self, command_class):
        """
        Register a command class.
        
        Args:
            command_class: Command class to register
        """
        # This would integrate with the console application
        # For now, just store the class reference
        pass
    
    def bootstrap(self):
        """
        Bootstrap the console kernel.
        
        Performs initialization tasks required for console operations.
        """
        # Register application commands
        self.commands()
        
        # Load commands from default directory if it exists
        if hasattr(self.app, 'base_path'):
            commands_dir = os.path.join(self.app.base_path(), 'app', 'console', 'commands')
            self.load_commands_from_directory(commands_dir)
    
    def handle(self, args: List[str] = None) -> int:
        """
        Handle console request.
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code
        """
        # Bootstrap the kernel
        self.bootstrap()
        
        # This would delegate to the console application
        # For now, return success
        return 0
    
    def terminate(self, exit_code: int):
        """
        Perform any final cleanup.
        
        Args:
            exit_code: The exit code from command execution
        """
        pass