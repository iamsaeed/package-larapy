"""Console Kernel for handling console commands"""

from typing import List, Dict, Any, Optional
import sys
import os


class ConsoleKernel:
    """
    Base console kernel for handling console commands
    """
    
    def __init__(self, app=None):
        self.app = app
        self.commands = {}
        self.register_default_commands()

    def register_default_commands(self):
        """Register default framework commands"""
        # Register commands that don't need complex dependencies first
        try:
            from ..database.console.make_migration_command import MakeMigrationCommand
            from ..database.console.make_factory_command import MakeFactoryCommand
            from ..database.console.make_seeder_command import MakeSeederCommand
            
            # These commands work without database connections
            self.register_command('make:migration', lambda: MakeMigrationCommand())
            self.register_command('make:factory', lambda: MakeFactoryCommand())
            self.register_command('make:seeder', lambda: MakeSeederCommand())
            
        except ImportError as e:
            print(f"Warning: Could not register make commands: {e}")
        
        # Register all available database commands
        try:
            self._register_all_database_commands()
        except Exception as e:
            print(f"Warning: Database commands not available: {e}")

    def _register_all_database_commands(self):
        """Register all available database commands"""
        # Migration commands
        try:
            from ..database.console.migrate_command import MigrateCommand
            self.register_command('migrate', lambda: MigrateCommand())
        except Exception as e:
            print(f"Warning: migrate command not available: {e}")
        
        try:
            from ..database.console.migrate_status_command import MigrateStatusCommand
            self.register_command('migrate:status', self._create_status_command)
        except Exception as e:
            print(f"Warning: migrate:status command not available: {e}")
        
        try:
            from ..database.console.migrate_install_command import MigrateInstallCommand
            self.register_command('migrate:install', self._create_install_command)
        except Exception as e:
            print(f"Warning: migrate:install command not available: {e}")
        
        try:
            from ..database.console.migrate_refresh_command import MigrateRefreshCommand
            self.register_command('migrate:refresh', lambda: MigrateRefreshCommand())
        except Exception as e:
            print(f"Warning: migrate:refresh command not available: {e}")
        
        try:
            from ..database.console.migrate_reset_command import MigrateResetCommand
            self.register_command('migrate:reset', lambda: MigrateResetCommand())
        except Exception as e:
            print(f"Warning: migrate:reset command not available: {e}")
        
        try:
            from ..database.console.rollback_command import RollbackCommand
            self.register_command('migrate:rollback', lambda: RollbackCommand())
        except Exception as e:
            print(f"Warning: migrate:rollback command not available: {e}")
        
        try:
            from ..database.console.fresh_command import FreshCommand
            self.register_command('migrate:fresh', lambda: FreshCommand())
        except Exception as e:
            print(f"Warning: migrate:fresh command not available: {e}")
        
        # Database seeding commands
        try:
            from ..database.console.seed_command import SeedCommand
            self.register_command('db:seed', lambda: SeedCommand())
        except Exception as e:
            print(f"Warning: db:seed command not available: {e}")
        
        # Additional database commands
        try:
            from ..database.console.reset_command import ResetCommand
            self.register_command('db:reset', lambda: ResetCommand())
        except Exception as e:
            print(f"Warning: db:reset command not available: {e}")
        
    def _create_status_command(self):
        """Create migrate:status command with error handling"""
        try:
            from ..database.console.migrate_status_command import MigrateStatusCommand
            from ..database.migrations.repository import MigrationRepository
            
            # Create a minimal repository for status checking
            class SimpleRepository:
                def repository_exists(self):
                    import os
                    return os.path.exists('database/migrations')
                
                def get_ran(self):
                    return []
                
                def get_migration_batch(self, name):
                    return 1
            
            return MigrateStatusCommand(SimpleRepository())
        except Exception as e:
            # Return a simple command that shows the error
            class ErrorCommand:
                def run(self, args):
                    print(f"migrate:status command not available: {e}")
                    return 1
            return ErrorCommand()
    
    def _create_install_command(self):
        """Create migrate:install command with error handling"""
        try:
            from ..database.console.migrate_install_command import MigrateInstallCommand
            
            class SimpleRepository:
                def repository_exists(self):
                    return False
                    
                def create_repository(self):
                    print("Migration repository would be created here")
                    print("(Database connection needed for actual implementation)")
            
            return MigrateInstallCommand(SimpleRepository())
        except Exception as e:
            class ErrorCommand:
                def run(self, args):
                    print(f"migrate:install command not available: {e}")
                    return 1
            return ErrorCommand()

    def register_command(self, name: str, command_class):
        """Register a console command"""
        self.commands[name] = command_class

    def handle(self, args: List[str]) -> int:
        """Handle console command execution"""
        if len(args) == 0:
            self.show_help()
            return 0
        
        command_name = args[0]
        command_args = args[1:] if len(args) > 1 else []
        
        if command_name in ['help', '--help', '-h']:
            self.show_help()
            return 0
        
        if command_name in ['version', '--version', '-V']:
            self.show_version()
            return 0
        
        if command_name not in self.commands:
            print(f"Command '{command_name}' not found.")
            self.show_available_commands()
            return 1
        
        try:
            command_factory = self.commands[command_name]
            
            # If it's a callable (lambda), call it to get the instance
            if callable(command_factory) and not hasattr(command_factory, 'handle'):
                command = command_factory()
            else:
                # It's a class, instantiate it
                command = command_factory()
                
            return command.run(command_args)
        except Exception as e:
            print(f"Error executing command '{command_name}': {e}")
            return 1

    def show_help(self):
        """Show help information"""
        print("Larapy Console Application")
        print("")
        print("Usage:")
        print("  larapy <command> [arguments] [options]")
        print("")
        self.show_available_commands()

    def show_version(self):
        """Show version information"""
        print("Larapy Framework 1.0.0")

    def show_available_commands(self):
        """Show available commands"""
        print("Available commands:")
        
        # Group commands by category
        categories = {
            'make': [],
            'migrate': [],
            'db': [],
            'other': []
        }
        
        for command_name in sorted(self.commands.keys()):
            if command_name.startswith('make:'):
                categories['make'].append(command_name)
            elif command_name.startswith('migrate'):
                categories['migrate'].append(command_name)
            elif command_name.startswith('db:'):
                categories['db'].append(command_name)
            else:
                categories['other'].append(command_name)
        
        # Display categories
        for category, commands in categories.items():
            if commands:
                print(f"\n {category}:")
                for cmd in commands:
                    print(f"  {cmd}")

    def call(self, command: str, parameters: Dict[str, Any] = None) -> int:
        """Programmatically call a command"""
        if parameters is None:
            parameters = {}
        
        # Convert parameters to args list
        args = [command]
        for key, value in parameters.items():
            if key.startswith('--'):
                args.append(key)
                if value is not True:
                    args.append(str(value))
            else:
                args.append(str(value))
        
        return self.handle(args)