"""Console Application for Larapy Framework"""

import sys
import os
from typing import List, Dict, Any, Optional
from .kernel import ConsoleKernel


class ConsoleApplication:
    """
    Console application for handling command-line interface
    """
    
    def __init__(self, app=None, kernel: ConsoleKernel = None):
        self.app = app
        self.kernel = kernel or ConsoleKernel(app)
        self.name = "Larapy Console"
        self.version = "1.0.0"

    def run(self, args: List[str] = None) -> int:
        """Run the console application"""
        if args is None:
            args = sys.argv[1:]  # Skip script name
        
        try:
            return self.kernel.handle(args)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def handle(self, args: List[str]) -> int:
        """Handle console command execution (alias for run)"""
        return self.run(args)

    def call(self, command: str, parameters: Dict[str, Any] = None) -> int:
        """Programmatically call a command"""
        return self.kernel.call(command, parameters)

    def set_kernel(self, kernel: ConsoleKernel):
        """Set the console kernel"""
        self.kernel = kernel

    def get_kernel(self) -> ConsoleKernel:
        """Get the console kernel"""
        return self.kernel

    def register_command(self, name: str, command_class):
        """Register a console command"""
        self.kernel.register_command(name, command_class)

    def get_commands(self) -> Dict[str, Any]:
        """Get all registered commands"""
        return self.kernel.commands

    def has_command(self, name: str) -> bool:
        """Check if a command is registered"""
        return name in self.kernel.commands

    def show_help(self):
        """Show help information"""
        self.kernel.show_help()

    def show_version(self):
        """Show version information"""
        self.kernel.show_version()


def create_application(app=None, kernel: ConsoleKernel = None) -> ConsoleApplication:
    """Create a new console application instance"""
    return ConsoleApplication(app, kernel)


def main():
    """Main entry point for the global larapy command"""
    import sys
    import os
    
    # Check if we're in a project directory (has bootstrap/console.py)
    project_bootstrap = os.path.join(os.getcwd(), 'bootstrap', 'console.py')
    project_larapy_script = os.path.join(os.getcwd(), 'larapy')
    
    if os.path.exists(project_bootstrap) and os.path.exists(project_larapy_script):
        # We're in a project directory, use the project-specific larapy script
        print("🏠 Detected Larapy project - using project console...")
        try:
            # Import project-specific console
            sys.path.insert(0, os.getcwd())
            from bootstrap.console import create_console_application, get_console_kernel
            
            # Create project-specific application
            app = create_console_application()
            kernel = get_console_kernel(app)
            
            # Create console application with project kernel
            console_app = ConsoleApplication(app, kernel)
            exit_code = console_app.run()
            sys.exit(exit_code)
            
        except Exception as e:
            print(f"⚠️  Project console failed, falling back to global: {e}")
    
    # Use global console application
    app = ConsoleApplication()
    exit_code = app.run()
    sys.exit(exit_code)