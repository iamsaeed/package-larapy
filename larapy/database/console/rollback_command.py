"""Rollback migration console command"""

import os
from typing import List
from larapy.console.command import Command
from ..migrations.migrator import Migrator
from ..migrations.repository import MigrationRepository


class RollbackCommand(Command):
    """
    Rollback database migrations
    """

    signature = "migrate:rollback {--step=1 : Number of batches to rollback}"
    description = "Rollback database migrations"

    def handle(self) -> int:
        """Execute the rollback command"""
        
        # Get database manager from app
        db_manager = self.app.resolve('database') if hasattr(self.app, 'resolve') else None
        
        if not db_manager:
            self.error("Database manager not available")
            return 1
        
        # Create migration repository
        repository = MigrationRepository(db_manager, 'migrations')
        
        # Create migrator
        migrator = Migrator(repository, db_manager)
        
        # Set migration paths
        migration_paths = self._get_migration_paths()
        migrator.set_paths(migration_paths)
        
        try:
            self.info("Rolling back migrations...")
            
            notes = migrator.rollback()
            
            for note in notes:
                self.line(note)
                
            return 0
            
        except Exception as e:
            self.error(f"Rollback failed: {str(e)}")
            return 1

    def _get_migration_paths(self) -> List[str]:
        """Get migration paths from configuration"""
        # Default migration path
        if hasattr(self.app, 'base_path'):
            base_path = self.app.base_path('database/migrations')
        else:
            base_path = os.path.join(os.getcwd(), 'database', 'migrations')
        
        # Check if path exists, create if not
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
            
        return [base_path]