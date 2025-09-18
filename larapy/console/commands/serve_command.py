"""Serve console command"""

import os
import signal
import sys
from typing import Optional
from ...console.command import Command


class ServeCommand(Command):
    """Start the development server"""
    
    signature = "serve {--host=127.0.0.1 : The host address to serve the application on} {--port=5000 : The port to serve the application on} {--debug : Run the server in debug mode}"
    description = "Start the Larapy development server"

    def handle(self) -> int:
        """Execute the serve command"""
        
        # Get options
        host = self.option('host') or '127.0.0.1'
        port = self.option('port') or 5000
        debug = self.option('debug')

        # Convert port to int if it's a string
        try:
            port = int(port)
        except (ValueError, TypeError):
            self.error(f"Invalid port number: {port}")
            return 1

        # Validate host
        if not host:
            host = '127.0.0.1'

        try:
            # Bootstrap the application
            app = self._bootstrap_application()
            
            if not app:
                self.error("Failed to bootstrap application")
                return 1

            # Display server info
            self._display_server_info(host, port, debug)
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Start the server
            app.run(host=host, port=port, debug=debug)
            
            return 0
            
        except KeyboardInterrupt:
            self.info("\\nServer stopped by user")
            return 0
        except Exception as e:
            self.error(f"Failed to start server: {str(e)}")
            return 1

    def _bootstrap_application(self):
        """Bootstrap the Larapy application"""
        try:
            # Import the application bootstrap
            from bootstrap.app import create_application
            
            # Create and return the application
            app = create_application()
            
            return app
            
        except ImportError:
            self.error("Could not import application bootstrap.")
            self.comment("Make sure you're running this command from the application root directory.")
            return None
        except Exception as e:
            self.error(f"Failed to bootstrap application: {str(e)}")
            return None

    def _display_server_info(self, host: str, port: int, debug: bool = None):
        """Display server startup information"""
        self.info("Starting Larapy development server...")
        
        # Show server details
        self.line(f"  Host: {host}")
        self.line(f"  Port: {port}")
        
        if debug is not None:
            self.line(f"  Debug: {'Enabled' if debug else 'Disabled'}")
        
        # Show URLs
        if host == '0.0.0.0':
            self.line(f"  Local URL: http://127.0.0.1:{port}")
            self.line(f"  Network URL: http://{self._get_local_ip()}:{port}")
        else:
            self.line(f"  URL: http://{host}:{port}")
        
        self.line("")
        self.success("Server is running! Press Ctrl+C to stop.")
        self.comment("Tip: Use --host=0.0.0.0 to accept connections from any IP address")
        self.line("")

    def _get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            import socket
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "localhost"

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            self.line("\\n")
            self.info("Shutting down server...")
            sys.exit(0)
        
        # Handle Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Handle termination signal (SIGTERM) on Unix systems
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)