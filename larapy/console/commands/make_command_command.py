"""Make command console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeCommandCommand(Command):
    """Create a new console command"""
    
    signature = "make:command {name : The name of the command class} {--command= : The terminal command that should be assigned}"
    description = "Create a new Artisan command"

    def handle(self) -> int:
        """Execute the make:command command"""
        
        # Get command name from arguments
        command_name = self.argument('name')
        if not command_name:
            command_name = self.ask("What should the command be named?")
        
        if not command_name:
            self.error("Command name is required.")
            return 1

        # Clean command name
        command_name = self._clean_command_name(command_name)

        # Get the terminal command name
        terminal_command = self.option('command')
        if not terminal_command:
            # Generate a default command name based on the class name
            terminal_command = self._generate_terminal_command(command_name)

        try:
            # Create the command file
            self._create_command_file(command_name, terminal_command)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create command: {str(e)}")
            return 1

    def _clean_command_name(self, name: str) -> str:
        """Clean and format command name"""
        # Add Command suffix if not present
        if not name.endswith('Command'):
            name = name + 'Command'
        
        # Remove Command suffix for processing
        base_name = name[:-7] if name.endswith('Command') else name
        
        # Split CamelCase and capitalize each word properly
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', base_name)
        cleaned_name = ''.join(word.capitalize() for word in words)
        
        return cleaned_name + 'Command'

    def _generate_terminal_command(self, command_name: str) -> str:
        """Generate a terminal command name from the class name"""
        # Remove 'Command' suffix and convert to snake_case
        base_name = command_name.replace('Command', '')
        
        # Convert CamelCase to snake_case
        import re
        snake_case = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', base_name)
        snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case).lower()
        
        return f"app:{snake_case}"

    def _create_command_file(self, command_name: str, terminal_command: str):
        """Create the command file"""
        # Create commands directory if it doesn't exist
        commands_dir = "app/Console/Commands"
        os.makedirs(commands_dir, exist_ok=True)

        # Create command file path
        command_file = os.path.join(commands_dir, f"{command_name}.py")

        # Check if file already exists
        if os.path.exists(command_file):
            self.error(f"Command {command_name} already exists.")
            return

        # Generate command content
        content = self._get_command_stub(command_name, terminal_command)

        # Write command file
        with open(command_file, 'w') as f:
            f.write(content)

        self.success(f"Command {command_name} created successfully.")
        self.info(f"File: {command_file}")
        self.comment(f"Don't forget to register your command in the console kernel")
        self.comment(f"Terminal command: {terminal_command}")

    def _get_command_stub(self, command_name: str, terminal_command: str) -> str:
        """Get the command stub content"""
        class_name_without_suffix = command_name[:-7] if command_name.endswith('Command') else command_name
        
        return f'''"""
{command_name}

Custom console command for {class_name_without_suffix.lower()} operations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'package-larapy'))

from larapy.console.command import Command


class {command_name}(Command):
    """
    {command_name}
    
    Handles {class_name_without_suffix.lower()} operations via the command line.
    """
    
    signature = "{terminal_command} {{--option= : Optional parameter}}"
    description = "Command description for {class_name_without_suffix.lower()}"

    def handle(self) -> int:
        """
        Execute the console command
        
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        # Add your command logic here
        self.info("Starting {class_name_without_suffix.lower()} command...")
        
        # Example: Get option values
        option_value = self.option('option')
        if option_value:
            self.line(f"Option value: {{option_value}}")
        
        # Example: Ask for user input
        # user_input = self.ask("Enter something")
        # self.line(f"You entered: {{user_input}}")
        
        # Example: Confirm action
        # if self.confirm("Are you sure you want to continue?"):
        #     self.info("Proceeding...")
        # else:
        #     self.info("Cancelled.")
        #     return 1
        
        # Your command implementation goes here
        try:
            # Example implementation
            self.line("Executing {class_name_without_suffix.lower()} logic...")
            
            # Simulate some work
            import time
            time.sleep(1)
            
            self.success("{class_name_without_suffix} command completed successfully!")
            return 0
            
        except Exception as e:
            self.error(f"Command failed: {{str(e)}}")
            return 1
    
    def get_arguments(self):
        """
        Get the command arguments
        
        Returns:
            List of argument definitions
        """
        return [
            # Define command arguments here
            # Example: ('filename', 'The name of the file to process')
        ]
    
    def get_options(self):
        """
        Get the command options
        
        Returns:
            List of option definitions
        """
        return [
            # Define command options here
            # Example: ('force', 'f', 'Force the operation')
            ('option', 'o', 'Optional parameter for the command'),
        ]
'''