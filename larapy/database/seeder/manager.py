"""Seeder Manager for running database seeders"""

from typing import List, Type, Dict, Any, Optional
import os
import importlib
from .seeder import Seeder, DatabaseSeeder


class SeederManager:
    """
    Manager for running database seeders
    """

    def __init__(self):
        """Initialize the seeder manager"""
        self.seeders_path = "database/seeders"
        self.output = True

    def run(self, seeder_class: Type[Seeder] = None, **options):
        """Run database seeders"""
        if seeder_class is None:
            seeder_class = DatabaseSeeder

        seeder = seeder_class()
        
        if self.output:
            print(f"Seeding: {seeder_class.__name__}")
        
        try:
            seeder.run()
            
            if self.output:
                print("Database seeding completed successfully.")
                
        except Exception as e:
            if self.output:
                print(f"Database seeding failed: {str(e)}")
            raise

    def call(self, seeder_classes: List[Type[Seeder]]):
        """Call multiple seeders"""
        for seeder_class in seeder_classes:
            self.run(seeder_class)

    def get_seeder_class(self, name: str) -> Optional[Type[Seeder]]:
        """Get a seeder class by name"""
        try:
            # Try to import from the seeders module
            module_name = f"{self.seeders_path.replace('/', '.')}.{name.lower()}"
            module = importlib.import_module(module_name)
            
            # Look for the seeder class
            seeder_class = getattr(module, name, None)
            
            if seeder_class and issubclass(seeder_class, Seeder):
                return seeder_class
                
        except ImportError:
            pass

        return None

    def discover_seeders(self) -> List[Type[Seeder]]:
        """Discover all available seeders"""
        seeders = []
        
        # This would scan the seeders directory for seeder classes
        # For now, return an empty list
        return seeders

    def set_output(self, output: bool):
        """Set whether to output seeding information"""
        self.output = output

    def set_seeders_path(self, path: str):
        """Set the path where seeders are located"""
        self.seeders_path = path


# Global seeder manager instance
_seeder_manager = SeederManager()


def seed(seeder_class: Type[Seeder] = None, **options):
    """Run database seeders"""
    return _seeder_manager.run(seeder_class, **options)


def call_seeders(seeder_classes: List[Type[Seeder]]):
    """Call multiple seeders"""
    return _seeder_manager.call(seeder_classes)


def get_seeder_manager() -> SeederManager:
    """Get the global seeder manager"""
    return _seeder_manager