"""Has Timestamps concern for Eloquent models"""

from datetime import datetime
from typing import Optional


class HasTimestamps:
    """
    Provides timestamp management functionality for Eloquent models
    """

    # Whether the model should have timestamps
    timestamps = True

    # The name of the "created at" column
    created_at = 'created_at'

    # The name of the "updated at" column
    updated_at = 'updated_at'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def touch(self, attribute: str = None) -> bool:
        """Update the model's update timestamp"""
        if not self.uses_timestamps():
            return False

        self.update_timestamps()

        if attribute:
            self.set_attribute(attribute, self.fresh_timestamp())

        return self.save()

    def update_timestamps(self):
        """Set the creation and update timestamps"""
        time = self.fresh_timestamp()

        if not self.is_dirty(self.get_updated_at_column()) and not self.exists:
            self.set_updated_at(time)

        if not self.exists and not self.is_dirty(self.get_created_at_column()):
            self.set_created_at(time)

    def set_created_at(self, value):
        """Set the value of the "created at" attribute"""
        self.set_attribute(self.get_created_at_column(), value)

    def set_updated_at(self, value):
        """Set the value of the "updated at" attribute"""
        self.set_attribute(self.get_updated_at_column(), value)

    def fresh_timestamp(self) -> datetime:
        """Get a fresh timestamp for the model"""
        return datetime.now()

    def fresh_timestamp_string(self) -> str:
        """Get a fresh timestamp string for the model"""
        return self.from_datetime(self.fresh_timestamp())

    def uses_timestamps(self) -> bool:
        """Determine if the model uses timestamps"""
        return getattr(self, 'timestamps', True)

    def get_created_at_column(self) -> str:
        """Get the name of the "created at" column"""
        return getattr(self, 'created_at', 'created_at')

    def get_updated_at_column(self) -> str:
        """Get the name of the "updated at" column"""
        return getattr(self, 'updated_at', 'updated_at')

    def get_qualified_created_at_column(self) -> str:
        """Get the fully qualified "created at" column"""
        return f"{self.get_table()}.{self.get_created_at_column()}"

    def get_qualified_updated_at_column(self) -> str:
        """Get the fully qualified "updated at" column"""
        return f"{self.get_table()}.{self.get_updated_at_column()}"

    def get_created_at(self) -> Optional[datetime]:
        """Get the value of the "created at" attribute"""
        return self.get_attribute(self.get_created_at_column())

    def get_updated_at(self) -> Optional[datetime]:
        """Get the value of the "updated at" attribute"""
        return self.get_attribute(self.get_updated_at_column())

    def prepare_timestamps_for_save(self):
        """Prepare the model for saving by updating timestamps"""
        if self.uses_timestamps():
            self.update_timestamps()