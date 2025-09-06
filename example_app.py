"""
Example Larapy Application

This demonstrates how to use the Larapy framework with all its features:
- Service Container & Dependency Injection
- Routing with middleware
- ORM with models
- Configuration management
- Service providers
"""

from larapy import Application, Route, Facade, Model, DatabaseManager, Schema
from larapy.http.response import Response
from larapy.http.request import Request
from larapy.database.orm import DatabaseConnection


# Example Model
class User(Model):
    table = 'users'
    fillable = ['name', 'email', 'password']
    
    @classmethod
    def find_by_email(cls, email: str):
        return cls.where('email', email).first()


class Post(Model):
    table = 'posts'
    fillable = ['title', 'content', 'user_id']


# Example Controller
class UserController:
    
    def index(self):
        """Get all users"""
        users = User.all()
        return Response.json([user.to_dict() for user in users])
    
    def show(self, id: int):
        """Get a specific user"""
        user = User.find(id)
        if not user:
            return Response.json({'error': 'User not found'}, 404)
        return Response.json(user.to_dict())
    
    def store(self, request: Request):
        """Create a new user"""
        data = request.only(['name', 'email', 'password'])
        
        # Simple validation
        if not all([data.get('name'), data.get('email'), data.get('password')]):
            return Response.json({'error': 'Missing required fields'}, 400)
        
        # Check if email already exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return Response.json({'error': 'Email already exists'}, 409)
        
        user = User.create(**data)
        return Response.json(user.to_dict(), 201)
    
    def update(self, id: int, request: Request):
        """Update a user"""
        user = User.find(id)
        if not user:
            return Response.json({'error': 'User not found'}, 404)
        
        data = request.only(['name', 'email'])
        for key, value in data.items():
            if value:  # Only update non-empty values
                setattr(user, key, value)
        
        if user.save():
            return Response.json(user.to_dict())
        return Response.json({'error': 'Failed to update user'}, 500)
    
    def destroy(self, id: int):
        """Delete a user"""
        user = User.find(id)
        if not user:
            return Response.json({'error': 'User not found'}, 404)
        
        if user.delete():
            return Response.json({'message': 'User deleted successfully'})
        return Response.json({'error': 'Failed to delete user'}, 500)


# Custom Service Provider
class AppServiceProvider:
    def __init__(self, app):
        self.app = app
    
    def register(self):
        """Register application services"""
        # Bind the UserController to the container
        self.app.bind('UserController', lambda app: UserController())
        
        # Set up database
        self._setup_database()
    
    def boot(self):
        """Bootstrap application services"""
        # Set up routes
        self._register_routes()
    
    def _setup_database(self):
        """Set up database connection and models"""
        # Create database manager
        db_manager = DatabaseManager()
        
        # Add default connection
        db_config = {
            'driver': 'sqlite',
            'database': self.app.base_path('storage/app.sqlite3')
        }
        db_manager.add_connection('default', db_config)
        
        # Bind to container
        self.app.singleton('db', lambda app: db_manager)
        
        # Set connection for models
        connection = db_manager.connection('default')
        User.set_connection(connection)
        Post.set_connection(connection)
        
        # Create tables if they don't exist
        self._create_tables(connection)
    
    def _create_tables(self, connection: DatabaseConnection):
        """Create database tables"""
        schema = Schema(connection)
        
        # Create users table
        if not schema.has_table('users'):
            def create_users_table(table):
                table.id()
                table.string('name')
                table.string('email').nullable()
                table.string('password')
                table.timestamps()
            
            schema.create_table('users', create_users_table)
        
        # Create posts table
        if not schema.has_table('posts'):
            def create_posts_table(table):
                table.id()
                table.string('title')
                table.text('content')
                table.integer('user_id')
                table.timestamps()
            
            schema.create_table('posts', create_posts_table)
    
    def _register_routes(self):
        """Register application routes"""
        router = self.app.resolve('router')
        
        # API routes
        router.get('/api/users', 'UserController@index')
        router.get('/api/users/{id}', 'UserController@show')
        router.post('/api/users', 'UserController@store')
        router.put('/api/users/{id}', 'UserController@update')
        router.delete('/api/users/{id}', 'UserController@destroy')
        
        # Simple lambda routes
        router.get('/', lambda: Response.json({
            'message': 'Welcome to Larapy!',
            'version': '1.0.0',
            'framework': 'Laravel concepts in Python Flask'
        }))
        
        router.get('/health', lambda: Response.json({'status': 'ok'}))


# Create and configure the application
def create_app():
    """Application factory"""
    app = Application()
    
    # Set up facades
    Facade.set_facade_application(app)
    
    # Register custom service provider
    app.register(AppServiceProvider(app))
    
    # Add some sample data
    @app.flask_app.before_first_request
    def create_sample_data():
        # Check if we already have users
        if User.count() == 0:
            # Create sample users
            User.create(name='John Doe', email='john@example.com', password='password123')
            User.create(name='Jane Smith', email='jane@example.com', password='password456')
            
            # Create sample posts
            Post.create(title='First Post', content='This is the first post content', user_id=1)
            Post.create(title='Second Post', content='This is the second post content', user_id=2)
    
    return app


if __name__ == '__main__':
    # Create the application
    app = create_app()
    
    # Run the application
    print("Starting Larapy application...")
    print("Available endpoints:")
    print("GET  /                 - Welcome message")
    print("GET  /health           - Health check")
    print("GET  /api/users        - List all users")
    print("GET  /api/users/{id}   - Get specific user")
    print("POST /api/users        - Create new user")
    print("PUT  /api/users/{id}   - Update user")
    print("DELETE /api/users/{id} - Delete user")
    print("\nStarting server on http://127.0.0.1:5000")
    
    app.run(debug=True)
