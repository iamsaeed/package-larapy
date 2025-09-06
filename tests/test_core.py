"""
Test the main LarapyApp functionality.
"""

import unittest
from larapy import LarapyApp, Config


class TestLarapyApp(unittest.TestCase):
    """Test cases for LarapyApp class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = LarapyApp()
    
    def test_app_initialization(self):
        """Test app initialization."""
        self.assertFalse(self.app.is_initialized)
        self.app.initialize()
        self.assertTrue(self.app.is_initialized)
    
    def test_configuration(self):
        """Test configuration management."""
        config = {'app': {'name': 'Test App', 'debug': True}}
        self.app.configure(config)
        
        self.assertEqual(self.app.get_config('app.name'), 'Test App')
        self.assertTrue(self.app.get_config('app.debug'))
        self.assertIsNone(self.app.get_config('nonexistent.key'))
    
    def test_service_registration(self):
        """Test service registration and retrieval."""
        class TestService:
            def __init__(self):
                self.data = 'test_data'
        
        service = TestService()
        self.app.register_service('test_service', service)
        
        retrieved_service = self.app.get_service('test_service')
        self.assertEqual(retrieved_service.data, 'test_data')
        
        with self.assertRaises(KeyError):
            self.app.get_service('nonexistent_service')


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        config = Config()
        
        config.set('app.name', 'Test App')
        config.set('app.debug', True)
        
        self.assertEqual(config.get('app.name'), 'Test App')
        self.assertTrue(config.get('app.debug'))
        self.assertIsNone(config.get('nonexistent.key'))
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
    
    def test_config_update(self):
        """Test configuration updates."""
        config = Config({'existing': 'value'})
        
        config.update({
            'new': 'value',
            'nested': {'key': 'value'}
        })
        
        self.assertEqual(config.get('existing'), 'value')
        self.assertEqual(config.get('new'), 'value')
        self.assertEqual(config.get('nested.key'), 'value')
    
    def test_config_dict_access(self):
        """Test dictionary-style access."""
        config = Config()
        
        config['app.name'] = 'Test App'
        self.assertEqual(config['app.name'], 'Test App')
        self.assertTrue('app.name' in config)
        self.assertFalse('nonexistent' in config)


if __name__ == '__main__':
    unittest.main()
