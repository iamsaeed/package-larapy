"""Make request console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeRequestCommand(Command):
    """Create a new form request class"""
    
    signature = "make:request {name : The name of the request class}"
    description = "Create a new form request class"

    def handle(self) -> int:
        """Execute the make:request command"""
        
        # Get request name from arguments
        request_name = self.argument('name')
        if not request_name:
            request_name = self.ask("What should the request be named?")
        
        if not request_name:
            self.error("Request name is required.")
            return 1

        # Clean request name
        request_name = self._clean_request_name(request_name)

        try:
            # Create the request file
            self._create_request_file(request_name)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create request: {str(e)}")
            return 1

    def _clean_request_name(self, name: str) -> str:
        """Clean and format request name"""
        # Add Request suffix if not present
        if not name.endswith('Request'):
            name = name + 'Request'
        
        # If it already ends with Request, just ensure proper capitalization of the whole name
        # Split on capital letters to handle CamelCase properly
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
        
        # Capitalize each word and join them
        return ''.join(word.capitalize() for word in words)

    def _create_request_file(self, request_name: str):
        """Create the request file"""
        # Create Requests directory if it doesn't exist
        requests_dir = "app/Http/Requests"
        os.makedirs(requests_dir, exist_ok=True)

        # Create request file path
        request_file = os.path.join(requests_dir, f"{request_name}.py")

        # Check if file already exists
        if os.path.exists(request_file):
            self.error(f"Request {request_name} already exists.")
            return

        # Generate request content
        content = self._get_request_stub(request_name)

        # Write request file
        with open(request_file, 'w') as f:
            f.write(content)

        self.success(f"Request {request_name} created successfully.")
        self.info(f"File: {request_file}")

    def _get_request_stub(self, request_name: str) -> str:
        """Get the request stub content"""
        class_name_without_suffix = request_name[:-7] if request_name.endswith('Request') else request_name
        
        return f'''"""
{request_name}

Form request class for {class_name_without_suffix.lower()} validation and authorization.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'package-larapy'))

from larapy.http.form_request import FormRequest
from typing import Dict, Union, List, Optional


class {request_name}(FormRequest):
    """
    {request_name}
    
    Handles validation and authorization for {class_name_without_suffix.lower()} requests.
    """
    
    def authorize(self) -> bool:
        """
        Determine if the user is authorized to make this request
        
        Returns:
            True if the user is authorized, False otherwise
        """
        # Add your authorization logic here
        # Example: return self.user() and self.user().can('create-{class_name_without_suffix.lower()}')
        return True
    
    def rules(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get the validation rules that apply to the request
        
        Returns:
            Dictionary of validation rules
        """
        return {{
            # Define your validation rules here
            # Example:
            # 'name': 'required|string|max:255',
            # 'email': 'required|email|unique:users,email',
            # 'password': 'required|string|min:8|confirmed',
        }}
    
    def messages(self) -> Dict[str, str]:
        """
        Get custom validation messages
        
        Returns:
            Dictionary of custom validation messages
        """
        return {{
            # Define custom validation messages here
            # Example:
            # 'name.required': 'The name field is required.',
            # 'email.email': 'Please provide a valid email address.',
            # 'password.min': 'The password must be at least 8 characters.',
        }}
    
    def attributes(self) -> Dict[str, str]:
        """
        Get custom attribute names for validation errors
        
        Returns:
            Dictionary of custom attribute names
        """
        return {{
            # Define custom attribute names here
            # Example:
            # 'email': 'email address',
            # 'first_name': 'given name',
        }}
    
    def prepare_for_validation(self):
        """
        Prepare the data for validation
        
        This method is called before validation occurs.
        Use it to modify or clean the input data.
        """
        # Add any data preparation logic here
        # Example:
        # self.merge([
        #     'slug': self.input('name', '').lower().replace(' ', '-')
        # ])
        pass
    
    def with_validator(self, validator):
        """
        Configure the validator instance
        
        Args:
            validator: The validator instance
        """
        # Add custom validation logic here
        # Example:
        # validator.after(lambda: self._validate_business_rules())
        pass
    
    def failed_validation(self, validator):
        """
        Handle a failed validation attempt
        
        Args:
            validator: The validator instance that failed
        """
        # Custom logic for handling validation failures
        # This is called before the ValidationException is thrown
        pass
'''