"""
Base Command class for Larapy console commands.

Provides Laravel-like command functionality with signature-based argument parsing,
container access, and interactive features.
"""

import sys
import os
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod


class Command(ABC):
    """
    Base command class with Larapy-specific functionality.
    
    Similar to Laravel's Illuminate\\Console\\Command class.
    """
    
    # Command signature (Laravel-style)
    signature: str = ""
    
    # Command description
    description: str = ""
    
    # Hidden commands don't appear in help listings
    hidden: bool = False
    
    def __init__(self, app=None):
        """Initialize the command"""
        self.app = app
        self._arguments: Dict[str, Any] = {}
        self._options: Dict[str, Any] = {}
        self._input_args: List[str] = []
        self._parsed = False
    
    @abstractmethod
    def handle(self) -> int:
        """
        Execute the command.
        
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        pass
    
    def run(self, args: List[str] = None) -> int:
        """
        Run the command with given arguments.
        
        Args:
            args: Command line arguments
            
        Returns:
            int: Exit code
        """
        if args is None:
            args = sys.argv[1:]
            
        self._input_args = args
        self._parse_arguments()
        
        try:
            return self.handle()
        except Exception as e:
            self.error(f"Command failed: {str(e)}")
            if self.app and hasattr(self.app, 'debug') and self.app.debug:
                import traceback
                self.line(traceback.format_exc())
            return 1
    
    def _parse_arguments(self):
        """Parse command arguments and options from signature"""
        if not self.signature:
            return
            
        # Parse the signature to extract command name, arguments, and options
        import re
        
        # Use regex to find all {parameter} patterns in the signature
        param_pattern = r'\{([^}]+)\}'
        param_matches = re.findall(param_pattern, self.signature)
        
        # Parse arguments and options from input
        args = []
        options = {}
        i = 0
        
        while i < len(self._input_args):
            arg = self._input_args[i]
            
            if arg.startswith('--'):
                # Long option
                option_name = arg[2:]
                if '=' in option_name:
                    # --option=value
                    key, value = option_name.split('=', 1)
                    options[key] = value
                else:
                    # --option (boolean or next arg is value)
                    if i + 1 < len(self._input_args) and not self._input_args[i + 1].startswith('-'):
                        # Next arg is the value
                        i += 1
                        options[option_name] = self._input_args[i]
                    else:
                        # Boolean option
                        options[option_name] = True
            elif arg.startswith('-'):
                # Short option
                option_name = arg[1:]
                if i + 1 < len(self._input_args) and not self._input_args[i + 1].startswith('-'):
                    i += 1
                    options[option_name] = self._input_args[i]
                else:
                    options[option_name] = True
            else:
                # Regular argument
                args.append(arg)
            
            i += 1
        
        # Parse signature parameters
        expected_args = []
        expected_options = {}
        
        for param in param_matches:
            if param.startswith('--'):
                # Option definition: {--option : description}
                option_def = param[2:]
                if ':' in option_def:
                    option_name = option_def.split(':')[0].strip()
                else:
                    option_name = option_def.strip()
                expected_options[option_name] = True
            else:
                # Argument definition: {name? : description} or {name : description}
                if ':' in param:
                    arg_part = param.split(':')[0].strip()
                else:
                    arg_part = param.strip()
                
                optional = arg_part.endswith('?')
                if optional:
                    arg_part = arg_part[:-1]
                
                expected_args.append({
                    'name': arg_part,
                    'optional': optional
                })
        
        # Map parsed arguments to expected arguments
        for i, arg_def in enumerate(expected_args):
            if i < len(args):
                self._arguments[arg_def['name']] = args[i]
            elif not arg_def['optional']:
                # Required argument missing - could prompt for it
                pass
        
        # Store parsed options
        self._options.update(options)
        
        self._parsed = True
    
    def argument(self, name: str, default: Any = None) -> Any:
        """
        Get an argument value.
        
        Args:
            name: Argument name
            default: Default value if not found
            
        Returns:
            Argument value
        """
        return self._arguments.get(name, default)
    
    def option(self, name: str, default: Any = None) -> Any:
        """
        Get an option value.
        
        Args:
            name: Option name  
            default: Default value if not found
            
        Returns:
            Option value
        """
        return self._options.get(name, default)
    
    def ask(self, question: str, default: str = None) -> str:
        """
        Ask a question and return the response.
        
        Args:
            question: Question to ask
            default: Default value
            
        Returns:
            User response
        """
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "
            
        response = input(prompt).strip()
        return response if response else default
    
    def confirm(self, question: str, default: bool = False) -> bool:
        """
        Ask a yes/no question.
        
        Args:
            question: Question to ask
            default: Default response
            
        Returns:
            True for yes, False for no
        """
        default_text = "Y/n" if default else "y/N"
        response = input(f"{question} ({default_text}): ").strip().lower()
        
        if not response:
            return default
            
        return response in ('y', 'yes', '1', 'true')
    
    def choice(self, question: str, choices: List[str], default: str = None) -> str:
        """
        Give the user a choice between options.
        
        Args:
            question: Question to ask
            choices: Available choices
            default: Default choice
            
        Returns:
            Selected choice
        """
        self.info(question)
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if choice == default else ""
            self.line(f"  [{i}] {choice}{marker}")
        
        while True:
            response = input("Choice: ").strip()
            
            if not response and default:
                return default
                
            try:
                index = int(response) - 1
                if 0 <= index < len(choices):
                    return choices[index]
            except ValueError:
                pass
                
            if response in choices:
                return response
                
            self.error("Invalid choice. Please try again.")
    
    def line(self, text: str = "", style: str = None):
        """
        Write a line of text.
        
        Args:
            text: Text to write
            style: Optional style (info, error, warning, etc.)
        """
        if style:
            text = self._style_text(text, style)
        print(text)
    
    def info(self, text: str):
        """Write an info message"""
        self.line(f"ℹ️  {text}", "info")
    
    def error(self, text: str):
        """Write an error message"""  
        self.line(f"❌ {text}", "error")
    
    def warning(self, text: str):
        """Write a warning message"""
        self.line(f"⚠️  {text}", "warning")
        
    def success(self, text: str):
        """Write a success message"""
        self.line(f"✅ {text}", "success")
    
    def comment(self, text: str):
        """Write a comment"""
        self.line(f"💬 {text}", "comment")
    
    def table(self, headers: List[str], rows: List[List[str]]):
        """
        Display a table.
        
        Args:
            headers: Table headers
            rows: Table rows
        """
        # Simple table implementation
        if not rows:
            return
            
        # Calculate column widths
        widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Print headers
        header_line = " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
        self.line(header_line)
        self.line("-" * len(header_line))
        
        # Print rows
        for row in rows:
            row_line = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            self.line(row_line)
    
    def _style_text(self, text: str, style: str) -> str:
        """Apply styling to text (basic implementation)"""
        # Basic color codes for terminal
        styles = {
            'info': '\033[94m',      # Blue
            'error': '\033[91m',     # Red  
            'warning': '\033[93m',   # Yellow
            'success': '\033[92m',   # Green
            'comment': '\033[90m',   # Gray
        }
        
        reset = '\033[0m'
        color = styles.get(style, '')
        
        return f"{color}{text}{reset}"
    
    def call(self, command: str, args: List[str] = None) -> int:
        """
        Call another command.
        
        Args:
            command: Command name to call
            args: Arguments to pass
            
        Returns:
            Exit code from called command
        """
        # This would need to be implemented with the console application
        self.comment(f"Would call command: {command} with args: {args or []}")
        return 0
    
    def get_name(self) -> str:
        """Get the command name from signature"""
        if not self.signature:
            return self.__class__.__name__.lower().replace('command', '')
            
        # Extract command name from signature
        parts = self.signature.split()
        return parts[0] if parts else ''