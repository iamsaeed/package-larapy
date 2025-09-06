import pytest
import tempfile
import os
from larapy import Application, Container


class TestContainer:
    """Test the Service Container"""
    
    def test_basic_binding_and_resolution(self):
        container = Container()
        
        # Test basic binding
        container.bind('test_service', lambda c: "Hello World")
        result = container.resolve('test_service')
        
        assert result == "Hello World"
    
    def test_singleton_binding(self):
        container = Container()
        
        class TestService:
            def __init__(self):
                self.value = "singleton"
        
        container.singleton('test_singleton', TestService)
        
        # Resolve twice and check they're the same instance
        instance1 = container.resolve('test_singleton')
        instance2 = container.resolve('test_singleton')
        
        assert instance1 is instance2
        assert instance1.value == "singleton"
    
    def test_instance_binding(self):
        container = Container()
        
        test_instance = {"key": "value"}
        container.instance('test_instance', test_instance)
        
        resolved = container.resolve('test_instance')
        assert resolved is test_instance
    
    def test_array_access(self):
        container = Container()
        
        # Test array-style access
        container['test'] = "test_value"
        assert container['test'] == "test_value"
    
    def test_aliases(self):
        container = Container()
        
        container.bind('original', lambda c: "original_value")
        container.alias('original', 'alias')
        
        assert container.resolve('alias') == "original_value"


class TestApplication:
    """Test the Application class"""
    
    def test_application_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(tmpdir)
            
            assert app.base_path() == tmpdir
            assert app.flask_app is not None
            assert isinstance(app, Container)
    
    def test_path_methods(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(tmpdir)
            
            assert app.config_path() == os.path.join(tmpdir, 'config')
            assert app.public_path() == os.path.join(tmpdir, 'public')
            assert app.storage_path() == os.path.join(tmpdir, 'storage')
            assert app.database_path() == os.path.join(tmpdir, 'database')
    
    def test_environment_detection(self):
        app = Application()
        
        # Test default environment
        assert app.environment() in ['production', 'local']
        
        # Test with environment variable
        os.environ['APP_ENV'] = 'testing'
        assert app.environment() == 'testing'
        
        # Clean up
        if 'APP_ENV' in os.environ:
            del os.environ['APP_ENV']
    
    def test_service_provider_registration(self):
        app = Application()
        
        class TestProvider:
            def __init__(self, app):
                self.app = app
                self.registered = False
            
            def register(self):
                self.registered = True
                self.app.bind('test_provider_service', lambda c: 'provider_service')
        
        provider = TestProvider(app)
        app.register(provider)
        
        assert provider.registered
        assert app.resolve('test_provider_service') == 'provider_service'


class TestConfig:
    """Test the Configuration system"""
    
    def test_env_function(self):
        from larapy.config.repository import env
        
        # Test with existing environment variable
        os.environ['TEST_VAR'] = 'test_value'
        assert env('TEST_VAR') == 'test_value'
        
        # Test with default value
        assert env('NON_EXISTENT_VAR', 'default') == 'default'
        
        # Test type casting
        os.environ['BOOL_VAR'] = 'true'
        assert env('BOOL_VAR', cast_type=bool) is True
        
        os.environ['INT_VAR'] = '42'
        assert env('INT_VAR', cast_type=int) == 42
        
        # Clean up
        for var in ['TEST_VAR', 'BOOL_VAR', 'INT_VAR']:
            if var in os.environ:
                del os.environ[var]
    
    def test_repository_get_set(self):
        from larapy.config.repository import Repository
        
        repo = Repository('/nonexistent/path')  # Won't load files
        
        # Test basic get/set
        repo.set('test.key', 'test_value')
        assert repo.get('test.key') == 'test_value'
        
        # Test default value
        assert repo.get('nonexistent.key', 'default') == 'default'
        
        # Test nested configuration
        repo.set('app.debug', True)
        repo.set('app.name', 'Test App')
        
        assert repo.get('app.debug') is True
        assert repo.get('app.name') == 'Test App'


class TestORM:
    """Test the ORM functionality"""
    
    def test_model_creation(self):
        from larapy.database.orm import Model, DatabaseConnection
        
        # Create test model
        class TestUser(Model):
            table = 'test_users'
            fillable = ['name', 'email']
        
        # Test table name inference
        assert TestUser.table == 'test_users'
        assert TestUser.fillable == ['name', 'email']
    
    def test_query_builder(self):
        from larapy.database.orm import QueryBuilder, DatabaseConnection
        
        # Create in-memory database
        connection = DatabaseConnection({'driver': 'sqlite', 'database': ':memory:'})
        
        # Create test table
        connection.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        
        # Insert test data
        connection.execute(
            "INSERT INTO test_table (name, email) VALUES (?, ?)",
            ('John Doe', 'john@example.com')
        )
        connection.commit()
        
        # Test query builder
        builder = QueryBuilder(connection, 'test_table')
        
        # Test select
        results = builder.select('name', 'email').get()
        assert len(results) == 1
        assert results[0]['name'] == 'John Doe'
        
        # Test where clause
        result = builder.where('name', 'John Doe').first()
        assert result is not None
        assert result['email'] == 'john@example.com'
        
        # Test count
        count = builder.count()
        assert count == 1
    
    def test_schema_builder(self):
        from larapy.database.orm import Schema, DatabaseConnection
        
        # Create in-memory database
        connection = DatabaseConnection({'driver': 'sqlite', 'database': ':memory:'})
        schema = Schema(connection)
        
        # Test table creation
        def create_users_table(table):
            table.id()
            table.string('name')
            table.string('email')
            table.timestamps()
        
        schema.create_table('users', create_users_table)
        
        # Test if table exists
        assert schema.has_table('users')
        
        # Test table structure by inserting data
        connection.execute(
            "INSERT INTO users (name, email, created_at, updated_at) VALUES (?, ?, ?, ?)",
            ('Test User', 'test@example.com', '2023-01-01 00:00:00', '2023-01-01 00:00:00')
        )
        connection.commit()
        
        result = connection.fetch_one("SELECT * FROM users WHERE name = ?", ('Test User',))
        assert result is not None
        assert result['name'] == 'Test User'


class TestRouting:
    """Test the Routing system"""
    
    def test_route_registration(self):
        from larapy.routing.router import Router
        from larapy import Application
        
        app = Application()
        router = Router(app)
        
        # Test basic route registration
        router.get('/test', lambda: 'test response')
        
        # Check if route was registered with Flask
        rules = [rule.rule for rule in app.flask_app.url_map.iter_rules()]
        assert '/test' in rules
    
    def test_route_parameter_conversion(self):
        from larapy.routing.router import Router
        from larapy import Application
        
        app = Application()
        router = Router(app)
        
        # Test Laravel-style parameter to Flask conversion
        assert router._convert_uri('/users/{id}') == '/users/<id>'
        assert router._convert_uri('/posts/{id}/comments/{comment_id}') == '/posts/<id>/comments/<comment_id>'


class TestHTTP:
    """Test HTTP Request and Response handling"""
    
    def test_response_creation(self):
        from larapy.http.response import Response
        
        # Test JSON response
        json_response = Response.json({'message': 'test'})
        assert json_response.status_code == 200
        
        # Test JSON response with custom status
        error_response = Response.json({'error': 'not found'}, 404)
        assert error_response.status_code == 404
        
        # Test make response
        text_response = Response.make('Hello World', 200)
        assert text_response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
