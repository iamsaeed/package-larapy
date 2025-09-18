"""Base Migration class for database schema changes"""

from abc import ABC, abstractmethod


class Migration(ABC):
    """
    Base migration class

    Similar to Laravel's Migration class, provides the structure
    for database schema changes with up/down methods.
    """

    # The database connection name
    connection: str = None

    # Whether to wrap migration in transaction
    within_transaction: bool = True

    def __init__(self):
        self.schema = None

    def get_connection(self) -> str:
        """Get the migration connection name"""
        return self.connection

    @abstractmethod
    def up(self):
        """Run the migrations"""
        pass

    @abstractmethod
    def down(self):
        """Reverse the migrations"""
        pass

    def should_run(self) -> bool:
        """Determine if this migration should run"""
        return True