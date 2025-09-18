"""Database Seeder base class"""

from abc import ABC, abstractmethod
from typing import List, Type, Any


class Seeder(ABC):
    """
    Base class for database seeders
    """

    def __init__(self):
        """Initialize the seeder"""
        self.called_seeders = []

    @abstractmethod
    def run(self):
        """Run the seeder"""
        pass

    def call(self, seeder_classes: List[Type['Seeder']]):
        """Call other seeders"""
        for seeder_class in seeder_classes:
            if isinstance(seeder_class, type):
                seeder = seeder_class()
            else:
                seeder = seeder_class

            print(f"Seeding: {seeder.__class__.__name__}")
            seeder.run()
            self.called_seeders.append(seeder.__class__.__name__)

    def call_silent(self, seeder_classes: List[Type['Seeder']]):
        """Call other seeders without output"""
        for seeder_class in seeder_classes:
            if isinstance(seeder_class, type):
                seeder = seeder_class()
            else:
                seeder = seeder_class

            seeder.run()
            self.called_seeders.append(seeder.__class__.__name__)

    def factory(self, model: Type, count: int = 1):
        """Get a factory for creating test data"""
        from ..factory.manager import factory
        return factory(model, count)

    def create(self, model: Type, count: int = 1, attributes: dict = None):
        """Create model instances using factories"""
        from ..factory.manager import create
        return create(model, count, attributes)

    def make(self, model: Type, count: int = 1, attributes: dict = None):
        """Make model instances using factories"""
        from ..factory.manager import make
        return make(model, count, attributes)

    def command(self, command: str, parameters: List[str] = None):
        """Execute an artisan command"""
        # This would integrate with the console command system
        print(f"Executing command: {command} {' '.join(parameters or [])}")

    def truncate(self, *tables):
        """Truncate database tables"""
        from ..manager import DatabaseManager
        
        manager = DatabaseManager.get_instance()
        connection = manager.connection()
        
        for table in tables:
            print(f"Truncating table: {table}")
            connection.statement(f"DELETE FROM {table}")
            connection.statement(f"DELETE FROM sqlite_sequence WHERE name='{table}'")

    def disable_foreign_key_checks(self):
        """Disable foreign key checks"""
        from ..manager import DatabaseManager
        
        manager = DatabaseManager.get_instance()
        connection = manager.connection()
        connection.statement("PRAGMA foreign_keys = OFF")

    def enable_foreign_key_checks(self):
        """Enable foreign key checks"""
        from ..manager import DatabaseManager
        
        manager = DatabaseManager.get_instance()
        connection = manager.connection()
        connection.statement("PRAGMA foreign_keys = ON")

    def with_foreign_key_checks_disabled(self, callback):
        """Run a callback with foreign key checks disabled"""
        self.disable_foreign_key_checks()
        try:
            callback()
        finally:
            self.enable_foreign_key_checks()


class DatabaseSeeder(Seeder):
    """
    Main database seeder that calls other seeders
    """

    def run(self):
        """Run the database seeder"""
        # This is the main seeder that would call other seeders
        # Example:
        # self.call([
        #     UserSeeder,
        #     PostSeeder,
        #     CommentSeeder,
        # ])
        pass