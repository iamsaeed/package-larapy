# Larapy Framework

Laravel concepts implemented in Python Flask - A powerful web framework that brings Laravel's elegant architecture to Python.

## Features

🚀 **Laravel-Inspired Architecture**
- Service Container with Dependency Injection
- Application Lifecycle Management  
- Service Providers for bootstrapping
- Facades for static-like access to services

🔗 **Advanced Routing**
- Laravel-style route registration
- Route middleware support
- Route groups and prefixes
- Automatic parameter binding

💾 **Built-in ORM**
- Eloquent-like model system
- Query Builder with fluent interface
- Database migrations and schema builder
- Multiple database support

🌐 **HTTP Handling**
- Request/Response wrappers
- Middleware pipeline
- JSON API support

⚙️ **Configuration Management**
- Environment-based configuration
- Dot notation access
- Auto-loading config files

## Installation

```bash
pip install larapy
```

## Quick Start

### 1. Basic Application

```python
from larapy import Application, Response

# Create application
app = Application()

# Define routes using the router
router = app.resolve('router')

router.get('/', lambda: Response.json({
    'message': 'Welcome to Larapy!',
    'framework': 'Laravel concepts in Python'
}))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
```

### 2. Using Models and ORM

```python
from larapy import Model, DatabaseManager, Schema

# Define a model
class User(Model):
    table = 'users'
    fillable = ['name', 'email', 'password']

# Set up database
db_manager = DatabaseManager()
db_manager.add_connection('default', {
    'driver': 'sqlite',
    'database': 'app.db'
})

# Set model connection
User.set_connection(db_manager.connection())

# Create table schema
schema = Schema(db_manager.connection())

def create_users_table(table):
    table.id()
    table.string('name')
    table.string('email')
    table.string('password')
    table.timestamps()

schema.create_table('users', create_users_table)

# Use the model
user = User.create(name='John Doe', email='john@example.com', password='secret')
users = User.all()
user = User.find(1)
```

### 3. Controllers and Dependency Injection

```python
from larapy.http.request import Request
from larapy.http.response import Response

class UserController:
    def index(self):
        users = User.all()
        return Response.json([user.to_dict() for user in users])
    
    def store(self, request: Request):
        data = request.only(['name', 'email', 'password'])
        user = User.create(**data)
        return Response.json(user.to_dict(), 201)
    
    def show(self, id: int):
        user = User.find(id)
        if not user:
            return Response.json({'error': 'Not found'}, 404)
        return Response.json(user.to_dict())

# Register controller routes
router.get('/users', 'UserController@index')
router.post('/users', 'UserController@store')
router.get('/users/{id}', 'UserController@show')
```

## Architecture

Larapy follows Laravel's architectural patterns with Service Container, Facades, ORM, and more.

See `example_app.py` for a complete working example.

## Requirements

- Python 3.8+
- Flask 2.0+
- python-dotenv

## License

MIT License
