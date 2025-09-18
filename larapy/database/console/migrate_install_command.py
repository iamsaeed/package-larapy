"""Migration install command"""

from typing import List, Dict, Any
from ...console.command import Command
from ..migrations.repository import MigrationRepository


class MigrateInstallCommand(Command):
    """Create the migration repository"""
    
    name = "migrate:install"
    description = "Create the migration repository"

    def __init__(self, repository: MigrationRepository):
        super().__init__()
        self.repository = repository

    def handle(self):
        """Execute the command"""
        if self.repository.repository_exists():
            self.info("Migration table already exists.")
            return

        self.repository.create_repository()
        self.info("Migration table created successfully.")