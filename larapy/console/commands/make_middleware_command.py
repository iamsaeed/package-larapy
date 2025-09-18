"""Make middleware console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeMiddlewareCommand(Command):
    """Create a new middleware"""
    
    signature = "make:middleware {name : The name of the middleware}"
    description = "Create a new middleware class"

    def handle(self) -> int:
        """Execute the make:middleware command"""
        
        # Get middleware name from arguments
        middleware_name = self.argument('name')
        if not middleware_name:
            middleware_name = self.ask("What should the middleware be named?")
        
        if not middleware_name:
            self.error("Middleware name is required.")
            return 1

        # Clean middleware name
        middleware_name = self._clean_middleware_name(middleware_name)

        try:
            # Create the middleware file
            self._create_middleware_file(middleware_name)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create middleware: {str(e)}")
            return 1

    def _clean_middleware_name(self, name: str) -> str:
        """Clean and format middleware name"""
        # Add Middleware suffix if not present
        if not name.endswith('Middleware'):
            name = name + 'Middleware'
        
        # Ensure proper capitalization (capitalize each word)
        return ''.join(word.capitalize() for word in name.split('Middleware')[0].split()) + 'Middleware'

    def _create_middleware_file(self, middleware_name: str):
        """Create the middleware file"""
        # Create Middleware directory if it doesn't exist
        middleware_dir = "app/Http/Middleware"
        os.makedirs(middleware_dir, exist_ok=True)

        # Create middleware file path
        middleware_file = os.path.join(middleware_dir, f"{middleware_name}.py")

        # Check if file already exists
        if os.path.exists(middleware_file):
            self.error(f"Middleware {middleware_name} already exists.")
            return

        # Generate middleware content
        content = self._get_middleware_stub(middleware_name)

        # Write middleware file
        with open(middleware_file, 'w') as f:
            f.write(content)

        self.success(f"Middleware {middleware_name} created successfully.")
        self.info(f"File: {middleware_file}")
        self.comment("Don't forget to register your middleware in app/Http/Kernel.py")

    def _get_middleware_stub(self, middleware_name: str) -> str:
        """Get the middleware stub content"""
        class_name_without_suffix = middleware_name[:-10] if middleware_name.endswith('Middleware') else middleware_name
        
        return f'''"""
{middleware_name}

{class_name_without_suffix} middleware for handling HTTP requests.
"""

from larapy.http.middleware.middleware import Middleware
from typing import Callable


class {middleware_name}(Middleware):
    """
    {middleware_name}
    
    This middleware handles {class_name_without_suffix.lower()} functionality for incoming requests.
    """
    
    def handle(self, request, next_handler: Callable):
        """
        Handle the incoming request
        
        Args:
            request: The HTTP request object
            next_handler: The next middleware/handler in the pipeline
            
        Returns:
            HTTP response
        """
        # Before processing request
        # Add your pre-processing logic here
        # Example: authentication, logging, validation
        
        # Process the request through the pipeline
        response = next_handler(request)
        
        # After processing request
        # Add your post-processing logic here
        # Example: modify response headers, logging, cleanup
        
        return response
    
    def terminate(self, request, response):
        """
        Perform any final work after the response has been sent to the browser
        
        Args:
            request: The HTTP request object
            response: The HTTP response object
        """
        # Optional: Add any cleanup or finalization logic here
        # This method is called after the response has been sent
        pass
'''