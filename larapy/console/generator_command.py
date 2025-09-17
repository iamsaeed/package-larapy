"""
Generator Command class for creating files from stubs.

Provides Laravel-like code generation functionality with stub template processing,
file generation, and directory creation.
"""

import os
import re
from typing import Dict, Any, Optional
from .command import Command


class GeneratorCommand(Command):
    """
    Base class for code generation commands.
    
    Similar to Laravel's Illuminate\\Console\\GeneratorCommand class.
    """
    
    # The stub file name
    stub: str = ""
    
    # Default namespace
    default_namespace: str = "App"
    
    def __init__(self, app=None):
        """Initialize the generator command"""
        super().__init__(app)
    
    def handle(self) -> int:
        """Handle the command execution"""
        name = self.get_name_input()
        
        if not name:
            self.error("Name argument is required")
            return 1
        
        # Get the fully qualified class name
        name = self.qualify_class(name)
        
        # Get the destination path
        path = self.get_path(name)
        
        # Check if file already exists
        if self.already_exists(path):
            self.error(f"File {path} already exists!")
            return 1
        
        # Make directory if needed
        self.make_directory(path)
        
        # Build the class content
        content = self.build_class(name)
        
        # Write the file
        with open(path, 'w') as f:
            f.write(content)
        
        self.success(f"Created: {path}")
        return 0
    
    def get_name_input(self) -> str:
        """Get the desired class name from the input"""
        # This would normally parse from command arguments
        # For now, return a placeholder
        return "ExampleClass"
    
    def qualify_class(self, name: str) -> str:
        """
        Qualify the given class name with the default namespace.
        
        Args:
            name: Class name to qualify
            
        Returns:
            Fully qualified class name
        """
        name = name.strip()
        
        # Remove leading slashes
        name = name.lstrip('\\/')
        
        # If already has namespace, return as-is
        if '\\' in name or '/' in name:
            return name.replace('/', '\\')
        
        # Add default namespace
        return f"{self.default_namespace}\\{name}"
    
    def get_path(self, name: str) -> str:
        """
        Get the destination path for the class.
        
        Args:
            name: Fully qualified class name
            
        Returns:
            File path where class should be created
        """
        # Convert namespace to path
        path = name.replace('\\', '/').replace('App/', 'app/')
        
        # Add .py extension
        path += '.py'
        
        # Get base path from app if available
        if self.app and hasattr(self.app, 'base_path'):
            base_path = self.app.base_path()
        else:
            base_path = os.getcwd()
        
        return os.path.join(base_path, path)
    
    def already_exists(self, path: str) -> bool:
        """
        Check if the file already exists.
        
        Args:
            path: File path to check
            
        Returns:
            True if file exists
        """
        return os.path.exists(path)
    
    def make_directory(self, path: str):
        """
        Create the directory for the given path if it doesn't exist.
        
        Args:
            path: File path
        """
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def build_class(self, name: str) -> str:
        """
        Build the class content from the stub.
        
        Args:
            name: Fully qualified class name
            
        Returns:
            Generated class content
        """
        stub_content = self.get_stub()
        
        return self.replace_placeholders(stub_content, name)
    
    def get_stub(self) -> str:
        """
        Get the stub file content.
        
        Returns:
            Stub file content
        """
        if not self.stub:
            raise ValueError("Stub file not specified")
        
        # Get stubs directory
        stubs_dir = self.get_stubs_directory()
        stub_path = os.path.join(stubs_dir, self.stub)
        
        if not os.path.exists(stub_path):
            raise FileNotFoundError(f"Stub file not found: {stub_path}")
        
        with open(stub_path, 'r') as f:
            return f.read()
    
    def get_stubs_directory(self) -> str:
        """
        Get the stubs directory path.
        
        Returns:
            Path to stubs directory
        """
        # Default to package stubs directory
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(package_dir, 'console', 'stubs')
    
    def replace_placeholders(self, stub: str, name: str) -> str:
        """
        Replace placeholders in the stub with actual values.
        
        Args:
            stub: Stub content
            name: Fully qualified class name
            
        Returns:
            Stub with placeholders replaced
        """
        replacements = self.get_replacements(name)
        
        for placeholder, replacement in replacements.items():
            stub = stub.replace(placeholder, replacement)
        
        return stub
    
    def get_replacements(self, name: str) -> Dict[str, str]:
        """
        Get the array of replacements for the stub.
        
        Args:
            name: Fully qualified class name
            
        Returns:
            Dictionary of placeholder -> replacement mappings
        """
        class_name = self.get_class_name(name)
        namespace = self.get_namespace(name)
        
        return {
            '{{ class }}': class_name,
            '{{class}}': class_name,
            '{{ namespace }}': namespace,
            '{{namespace}}': namespace,
            '{{ table }}': self.get_table_name(class_name),
            '{{table}}': self.get_table_name(class_name),
        }
    
    def get_class_name(self, name: str) -> str:
        """
        Get the class name from the fully qualified name.
        
        Args:
            name: Fully qualified class name
            
        Returns:
            Class name without namespace
        """
        return name.split('\\')[-1]
    
    def get_namespace(self, name: str) -> str:
        """
        Get the namespace from the fully qualified name.
        
        Args:
            name: Fully qualified class name
            
        Returns:
            Namespace without class name
        """
        parts = name.split('\\')
        if len(parts) > 1:
            return '\\'.join(parts[:-1])
        return ''
    
    def get_table_name(self, class_name: str) -> str:
        """
        Get the table name from the class name.
        
        Args:
            class_name: Class name
            
        Returns:
            Database table name (snake_case, plural)
        """
        # Convert CamelCase to snake_case
        table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        
        # Simple pluralization
        if table_name.endswith('y'):
            table_name = table_name[:-1] + 'ies'
        elif table_name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            table_name += 'es'
        else:
            table_name += 's'
        
        return table_name
    
    def get_default_namespace(self, root_namespace: str) -> str:
        """
        Get the default namespace for the class.
        
        Args:
            root_namespace: Root namespace
            
        Returns:
            Default namespace
        """
        return root_namespace