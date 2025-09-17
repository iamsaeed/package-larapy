"""
Make Controller Command - Generate a controller class.
"""

from ...generator_command import GeneratorCommand


class MakeControllerCommand(GeneratorCommand):
    """Create a new controller class"""
    
    signature = "make:controller {name : The name of the controller}"
    description = "Create a new controller class"
    stub = "controller.stub"
    
    def get_name_input(self) -> str:
        """Get the desired class name from the input"""
        # Get name from arguments first, then prompt if not provided
        name = self.argument('name')
        if name:
            return name
        return self.ask("Controller name", "ExampleController")
    
    def get_name(self) -> str:
        """Get the command name"""
        return "make:controller"