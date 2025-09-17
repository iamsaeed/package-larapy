"""
Make Middleware Command - Generate a middleware class.
"""

from ...generator_command import GeneratorCommand


class MakeMiddlewareCommand(GeneratorCommand):
    """Create a new middleware class"""
    
    signature = "make:middleware {name : The name of the middleware}"
    description = "Create a new middleware class"
    stub = "middleware.stub"
    
    def get_name_input(self) -> str:
        """Get the desired class name from the input"""
        # Get name from arguments first, then prompt if not provided
        name = self.argument('name')
        if name:
            return name
        return self.ask("Middleware name", "ExampleMiddleware")
    
    def get_name(self) -> str:
        """Get the command name"""
        return "make:middleware"