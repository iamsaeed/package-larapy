"""
Make Model Command - Generate a model class.
"""

from ...generator_command import GeneratorCommand


class MakeModelCommand(GeneratorCommand):
    """Create a new model class"""
    
    signature = "make:model {name : The name of the model}"
    description = "Create a new model class"
    stub = "model.stub"
    
    def get_name_input(self) -> str:
        """Get the desired class name from the input"""
        # Get name from arguments first, then prompt if not provided
        name = self.argument('name')
        if name:
            return name
        return self.ask("Model name", "ExampleModel")
    
    def get_name(self) -> str:
        """Get the command name"""
        return "make:model"