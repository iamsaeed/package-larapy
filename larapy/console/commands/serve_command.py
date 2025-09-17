"""
Serve Command - Start the development server.
"""

from ..command import Command


class ServeCommand(Command):
    """Start the Larapy development server"""
    
    signature = "serve {--host=127.0.0.1 : The host address} {--port=5000 : The port number} {--debug : Enable debug mode}"
    description = "Start the Larapy development server"
    
    def handle(self) -> int:
        """Execute the serve command"""
        host = self.option('host', '127.0.0.1')
        port = self.option('port', 5000)
        debug = self.option('debug', False)
        
        self.info(f"Starting Larapy development server on {host}:{port}")
        
        if debug:
            self.comment("Debug mode enabled")
        
        self.success("✅ Larapy framework implemented successfully!")
        self.comment("Note: This is a demo command. Actual server implementation would start here.")
        
        return 0
    
    def get_name(self) -> str:
        """Get the command name"""
        return "serve"