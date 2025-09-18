"""Database migration console command"""

import os
from typing import List
from larapy.console.command import Command
from ..migrations.migrator import Migrator
from ..migrations.repository import MigrationRepository


class MigrateCommand(Command):
    """
    Run database migrations
    """

    signature = "migrate {--rollback : Rollback the last migration batch} {--reset : Rollback all migrations} {--fresh : Drop all tables and re-run migrations}"
    description = "Run database migrations"

    def handle(self) -> int:
        """Execute the migrate command"""
        
        # Get database manager from app
        db_manager = self.app.resolve('database')
        
        # Create migration repository
        repository = MigrationRepository(db_manager, 'migrations')
        
        # Create migrator
        migrator = Migrator(repository, db_manager)
        
        # Set migration paths
        migration_paths = self._get_migration_paths()
        migrator.set_paths(migration_paths)
        
        try:
            if self.option('rollback'):
                return self._rollback(migrator)
            elif self.option('reset'):
                return self._reset(migrator)
            elif self.option('fresh'):
                return self._fresh(migrator)
            else:
                return self._migrate(migrator)
        except Exception as e:
            self.error(f"Migration failed: {str(e)}")
            return 1

    def _migrate(self, migrator: Migrator) -> int:
        """Run pending migrations"""
        self.info("Running migrations...")
        
        notes = migrator.run()
        
        for note in notes:
            self.line(note)
            
        return 0

    def _rollback(self, migrator: Migrator) -> int:
        """Rollback the last migration batch"""
        self.info("Rolling back migrations...")
        
        notes = migrator.rollback()
        
        for note in notes:
            self.line(note)
            
        return 0

    def _reset(self, migrator: Migrator) -> int:
        """Rollback all migrations"""
        self.info("Resetting all migrations...")
        
        notes = migrator.reset()
        
        for note in notes:
            self.line(note)
            
        return 0

    def _fresh(self, migrator: Migrator) -> int:
        """Drop all tables and re-run migrations"""
        self.info("Dropping all tables and re-running migrations...")
        
        notes = migrator.fresh()
        
        for note in notes:
            self.line(note)
            
        return 0

    def _get_migration_paths(self) -> List[str]:
        """Get migration paths from configuration"""
        # Default migration path
        base_path = os.path.join(self.app.base_path, 'database', 'migrations')
        
        # Check if path exists, create if not
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
            
        return [base_path]