"""Migration status command"""

import os
from typing import List, Dict, Any
from ...console.command import Command
from ..migrations.repository import MigrationRepository


class MigrateStatusCommand(Command):
    """Show the repository status for each migration"""
    
    name = "migrate:status"
    description = "Show the status of each migration"

    def __init__(self, repository: MigrationRepository):
        super().__init__()
        self.repository = repository

    def handle(self):
        """Execute the command"""
        if not self.repository.repository_exists():
            self.error("Migration table not found.")
            self.line("")
            self.info("Run 'migrate:install' to create the migration table.")
            return

        # Get all migrations from files
        migration_files = self._get_migration_files()
        
        # Get ran migrations from database
        ran_migrations = self.repository.get_ran()
        
        if not migration_files and not ran_migrations:
            self.info("No migrations found.")
            return

        self.line("")
        self.info("Migration Status:")
        self.line("")

        # Show status for each migration
        for migration_file in migration_files:
            migration_name = self._get_migration_name(migration_file)
            status = "✓ Ran" if migration_name in ran_migrations else "✗ Pending"
            
            if migration_name in ran_migrations:
                batch = self.repository.get_migration_batch(migration_name)
                self.line(f"  {status:<10} {migration_name} (Batch {batch})")
            else:
                self.line(f"  {status:<10} {migration_name}")

        # Show migrations in database but not in files
        orphaned = set(ran_migrations) - {self._get_migration_name(f) for f in migration_files}
        if orphaned:
            self.line("")
            self.comment("Orphaned migrations (in database but not in files):")
            for migration in orphaned:
                batch = self.repository.get_migration_batch(migration)
                self.line(f"  Missing    {migration} (Batch {batch})")

        self.line("")

    def _get_migration_files(self) -> List[str]:
        """Get all migration files"""
        migrations_path = "database/migrations"
        if not os.path.exists(migrations_path):
            return []
        
        files = []
        for file in os.listdir(migrations_path):
            if file.endswith('.py') and not file.startswith('__'):
                files.append(file)
        
        return sorted(files)

    def _get_migration_name(self, filename: str) -> str:
        """Get migration name from filename"""
        # Remove .py extension
        return filename[:-3] if filename.endswith('.py') else filename