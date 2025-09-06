"""
logger.py
Logging Utilities Module
Provides logging setup and configuration for the Discord bot.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from config import LOGGING_CONFIG

def setup_logger(name=None):
    """
    Setup and configure logger for the bot
    
    Args:
        name (str, optional): Logger name. Defaults to root logger.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Set logging level
    log_level = getattr(logging, LOGGING_CONFIG['level'], logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        LOGGING_CONFIG['format'],
        datefmt=LOGGING_CONFIG['date_format']
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Add color formatting for console output
    if hasattr(console_handler.stream, 'isatty') and console_handler.stream.isatty():
        console_handler.setFormatter(ColoredFormatter(
            LOGGING_CONFIG['format'],
            datefmt=LOGGING_CONFIG['date_format']
        ))
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if LOGGING_CONFIG['log_to_file']:
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(LOGGING_CONFIG['log_file'])
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                LOGGING_CONFIG['log_file'],
                maxBytes=LOGGING_CONFIG['max_log_size'],
                backupCount=LOGGING_CONFIG['backup_count'],
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    # Set discord.py logging level to WARNING to reduce spam
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
    
    # Set urllib3 logging level to WARNING to reduce spam
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.WARNING)
    
    return logger

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Get original formatted message
        original = super().format(record)
        
        # Add color if level has one
        if record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS['RESET']
            return f"{color}{original}{reset}"
        
        return original

def log_command_execution(logger, ctx, command_name, execution_time=None, error=None):
    """
    Log command execution with context information
    
    Args:
        logger: Logger instance
        ctx: Discord command context
        command_name (str): Name of the command
        execution_time (float, optional): Command execution time in seconds
        error (Exception, optional): Exception if command failed
    """
    
    # Build base log message
    user_info = f"{ctx.author} (ID: {ctx.author.id})"
    guild_info = f"in {ctx.guild.name}" if ctx.guild else "in DM"
    channel_info = f"#{ctx.channel.name}" if hasattr(ctx.channel, 'name') else "DM"
    
    base_msg = f"Command '{command_name}' executed by {user_info} {guild_info} {channel_info}"
    
    if error:
        logger.error(f"{base_msg} - ERROR: {error}")
    elif execution_time:
        logger.info(f"{base_msg} - Completed in {execution_time:.2f}s")
    else:
        logger.info(base_msg)

def log_event(logger, event_name, **kwargs):
    """
    Log Discord events with additional context
    
    Args:
        logger: Logger instance
        event_name (str): Name of the event
        **kwargs: Additional context information
    """
    
    context_parts = []
    for key, value in kwargs.items():
        if hasattr(value, 'name') and hasattr(value, 'id'):
            context_parts.append(f"{key}={value.name}(ID:{value.id})")
        else:
            context_parts.append(f"{key}={value}")
    
    context_str = " ".join(context_parts) if context_parts else ""
    log_msg = f"Event '{event_name}'"
    
    if context_str:
        log_msg += f" - {context_str}"
    
    logger.debug(log_msg)

def setup_debug_logging():
    """Setup debug logging for development"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

class LoggingContext:
    """Context manager for temporary logging configuration"""
    
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.original_level = None
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)
