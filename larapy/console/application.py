"""
Console Application for Larapy Framework.

Manages command registration, discovery, and execution for the Larapy console system.
Provides Laravel-like artisan functionality.
"""

import sys
import os
from typing import Dict, Type, List, Optional
from .command import Command
from .kernel import ConsoleKernel
from ..foundation.application import Application


class ConsoleApplication:
    """
    Console application managing command lifecycle.
    
    Similar to Laravel's console application infrastructure.
    """
    
    def __init__(self, app: Application = None, kernel: ConsoleKernel = None):
        """
        Initialize console application.
        
        Args:
            app: Larapy application instance
            kernel: Console kernel instance
        """
        self.app = app
        self.kernel = kernel
        self.commands: Dict[str, Type[Command]] = {}
        
        # Register built-in framework commands
        self._register_builtin_commands()
        
        # Register application commands if kernel provided
        if kernel:
            self._register_kernel_commands(kernel)
    
    def _register_builtin_commands(self):
        """Register built-in framework commands"""
        # Import and register framework commands
        try:
            from .commands.serve_command import ServeCommand
            from .commands.about_command import AboutCommand
            from .commands.make.controller_command import MakeControllerCommand
            from .commands.make.model_command import MakeModelCommand
            from .commands.make.middleware_command import MakeMiddlewareCommand
            
            self.register_command('serve', ServeCommand)
            self.register_command('about', AboutCommand)
            self.register_command('make:controller', MakeControllerCommand)
            self.register_command('make:model', MakeModelCommand)
            self.register_command('make:middleware', MakeMiddlewareCommand)
            
        except ImportError as e:
            # Commands not yet implemented - that's ok
            pass
    
    def _register_kernel_commands(self, kernel: ConsoleKernel):
        """
        Register commands from the console kernel.
        
        Args:
            kernel: Console kernel containing application commands
        """
        # Register commands defined in kernel.command_classes
        for command_class_path in kernel.command_classes:
            self._register_command_from_path(command_class_path)
        
        # Let kernel register additional commands
        kernel.commands()
    
    def _register_command_from_path(self, command_class_path: str):
        """
        Register a command from a class path string.
        
        Args:
            command_class_path: Dotted path to command class
        """
        try:
            # Import the command class
            module_path, class_name = command_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            command_class = getattr(module, class_name)
            
            # Get command name from the class
            command_instance = command_class(self.app)
            command_name = command_instance.get_name()
            
            # Register the command
            self.register_command(command_name, command_class)
            
        except Exception as e:
            print(f"Warning: Could not register command {command_class_path}: {e}")
    
    def register_command(self, name: str, command_class: Type[Command]):
        """
        Register a command class.
        
        Args:
            name: Command name
            command_class: Command class
        """
        self.commands[name] = command_class
    
    def run(self, args: List[str] = None) -> int:
        """
        Run the console application.
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code
        """
        if args is None:
            args = sys.argv[1:]
        
        # Handle help command
        if not args or args[0] in ['help', '--help', '-h']:
            if len(args) > 1 and args[1] != '--help':
                # Help for specific command: larapy help command-name
                self.show_command_help(args[1])
            else:
                self.show_help()
            return 0
        
        # Handle version command
        if args[0] in ['--version', '-V']:
            self.show_version()
            return 0
        
        # Get command name
        command_name = args[0]
        command_args = args[1:] if len(args) > 1 else []
        
        # Find and execute command
        if command_name in self.commands:
            command_class = self.commands[command_name]
            command = command_class(self.app)
            return command.run(command_args)
        else:
            self.show_command_not_found(command_name)
            return 1
    
    def show_help(self):
        """Show help information"""
        print("Larapy Framework")
        print("Laravel-inspired command line interface for Larapy applications")
        print()
        print("Usage:")
        print("  larapy <command> [options] [arguments]")
        print()
        print("Available commands:")
        
        # Group commands by category
        make_commands = []
        other_commands = []
        
        for name in sorted(self.commands.keys()):
            if name.startswith('make:'):
                make_commands.append(name)
            else:
                other_commands.append(name)
        
        # Show general commands
        if other_commands:
            for name in other_commands:
                command_class = self.commands[name]
                try:
                    instance = command_class(self.app)
                    description = getattr(instance, 'description', '')
                    print(f"  {name:<20} {description}")
                except:
                    print(f"  {name:<20}")
        
        # Show make commands
        if make_commands:
            print()
            print("make")
            for name in make_commands:
                command_class = self.commands[name]
                try:
                    instance = command_class(self.app)
                    description = getattr(instance, 'description', '')
                    print(f"  {name:<20} {description}")
                except:
                    print(f"  {name:<20}")
    
    def show_version(self):
        """Show version information"""
        version = "1.0.0"
        if self.app and hasattr(self.app, 'VERSION'):
            version = self.app.VERSION
        print(f"Larapy Framework {version}")
    
    def show_command_not_found(self, command_name: str):
        """
        Show command not found error.
        
        Args:
            command_name: Name of command that was not found
        """
        print(f"Command '{command_name}' not found.")
        print()
        print("Did you mean one of these?")
        
        # Find similar commands
        similar_commands = []
        for name in self.commands.keys():
            if command_name in name or name in command_name:
                similar_commands.append(name)
        
        if similar_commands:
            for name in similar_commands[:5]:  # Show max 5 suggestions
                print(f"  {name}")
        else:
            print("  No similar commands found.")
        
        print()
        print("Use 'larapy help' to see all available commands.")
    
    def show_command_help(self, command_name: str):
        """
        Show help for a specific command.
        
        Args:
            command_name: Name of command to show help for
        """
        if command_name not in self.commands:
            self.show_command_not_found(command_name)
            return
        
        command_class = self.commands[command_name]
        try:
            instance = command_class(self.app)
            signature = getattr(instance, 'signature', '')
            description = getattr(instance, 'description', '')
            
            print(f"Description:")
            print(f"  {description}")
            print()
            
            if signature:
                print(f"Usage:")
                print(f"  {signature}")
                print()
                
                # Parse signature to show arguments and options
                import re
                param_pattern = r'\{([^}]+)\}'
                param_matches = re.findall(param_pattern, signature)
                
                args_help = []
                options_help = []
                
                for param in param_matches:
                    if param.startswith('--'):
                        # Option
                        option_def = param[2:]
                        if ':' in option_def:
                            option_name = option_def.split(':')[0].strip()
                            option_desc = option_def.split(':', 1)[1].strip()
                        else:
                            option_name = option_def.strip()
                            option_desc = ''
                        options_help.append([f"--{option_name}", option_desc])
                    else:
                        # Argument
                        if ':' in param:
                            arg_part = param.split(':')[0].strip()
                            arg_desc = param.split(':', 1)[1].strip()
                        else:
                            arg_part = param.strip()
                            arg_desc = ''
                        
                        optional = arg_part.endswith('?')
                        if optional:
                            arg_part = arg_part[:-1]
                            arg_display = f"{arg_part} (optional)"
                        else:
                            arg_display = arg_part
                        
                        args_help.append([arg_display, arg_desc])
                
                if args_help:
                    print("Arguments:")
                    for arg_name, arg_desc in args_help:
                        print(f"  {arg_name:<20} {arg_desc}")
                    print()
                
                if options_help:
                    print("Options:")
                    for opt_name, opt_desc in options_help:
                        print(f"  {opt_name:<20} {opt_desc}")
            
        except Exception as e:
            print(f"Error showing help for {command_name}: {e}")


def main():
    """Main entry point for the global Larapy CLI"""
    import os
    from ..foundation.application import Application
    
    # Create a basic application for framework commands only
    app = Application(os.getcwd())
    
    # Create console application without kernel (framework commands only)
    console_app = ConsoleApplication(app, None)
    
    # Run the application
    import sys
    sys.exit(console_app.run())