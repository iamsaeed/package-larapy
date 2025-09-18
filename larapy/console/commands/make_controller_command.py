"""Make controller console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeControllerCommand(Command):
    """Create a new controller"""
    
    signature = "make:controller {name : The name of the controller} {--resource : Generate a resource controller} {--api : Generate an API controller} {--model= : Generate a resource controller for the given model}"
    description = "Create a new controller class"

    def handle(self) -> int:
        """Execute the make:controller command"""
        
        # Get controller name from arguments
        controller_name = self.argument('name')
        if not controller_name:
            controller_name = self.ask("What should the controller be named?")
        
        if not controller_name:
            self.error("Controller name is required.")
            return 1

        # Clean controller name
        controller_name = self._clean_controller_name(controller_name)

        # Check options
        is_resource = self.option('resource')
        is_api = self.option('api')
        model_name = self.option('model')

        try:
            # Create the controller file
            self._create_controller_file(controller_name, is_resource, is_api, model_name)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create controller: {str(e)}")
            return 1

    def _clean_controller_name(self, name: str) -> str:
        """Clean and format controller name"""
        # Add Controller suffix if not present
        if not name.endswith('Controller'):
            name = name + 'Controller'
        
        # Remove Controller suffix for processing
        base_name = name[:-10] if name.endswith('Controller') else name
        
        # Split CamelCase and capitalize each word properly
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', base_name)
        cleaned_name = ''.join(word.capitalize() for word in words)
        
        return cleaned_name + 'Controller'

    def _create_controller_file(self, controller_name: str, is_resource: bool = False, is_api: bool = False, model_name: Optional[str] = None):
        """Create the controller file"""
        # Create Controllers directory if it doesn't exist
        controllers_dir = "app/Http/Controllers"
        os.makedirs(controllers_dir, exist_ok=True)

        # Create controller file path
        controller_file = os.path.join(controllers_dir, f"{controller_name}.py")

        # Check if file already exists
        if os.path.exists(controller_file):
            self.error(f"Controller {controller_name} already exists.")
            return

        # Generate controller content
        if is_resource or model_name:
            content = self._get_resource_controller_stub(controller_name, is_api, model_name)
        else:
            content = self._get_basic_controller_stub(controller_name, is_api)

        # Write controller file
        with open(controller_file, 'w') as f:
            f.write(content)

        self.success(f"Controller {controller_name} created successfully.")
        self.info(f"File: {controller_file}")

    def _get_basic_controller_stub(self, controller_name: str, is_api: bool = False) -> str:
        """Get the basic controller stub content"""
        imports = []
        base_class = ""
        
        if is_api:
            imports.append("from larapy import Response")
            imports.append("from flask import jsonify, request")
        else:
            imports.append("from larapy import Response")
            imports.append("from flask import render_template, request")
        
        # Add base controller import
        imports.append("from larapy.http.concerns.validates_requests import Controller")
        base_class = "(Controller)"
        
        imports_str = "\n".join(imports)
        
        if is_api:
            methods = self._get_api_basic_methods()
        else:
            methods = self._get_web_basic_methods()
        
        return f'''"""{controller_name}"""

{imports_str}


class {controller_name}{base_class}:
    """{controller_name} class"""
    
    def __init__(self):
        super().__init__()
    
{methods}
'''

    def _get_resource_controller_stub(self, controller_name: str, is_api: bool = False, model_name: Optional[str] = None) -> str:
        """Get the resource controller stub content"""
        imports = []
        base_class = ""
        
        if is_api:
            imports.append("from larapy import Response")
            imports.append("from flask import jsonify, request")
        else:
            imports.append("from larapy import Response")
            imports.append("from flask import render_template, request, redirect, url_for")
        
        # Add base controller import
        imports.append("from larapy.http.concerns.validates_requests import Controller")
        base_class = "(Controller)"
        
        # Add model import if specified
        if model_name:
            imports.append(f"from app.Models.{model_name} import {model_name}")
        
        imports_str = "\n".join(imports)
        
        if is_api:
            methods = self._get_api_resource_methods(model_name)
        else:
            methods = self._get_web_resource_methods(model_name)
        
        return f'''"""{controller_name}"""

{imports_str}


class {controller_name}{base_class}:
    """{controller_name} class"""
    
    def __init__(self):
        super().__init__()
    
{methods}
'''

    def _get_web_basic_methods(self) -> str:
        """Get basic web controller methods"""
        return '''    def index(self):
        """Display the main view"""
        return render_template('index.html')
    
    def show(self, id):
        """Display a specific resource"""
        return render_template('show.html', id=id)'''

    def _get_api_basic_methods(self) -> str:
        """Get basic API controller methods"""
        return '''    def index(self):
        """Return a JSON response"""
        return {
            'message': 'Hello from API',
            'status': 'success'
        }
    
    def show(self, id):
        """Return a specific resource as JSON"""
        return {
            'id': id,
            'message': f'Resource {id} details',
            'status': 'success'
        }'''

    def _get_web_resource_methods(self, model_name: Optional[str] = None) -> str:
        """Get web resource controller methods"""
        model_var = model_name.lower() if model_name else 'item'
        model_class = model_name if model_name else 'Model'
        
        return f'''    def index(self):
        """Display a listing of the resource"""
        # {model_var}s = {model_class}.all()
        return render_template('{model_var}s/index.html')
    
    def create(self):
        """Show the form for creating a new resource"""
        return render_template('{model_var}s/create.html')
    
    def store(self):
        """Store a newly created resource in storage"""
        # Validate request
        data = self.validate_request({{
            'name': 'required|string|max:255',
            # Add your validation rules here
        }})
        
        # Create new {model_var}
        # {model_var} = {model_class}.create(data)
        
        # Redirect with success message
        return redirect(url_for('{model_var}s.index'))
    
    def show(self, id):
        """Display the specified resource"""
        # {model_var} = {model_class}.find_or_fail(id)
        return render_template('{model_var}s/show.html', id=id)
    
    def edit(self, id):
        """Show the form for editing the specified resource"""
        # {model_var} = {model_class}.find_or_fail(id)
        return render_template('{model_var}s/edit.html', id=id)
    
    def update(self, id):
        """Update the specified resource in storage"""
        # Validate request
        data = self.validate_request({{
            'name': 'required|string|max:255',
            # Add your validation rules here
        }})
        
        # Update {model_var}
        # {model_var} = {model_class}.find_or_fail(id)
        # {model_var}.update(data)
        
        # Redirect with success message
        return redirect(url_for('{model_var}s.show', id=id))
    
    def destroy(self, id):
        """Remove the specified resource from storage"""
        # {model_var} = {model_class}.find_or_fail(id)
        # {model_var}.delete()
        
        # Redirect with success message
        return redirect(url_for('{model_var}s.index'))'''

    def _get_api_resource_methods(self, model_name: Optional[str] = None) -> str:
        """Get API resource controller methods"""
        model_var = model_name.lower() if model_name else 'item'
        model_class = model_name if model_name else 'Model'
        
        return f'''    def index(self):
        """Display a listing of the resource"""
        # {model_var}s = {model_class}.all()
        return {{
            'data': [],  # Replace with actual {model_var}s data
            'status': 'success',
            'message': '{model_class} list retrieved successfully'
        }}
    
    def store(self):
        """Store a newly created resource in storage"""
        # Validate request
        data = self.validate_request({{
            'name': 'required|string|max:255',
            # Add your validation rules here
        }})
        
        # Create new {model_var}
        # {model_var} = {model_class}.create(data)
        
        return {{
            'data': data,  # Replace with actual {model_var} data
            'status': 'success',
            'message': '{model_class} created successfully'
        }}, 201
    
    def show(self, id):
        """Display the specified resource"""
        # {model_var} = {model_class}.find_or_fail(id)
        return {{
            'data': {{'id': id}},  # Replace with actual {model_var} data
            'status': 'success',
            'message': f'{model_class} {{id}} retrieved successfully'
        }}
    
    def update(self, id):
        """Update the specified resource in storage"""
        # Validate request
        data = self.validate_request({{
            'name': 'required|string|max:255',
            # Add your validation rules here
        }})
        
        # Update {model_var}
        # {model_var} = {model_class}.find_or_fail(id)
        # {model_var}.update(data)
        
        return {{
            'data': data,  # Replace with actual {model_var} data
            'status': 'success',
            'message': f'{model_class} {{id}} updated successfully'
        }}
    
    def destroy(self, id):
        """Remove the specified resource from storage"""
        # {model_var} = {model_class}.find_or_fail(id)
        # {model_var}.delete()
        
        return {{
            'status': 'success',
            'message': f'{model_class} {{id}} deleted successfully'
        }}, 204'''