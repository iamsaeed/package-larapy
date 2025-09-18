"""Seed command for running database seeders"""

from ...console.command import Command
from ..seeder.manager import get_seeder_manager
from ..seeder.seeder import DatabaseSeeder


class SeedCommand(Command):
    """
    Seed the database with records
    """

    def __init__(self):
        super().__init__()
        self.name = "db:seed"
        self.description = "Seed the database with records"

    def handle(self, *args, **options):
        """Execute the command"""
        seeder_class = options.get('class', DatabaseSeeder)
        force = options.get('force', False)
        
        # Check if we're in production
        if not force and self._is_production():
            self.error("Application is in production. Use --force to run seeders in production.")
            return False

        try:
            self.info("Seeding database...")
            
            manager = get_seeder_manager()
            manager.run(seeder_class)
            
            self.info("Database seeding completed successfully.")
            return True
            
        except Exception as e:
            self.error(f"Database seeding failed: {str(e)}")
            return False

    def _is_production(self) -> bool:
        """Check if the application is in production environment"""
        import os
        return os.getenv('APP_ENV', 'development') == 'production'

    def get_arguments(self):
        """Get the command arguments"""
        return [
            ('class', 'The class name of the root seeder', None, False)
        ]

    def get_options(self):
        """Get the command options"""
        return [
            ('force', 'Force the operation to run when in production', False, False)
        ]