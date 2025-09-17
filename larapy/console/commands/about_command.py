"""
About Command - Display application information.
"""

from ..command import Command


class AboutCommand(Command):
    """Display information about the application"""
    
    signature = "about"
    description = "Display application information"
    
    def handle(self) -> int:
        """Execute the about command"""
        self.info("Larapy Framework")
        self.line("Laravel-inspired framework for Python")
        self.line()
        
        # Application info
        app_info = [
            ["Framework", "Larapy"],
            ["Version", "1.0.0"],
            ["Environment", "development"],
            ["Debug", "enabled"],
        ]
        
        self.table(["Setting", "Value"], app_info)
        
        return 0
    
    def get_name(self) -> str:
        """Get the command name"""
        return "about"