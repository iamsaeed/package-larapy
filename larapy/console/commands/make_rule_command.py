"""Make rule console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeRuleCommand(Command):
    """Create a new validation rule"""
    
    signature = "make:rule {name : The name of the rule class}"
    description = "Create a new validation rule"

    def handle(self) -> int:
        """Execute the make:rule command"""
        
        # Get rule name from arguments
        rule_name = self.argument('name')
        if not rule_name:
            rule_name = self.ask("What should the rule be named?")
        
        if not rule_name:
            self.error("Rule name is required.")
            return 1

        # Clean rule name
        rule_name = self._clean_rule_name(rule_name)

        try:
            # Create the rule file
            self._create_rule_file(rule_name)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create rule: {str(e)}")
            return 1

    def _clean_rule_name(self, name: str) -> str:
        """Clean and format rule name"""
        # Add Rule suffix if not present
        if not name.endswith('Rule'):
            name = name + 'Rule'
        
        # Split CamelCase and capitalize each word properly
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name[:-4] if name.endswith('Rule') else name)
        cleaned_name = ''.join(word.capitalize() for word in words)
        
        return cleaned_name + 'Rule'

    def _create_rule_file(self, rule_name: str):
        """Create the rule file"""
        # Create rules directory if it doesn't exist
        rules_dir = "app/Rules"
        os.makedirs(rules_dir, exist_ok=True)

        # Create rule file path
        rule_file = os.path.join(rules_dir, f"{rule_name}.py")

        # Check if file already exists
        if os.path.exists(rule_file):
            self.error(f"Rule {rule_name} already exists.")
            return

        # Generate rule content
        content = self._get_rule_stub(rule_name)

        # Write rule file
        with open(rule_file, 'w') as f:
            f.write(content)

        self.success(f"Rule {rule_name} created successfully.")
        self.info(f"File: {rule_file}")

    def _get_rule_stub(self, rule_name: str) -> str:
        """Get the rule stub content"""
        rule_name_without_suffix = rule_name[:-4] if rule_name.endswith('Rule') else rule_name
        
        return f'''"""
{rule_name}

Custom validation rule for {rule_name_without_suffix.lower()} validation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'package-larapy'))

from larapy.validation.rule import Rule
from typing import Any, Optional


class {rule_name}(Rule):
    """
    {rule_name}
    
    Custom validation rule for {rule_name_without_suffix.lower()} validation.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the validation rule
        
        Args:
            *args: Positional arguments for the rule
            **kwargs: Keyword arguments for the rule
        """
        super().__init__()
        self.args = args
        self.kwargs = kwargs
    
    def passes(self, attribute: str, value: Any) -> bool:
        """
        Determine if the validation rule passes
        
        Args:
            attribute: The attribute name being validated
            value: The value being validated
            
        Returns:
            True if validation passes, False otherwise
        """
        # Add your validation logic here
        # Example validations:
        
        # Check if value is not None or empty
        if value is None or (isinstance(value, str) and not value.strip()):
            return False
        
        # Example: String length validation
        # if isinstance(value, str):
        #     min_length = self.kwargs.get('min_length', 1)
        #     max_length = self.kwargs.get('max_length', 255)
        #     return min_length <= len(value) <= max_length
        
        # Example: Numeric range validation
        # if isinstance(value, (int, float)):
        #     min_value = self.kwargs.get('min_value', 0)
        #     max_value = self.kwargs.get('max_value', 100)
        #     return min_value <= value <= max_value
        
        # Example: Email format validation
        # if isinstance(value, str):
        #     import re
        #     email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$'
        #     return re.match(email_pattern, value) is not None
        
        # Example: Custom business logic
        # if isinstance(value, str):
        #     forbidden_words = ['spam', 'test', 'admin']
        #     return not any(word in value.lower() for word in forbidden_words)
        
        # Default: return True (passes validation)
        return True
    
    def message(self) -> str:
        """
        Get the validation error message
        
        Returns:
            The validation error message
        """
        # Return a custom error message
        return f"The :attribute field does not pass {rule_name_without_suffix.lower()} validation."
        
        # You can also return dynamic messages based on the rule parameters
        # Example:
        # if 'min_length' in self.kwargs:
        #     return f"The :attribute must be at least {{self.kwargs['min_length']}} characters."
        # return "The :attribute is invalid."
    
    def __str__(self) -> str:
        """
        Get the string representation of the rule
        
        Returns:
            String representation of the rule
        """
        return f"{rule_name_without_suffix.lower()}"
    
    # Optional: Add additional methods for complex validation
    def set_parameters(self, parameters: list) -> 'Rule':
        """
        Set rule parameters from validation string
        
        Args:
            parameters: List of parameters from validation rule string
            
        Returns:
            Self for method chaining
        """
        # Parse parameters if your rule accepts them
        # Example: "custom_rule:min_length=5,max_length=100"
        for param in parameters:
            if '=' in param:
                key, value = param.split('=', 1)
                try:
                    # Try to convert to int/float if possible
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)
                    self.kwargs[key] = value
                except ValueError:
                    self.kwargs[key] = value
            else:
                self.args = self.args + (param,)
        
        return self
    
    def get_size(self, value: Any) -> Optional[int]:
        """
        Get the size of the value for size-based validation
        
        Args:
            value: The value to get size for
            
        Returns:
            Size of the value or None
        """
        if isinstance(value, str):
            return len(value)
        elif isinstance(value, (list, tuple, dict)):
            return len(value)
        elif isinstance(value, (int, float)):
            return value
        return None
'''