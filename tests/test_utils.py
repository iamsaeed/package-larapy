"""
Test utility functions.
"""

import unittest
from larapy.utils import helpers


class TestHelpers(unittest.TestCase):
    """Test cases for helper functions."""
    
    def test_case_conversions(self):
        """Test string case conversion functions."""
        test_string = "hello_world-test"
        
        self.assertEqual(helpers.snake_case("HelloWorldTest"), "hello_world_test")
        self.assertEqual(helpers.camel_case(test_string), "helloWorldTest")
        self.assertEqual(helpers.pascal_case(test_string), "HelloWorldTest")
        self.assertEqual(helpers.kebab_case("HelloWorldTest"), "hello-world-test")
    
    def test_deep_get_set(self):
        """Test deep dictionary operations."""
        data = {}
        
        helpers.deep_set(data, 'app.database.host', 'localhost')
        helpers.deep_set(data, 'app.database.port', 5432)
        
        self.assertEqual(helpers.deep_get(data, 'app.database.host'), 'localhost')
        self.assertEqual(helpers.deep_get(data, 'app.database.port'), 5432)
        self.assertIsNone(helpers.deep_get(data, 'nonexistent.key'))
        self.assertEqual(helpers.deep_get(data, 'nonexistent.key', 'default'), 'default')
    
    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested = {
            'app': {
                'name': 'Test App',
                'database': {
                    'host': 'localhost',
                    'port': 5432
                }
            }
        }
        
        flattened = helpers.flatten_dict(nested)
        expected = {
            'app.name': 'Test App',
            'app.database.host': 'localhost',
            'app.database.port': 5432
        }
        
        self.assertEqual(flattened, expected)
    
    def test_chunk_list(self):
        """Test list chunking."""
        test_list = list(range(10))
        chunks = helpers.chunk_list(test_list, 3)
        
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        self.assertEqual(chunks, expected)
    
    def test_is_empty(self):
        """Test empty value checking."""
        self.assertTrue(helpers.is_empty(None))
        self.assertTrue(helpers.is_empty(''))
        self.assertTrue(helpers.is_empty([]))
        self.assertTrue(helpers.is_empty({}))
        self.assertTrue(helpers.is_empty(()))
        
        self.assertFalse(helpers.is_empty('test'))
        self.assertFalse(helpers.is_empty([1]))
        self.assertFalse(helpers.is_empty({'key': 'value'}))
        self.assertFalse(helpers.is_empty(0))
        self.assertFalse(helpers.is_empty(False))


if __name__ == '__main__':
    unittest.main()
