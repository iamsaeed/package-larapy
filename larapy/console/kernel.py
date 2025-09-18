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
        self.register_application_commands()

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
        
        # Register general make commands
        try:
            from .commands.make_model_command import MakeModelCommand
            from .commands.make_controller_command import MakeControllerCommand
            from .commands.make_middleware_command import MakeMiddlewareCommand
            from .commands.make_provider_command import MakeProviderCommand
            from .commands.serve_command import ServeCommand
            from .commands.route_list_command import RouteListCommand
            from .commands.make_request_command import MakeRequestCommand
            from .commands.make_command_command import MakeCommandCommand
            from .commands.make_test_command import MakeTestCommand
            from .commands.config_show_command import ConfigShowCommand
            from .commands.make_rule_command import MakeRuleCommand
            from .commands.make_observer_command import MakeObserverCommand
            
            # Phase 1 commands
            self.register_command('make:model', lambda: MakeModelCommand())
            self.register_command('make:controller', lambda: MakeControllerCommand())
            self.register_command('make:middleware', lambda: MakeMiddlewareCommand())
            self.register_command('make:provider', lambda: MakeProviderCommand())
            self.register_command('serve', lambda: ServeCommand())
            
            # Phase 2 commands
            self.register_command('route:list', lambda: RouteListCommand())
            self.register_command('make:request', lambda: MakeRequestCommand())
            self.register_command('make:command', lambda: MakeCommandCommand())
            self.register_command('make:test', lambda: MakeTestCommand())
            self.register_command('config:show', lambda: ConfigShowCommand())
            
            # Phase 3 commands
            self.register_command('make:rule', lambda: MakeRuleCommand())
            self.register_command('make:observer', lambda: MakeObserverCommand())
            
        except ImportError as e:
            print(f"Warning: Could not register general commands: {e}")
        
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
            # Check for prefix matches
            prefix_matches = self.find_prefix_matches(command_name)
            if prefix_matches:
                self.show_prefix_matches(command_name, prefix_matches)
                return 1
            else:
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

    def find_prefix_matches(self, prefix: str) -> List[str]:
        """Find commands that start with the given prefix"""
        matches = []
        prefix_with_colon = prefix + ':'
        
        for command_name in self.commands.keys():
            if command_name.startswith(prefix_with_colon):
                matches.append(command_name)
        
        return sorted(matches)

    def show_prefix_matches(self, prefix: str, matches: List[str]):
        """Show available commands for a given prefix"""
        print(f"Command '{prefix}' not found.")
        print(f"\n✨ Did you mean one of these commands with '{prefix}:' prefix?")
        print("=" * 70)
        
        for command_name in matches:
            try:
                # Get command description
                command_factory = self.commands[command_name]
                if callable(command_factory) and not hasattr(command_factory, 'handle'):
                    command = command_factory()
                else:
                    command = command_factory()
                
                description = getattr(command, 'description', 'No description available')
                print(f"  📝 {command_name:<20} {description}")
                
            except Exception:
                print(f"  📝 {command_name:<20} Available command")
        
        print(f"\n💡 Usage:")
        print(f"   larapy <command> [arguments] [options]")
        print(f"\n🚀 Example:")
        if matches:
            print(f"   larapy {matches[0]}")
        
        print(f"\n💭 Tip: Use 'larapy --help' to see all available commands.")

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
            'app': [],
            'other': []
        }
        
        for command_name in sorted(self.commands.keys()):
            if command_name.startswith('make:'):
                categories['make'].append(command_name)
            elif command_name.startswith('migrate'):
                categories['migrate'].append(command_name)
            elif command_name.startswith('db:'):
                categories['db'].append(command_name)
            elif command_name.startswith('app:'):
                categories['app'].append(command_name)
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

    def register_application_commands(self):
        """Auto-discover and register custom commands from app/console/commands/"""
        try:
            commands_dir = "app/console/commands"
            if not os.path.exists(commands_dir):
                return
            
            # Add current directory to Python path for importing
            current_dir = os.getcwd()
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # Scan for Python files in the commands directory
            for file_name in os.listdir(commands_dir):
                if file_name.endswith('.py') and file_name != '__init__.py':
                    try:
                        # Import the module
                        module_name = f"app.console.commands.{file_name[:-3]}"
                        module = __import__(module_name, fromlist=[''])
                        
                        # Find command classes in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            
                            # Check if it's a command class (inherits from Command and not the base Command)
                            if (isinstance(attr, type) and 
                                hasattr(attr, 'signature') and 
                                hasattr(attr, 'handle') and
                                attr_name != 'Command'):
                                
                                try:
                                    # Create an instance to get the command name
                                    instance = attr()
                                    
                                    # Get command name from signature or get_name method
                                    if hasattr(instance, 'get_name'):
                                        command_name = instance.get_name()
                                    elif hasattr(instance, 'signature'):
                                        # Extract command name from signature
                                        signature = instance.signature
                                        command_name = signature.split()[0] if signature else attr_name.lower()
                                    else:
                                        command_name = attr_name.lower()
                                    
                                    # Register the command
                                    self.register_command(command_name, lambda cls=attr: cls())
                                    
                                except Exception as e:
                                    print(f"Warning: Could not register command {attr_name}: {e}")
                                    
                    except Exception as e:
                        print(f"Warning: Could not import command file {file_name}: {e}")
                        
        except Exception as e:
            print(f"Warning: Could not scan for application commands: {e}")