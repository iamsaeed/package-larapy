"""Make observer console command"""

import os
from typing import Optional
from ...console.command import Command


class MakeObserverCommand(Command):
    """Create a new model observer"""
    
    signature = "make:observer {name : The name of the observer class} {--model= : The model to observe}"
    description = "Create a new model observer"

    def handle(self) -> int:
        """Execute the make:observer command"""
        
        # Get observer name from arguments
        observer_name = self.argument('name')
        if not observer_name:
            observer_name = self.ask("What should the observer be named?")
        
        if not observer_name:
            self.error("Observer name is required.")
            return 1

        # Clean observer name
        observer_name = self._clean_observer_name(observer_name)

        # Get model name
        model_name = self.option('model')
        if not model_name and observer_name.endswith('Observer'):
            # Try to infer model name from observer name
            model_name = observer_name[:-8]  # Remove 'Observer' suffix
        
        if not model_name:
            model_name = self.ask("What model should this observer observe?")

        if model_name:
            model_name = self._clean_model_name(model_name)

        try:
            # Create the observer file
            self._create_observer_file(observer_name, model_name)
            return 0
            
        except Exception as e:
            self.error(f"Failed to create observer: {str(e)}")
            return 1

    def _clean_observer_name(self, name: str) -> str:
        """Clean and format observer name"""
        # Add Observer suffix if not present
        if not name.endswith('Observer'):
            name = name + 'Observer'
        
        # Split CamelCase and capitalize each word properly
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name[:-8] if name.endswith('Observer') else name)
        cleaned_name = ''.join(word.capitalize() for word in words)
        
        return cleaned_name + 'Observer'

    def _clean_model_name(self, name: str) -> str:
        """Clean and format model name"""
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
        return ''.join(word.capitalize() for word in words)

    def _create_observer_file(self, observer_name: str, model_name: Optional[str]):
        """Create the observer file"""
        # Create observers directory if it doesn't exist
        observers_dir = "app/Observers"
        os.makedirs(observers_dir, exist_ok=True)

        # Create observer file path
        observer_file = os.path.join(observers_dir, f"{observer_name}.py")

        # Check if file already exists
        if os.path.exists(observer_file):
            self.error(f"Observer {observer_name} already exists.")
            return

        # Generate observer content
        content = self._get_observer_stub(observer_name, model_name)

        # Write observer file
        with open(observer_file, 'w') as f:
            f.write(content)

        self.success(f"Observer {observer_name} created successfully.")
        self.info(f"File: {observer_file}")
        if model_name:
            self.comment(f"Don't forget to register this observer for the {model_name} model")
            self.comment(f"Example: {model_name}.observe({observer_name}())")

    def _get_observer_stub(self, observer_name: str, model_name: Optional[str]) -> str:
        """Get the observer stub content"""
        observer_name_without_suffix = observer_name[:-8] if observer_name.endswith('Observer') else observer_name
        model_name = model_name or 'Model'
        
        return f'''"""
{observer_name}

Model observer for {model_name} model events.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'package-larapy'))

from larapy.database.eloquent.observer import Observer
from typing import Any, Optional


class {observer_name}(Observer):
    """
    {observer_name}
    
    Observes {model_name} model events and handles them accordingly.
    """
    
    def __init__(self):
        """Initialize the observer"""
        super().__init__()
    
    def creating(self, model: Any) -> Optional[bool]:
        """
        Handle the {model_name} "creating" event
        
        Args:
            model: The model instance being created
            
        Returns:
            False to halt the operation, True or None to continue
        """
        # Called before a model is created
        # You can modify model attributes here
        # Example: Set default values, validate data, etc.
        
        # Example: Set created_by field
        # if hasattr(model, 'created_by') and not model.created_by:
        #     model.created_by = self.get_current_user_id()
        
        # Example: Generate slug from title
        # if hasattr(model, 'title') and hasattr(model, 'slug') and not model.slug:
        #     model.slug = self.generate_slug(model.title)
        
        # Example: Validate business rules
        # if hasattr(model, 'price') and model.price < 0:
        #     raise ValueError("Price cannot be negative")
        
        return None  # Continue with creation
    
    def created(self, model: Any) -> None:
        """
        Handle the {model_name} "created" event
        
        Args:
            model: The model instance that was created
        """
        # Called after a model is created
        # Perfect for logging, sending notifications, cache invalidation, etc.
        
        # Example: Log the creation
        # self.log_event('created', model)
        
        # Example: Send notification
        # self.send_notification(f"{model_name} created: {{model.id}}")
        
        # Example: Clear cache
        # cache.forget(f"{model_name.lower()}_list")
        
        # Example: Create related records
        # if hasattr(model, 'user_id'):
        #     self.create_user_activity(model.user_id, 'created', model)
        
        pass
    
    def updating(self, model: Any) -> Optional[bool]:
        """
        Handle the {model_name} "updating" event
        
        Args:
            model: The model instance being updated
            
        Returns:
            False to halt the operation, True or None to continue
        """
        # Called before a model is updated
        # You can modify model attributes or prevent updates here
        
        # Example: Set updated_by field
        # if hasattr(model, 'updated_by'):
        #     model.updated_by = self.get_current_user_id()
        
        # Example: Update slug if title changed
        # if hasattr(model, 'title') and hasattr(model, 'slug') and model.is_dirty('title'):
        #     model.slug = self.generate_slug(model.title)
        
        # Example: Prevent updates under certain conditions
        # if hasattr(model, 'status') and model.status == 'locked':
        #     return False  # Prevent update
        
        return None  # Continue with update
    
    def updated(self, model: Any) -> None:
        """
        Handle the {model_name} "updated" event
        
        Args:
            model: The model instance that was updated
        """
        # Called after a model is updated
        
        # Example: Log the update with changed fields
        # changed_fields = model.get_dirty()
        # self.log_event('updated', model, changed_fields)
        
        # Example: Clear cache if important fields changed
        # if model.was_changed(['name', 'status']):
        #     cache.forget(f"{model_name.lower()}_{{model.id}}")
        
        # Example: Send notification for status changes
        # if model.was_changed('status'):
        #     self.send_status_change_notification(model)
        
        pass
    
    def saving(self, model: Any) -> Optional[bool]:
        """
        Handle the {model_name} "saving" event
        
        Args:
            model: The model instance being saved
            
        Returns:
            False to halt the operation, True or None to continue
        """
        # Called before a model is saved (created or updated)
        
        # Example: Validate common business rules
        # if hasattr(model, 'email') and model.email:
        #     if not self.is_valid_email(model.email):
        #         raise ValueError("Invalid email format")
        
        # Example: Sanitize input
        # if hasattr(model, 'content'):
        #     model.content = self.sanitize_html(model.content)
        
        return None  # Continue with save
    
    def saved(self, model: Any) -> None:
        """
        Handle the {model_name} "saved" event
        
        Args:
            model: The model instance that was saved
        """
        # Called after a model is saved (created or updated)
        
        # Example: Update search index
        # self.update_search_index(model)
        
        # Example: Sync with external service
        # self.sync_with_external_service(model)
        
        pass
    
    def deleting(self, model: Any) -> Optional[bool]:
        """
        Handle the {model_name} "deleting" event
        
        Args:
            model: The model instance being deleted
            
        Returns:
            False to halt the operation, True or None to continue
        """
        # Called before a model is deleted
        
        # Example: Prevent deletion under certain conditions
        # if hasattr(model, 'has_children') and model.has_children():
        #     return False  # Prevent deletion
        
        # Example: Soft delete instead of hard delete
        # if hasattr(model, 'deleted_at'):
        #     model.deleted_at = datetime.now()
        #     model.save()
        #     return False  # Prevent actual deletion
        
        return None  # Continue with deletion
    
    def deleted(self, model: Any) -> None:
        """
        Handle the {model_name} "deleted" event
        
        Args:
            model: The model instance that was deleted
        """
        # Called after a model is deleted
        
        # Example: Clean up related records
        # self.cleanup_related_records(model)
        
        # Example: Log the deletion
        # self.log_event('deleted', model)
        
        # Example: Clear cache
        # cache.forget(f"{model_name.lower()}_{{model.id}}")
        
        pass
    
    def restoring(self, model: Any) -> Optional[bool]:
        """
        Handle the {model_name} "restoring" event
        
        Args:
            model: The model instance being restored
            
        Returns:
            False to halt the operation, True or None to continue
        """
        # Called before a soft-deleted model is restored
        
        # Example: Validate that restoration is allowed
        # if hasattr(model, 'can_be_restored') and not model.can_be_restored():
        #     return False
        
        return None  # Continue with restoration
    
    def restored(self, model: Any) -> None:
        """
        Handle the {model_name} "restored" event
        
        Args:
            model: The model instance that was restored
        """
        # Called after a soft-deleted model is restored
        
        # Example: Log the restoration
        # self.log_event('restored', model)
        
        # Example: Restore related records
        # self.restore_related_records(model)
        
        pass
    
    # Helper methods
    def get_current_user_id(self) -> Optional[int]:
        """Get the current user ID"""
        # Implement your logic to get current user ID
        # Example: return request.user.id if request.user else None
        return None
    
    def generate_slug(self, text: str) -> str:
        """Generate a URL-friendly slug from text"""
        import re
        slug = re.sub(r'[^\\w\\s-]', '', text.lower())
        slug = re.sub(r'[-\\s]+', '-', slug)
        return slug.strip('-')
    
    def is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$'
        return re.match(pattern, email) is not None
    
    def sanitize_html(self, content: str) -> str:
        """Sanitize HTML content"""
        # Implement your HTML sanitization logic
        return content
    
    def log_event(self, event: str, model: Any, extra_data: dict = None) -> None:
        """Log model events"""
        # Implement your logging logic
        print(f"{model_name} {{model.id}} {{event}}")
        if extra_data:
            print(f"Extra data: {{extra_data}}")
    
    def send_notification(self, message: str) -> None:
        """Send notification"""
        # Implement your notification logic
        print(f"Notification: {{message}}")
    
    def update_search_index(self, model: Any) -> None:
        """Update search index"""
        # Implement your search index update logic
        pass
    
    def sync_with_external_service(self, model: Any) -> None:
        """Sync with external service"""
        # Implement your external service sync logic
        pass
'''