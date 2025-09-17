"""Laravel-like logging system with multiple channels"""

import logging
import logging.handlers
import json
from pathlib import Path
from typing import Dict, Optional, Any

class LarapyLogger:
    """Laravel-like logging system with multiple channels"""

    def __init__(self, app):
        self.app = app
        self.loggers = {}
        self.current_channel = None
        self.setup_logging()

    def setup_logging(self):
        """Initialize logging configuration from config/logging.py"""
        config = self.app.config.get('logging.config', {})
        if not config:
            # Fallback config if no config file found
            config = {
                'default': 'single',
                'channels': {
                    'single': {
                        'driver': 'single',
                        'path': 'larapy.log',
                        'level': 'DEBUG'
                    }
                }
            }

        # Ensure storage/logs directory exists
        log_dir = Path(self.app.base_path()) / 'storage' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # Setup channels
        channels = config.get('channels', {})
        for channel_name, channel_config in channels.items():
            self.setup_channel(channel_name, channel_config, log_dir)

        # Set default channel
        self.current_channel = config.get('default', 'single')

    def setup_channel(self, name: str, config: Dict, log_dir: Path):
        """Setup individual logging channel"""
        logger = logging.getLogger(f'larapy.{name}')
        logger.setLevel(getattr(logging, config.get('level', 'DEBUG')))

        # Clear existing handlers
        logger.handlers = []

        driver = config.get('driver', 'single')

        if driver == 'single':
            handler = logging.FileHandler(
                log_dir / config.get('path', 'larapy.log')
            )
        elif driver == 'daily':
            handler = logging.handlers.TimedRotatingFileHandler(
                log_dir / config.get('path', 'larapy.log'),
                when='midnight',
                interval=1,
                backupCount=config.get('days', 14)
            )
            # Add date suffix to daily logs
            handler.suffix = '%Y-%m-%d'
        elif driver == 'stack':
            # Stack combines multiple channels
            self.setup_stack_channel(name, config, log_dir)
            return
        elif driver == 'errorlog':
            handler = logging.StreamHandler()
        elif driver == 'null':
            handler = logging.NullHandler()
        else:
            handler = logging.StreamHandler()

        # Set formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s.%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.loggers[name] = logger

    def setup_stack_channel(self, name: str, config: Dict, log_dir: Path):
        """Setup stack channel that combines multiple channels"""
        logger = logging.getLogger(f'larapy.{name}')
        logger.setLevel(logging.DEBUG)
        logger.handlers = []

        # Get channels to stack
        channels = config.get('channels', [])
        logging_config = self.app.config.get('logging.config', {})

        for channel_name in channels:
            # Get channel config
            channel_config = logging_config.get('channels', {}).get(channel_name, {})
            if channel_config:
                # Create handler for this channel
                driver = channel_config.get('driver', 'single')

                if driver == 'single':
                    handler = logging.FileHandler(
                        log_dir / channel_config.get('path', 'larapy.log')
                    )
                elif driver == 'daily':
                    handler = logging.handlers.TimedRotatingFileHandler(
                        log_dir / channel_config.get('path', 'larapy.log'),
                        when='midnight',
                        interval=1,
                        backupCount=channel_config.get('days', 14)
                    )
                else:
                    continue

                # Set level and formatter
                handler.setLevel(getattr(logging, channel_config.get('level', 'DEBUG')))
                formatter = logging.Formatter(
                    '[%(asctime)s] %(name)s.%(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

        self.loggers[name] = logger

    def channel(self, channel: str = None):
        """Get a specific channel or set current channel"""
        if channel is None:
            channel = self.current_channel

        # Create a new instance with the specified channel
        new_logger = LarapyLogger.__new__(LarapyLogger)
        new_logger.app = self.app
        new_logger.loggers = self.loggers
        new_logger.current_channel = channel
        return new_logger

    def get_logger(self, channel: str = None):
        """Get logger instance for specified channel"""
        if channel is None:
            channel = self.current_channel or self.app.config.get('logging.config.default', 'single')
        return self.loggers.get(channel, logging.getLogger())

    def emergency(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log emergency message"""
        self.log('CRITICAL', message, context)

    def alert(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log alert message"""
        self.log('CRITICAL', message, context)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self.log('CRITICAL', message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.log('ERROR', message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.log('WARNING', message, context)

    def notice(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log notice message"""
        self.log('INFO', message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.log('INFO', message, context)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.log('DEBUG', message, context)

    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message with context"""
        logger = self.get_logger()

        # Format message with context
        if context:
            try:
                context_str = json.dumps(context, default=str)
                message = f"{message} | Context: {context_str}"
            except (TypeError, ValueError):
                message = f"{message} | Context: {str(context)}"

        # Log the message
        getattr(logger, level.lower())(message)

    def write_log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Write log entry (alias for log method)"""
        self.log(level, message, context)