"""Migration refresh command"""

from typing import List, Dict, Any
from ...console.command import Command
from .migrate_reset_command import MigrateResetCommand
from .migrate_command import MigrateCommand


class MigrateRefreshCommand(Command):
    """Reset and re-run all migrations"""
    
    name = "migrate:refresh"
    description = "Reset and re-run all migrations"

    def __init__(self, reset_command: MigrateResetCommand, migrate_command: MigrateCommand):
        super().__init__()
        self.reset_command = reset_command
        self.migrate_command = migrate_command

    def handle(self):
        """Execute the command"""
        self.info("Refreshing migrations...")
        
        # First reset all migrations
        self.line("Resetting migrations...")
        self.reset_command.handle()
        
        self.line("")
        
        # Then run migrations again
        self.line("Running migrations...")
        self.migrate_command.handle()
        
        self.info("Migrations refreshed successfully.")