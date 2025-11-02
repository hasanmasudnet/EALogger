"""
Enhanced logging setup with rotation, console output, and context support
"""

import logging
import logging.handlers
import os
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .formatters import JSONFormatter, ColoredConsoleFormatter

__all__ = [
    "get_logger",
    "set_default_app_name",
    "get_default_app_name",
    "set_default_log_dir",
    "get_default_log_dir",
    "ContextLoggerAdapter",
]

# --- Globals ---
_default_app_name = "default"
_default_log_dir = os.getenv("LOG_BASE_DIR", os.path.join(".", "logs"))

# Configuration defaults
_LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10MB
_LOG_BACKUP_COUNT = 5
_LOG_CONSOLE_ENABLED = os.getenv("LOG_CONSOLE", "true").lower() == "true"


def set_default_app_name(app_name: str):
    """Set a global default app name for all decorators and loggers."""
    global _default_app_name
    _default_app_name = app_name


def get_default_app_name() -> str:
    """Get the current global default app name."""
    return _default_app_name


def set_default_log_dir(path: str):
    """Set a global default log directory base (overrides env var)."""
    global _default_log_dir
    _default_log_dir = path


def get_default_log_dir() -> str:
    """Get the current global default log directory base."""
    return _default_log_dir


class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    Enhanced logger adapter that injects context fields into log records.
    Supports username and any other context fields.
    """
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any] = None):
        """
        Initialize adapter with logger and context dict.
        
        Args:
            logger: Base logger instance
            context: Dict of context fields to inject (e.g., {"username": "john", "user_id": 123})
        """
        super().__init__(logger, context or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message and inject context fields.
        Merges context with any extra fields passed in kwargs.
        """
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}
        return msg, kwargs


def get_logger(
    name: str,
    app_name: Optional[str] = None,
    use_json: bool = True,
    username: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    enable_console: Optional[bool] = None,
    enable_rotation: bool = True,
    rotation_size: int = _LOG_ROTATION_SIZE,
    backup_count: int = _LOG_BACKUP_COUNT,
) -> logging.LoggerAdapter:
    """
    Return a logger with consistent, production-ready configuration.
    
    Features:
    - Logs stored under <base_dir>/<app_name>/<YYYY-MM>/<app_name>-<YYYY-MM-DD>.log
    - Base dir can be overridden via LOG_BASE_DIR env var or set_default_log_dir()
    - All timestamps in UTC
    - JSON by default for EFK/log aggregation
    - Optional log rotation (10MB, 5 backups)
    - Optional colored console output
    - Context injection support
    
    Args:
        name: Logger name (typically __name__)
        app_name: Application name (defaults to global default)
        use_json: Use JSON formatting (default: True)
        username: Username to inject (deprecated, use context instead)
        context: Dict of context fields to inject
        enable_console: Enable colored console output (default: from LOG_CONSOLE env var)
        enable_rotation: Enable log rotation (default: True)
        rotation_size: Max file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    
    Returns:
        LoggerAdapter configured with context and handlers
    """
    # Fallback to global default if not passed explicitly
    if app_name is None:
        app_name = get_default_app_name()
    
    # Merge username into context for backward compatibility
    if username is not None:
        if context is None:
            context = {}
        context["username"] = username
    
    # Ensure directory path is UTC-based by month
    utc_today = datetime.now(timezone.utc).date()
    log_dir = os.path.join(get_default_log_dir(), app_name, utc_today.strftime("%Y-%m"))
    os.makedirs(log_dir, exist_ok=True)
    
    # Daily log file (UTC)
    log_filename = f"{app_name}-{utc_today.strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    logger = logging.getLogger(name)
    
    # Only add handlers if none exist for this file path
    has_file_handler = any(
        isinstance(h, (logging.FileHandler, logging.handlers.RotatingFileHandler)) 
        and getattr(h, "baseFilename", None) == os.path.abspath(log_path)
        for h in logger.handlers
    )
    
    if not has_file_handler:
        # File handler with optional rotation
        if enable_rotation:
            handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=rotation_size,
                backupCount=backup_count,
                mode="a",
                encoding="utf-8"
            )
        else:
            handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        
        # Set formatter
        if use_json:
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            )
            formatter.converter = time.gmtime  # Force UTC in plain text
            handler.setFormatter(formatter)
        
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    
    # Console handler (optional, colored output)
    if enable_console is None:
        enable_console = _LOG_CONSOLE_ENABLED
    
    if enable_console:
        has_console_handler = any(
            isinstance(h, logging.StreamHandler)
            for h in logger.handlers
        )
        if not has_console_handler:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(ColoredConsoleFormatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            ))
            console_handler.setLevel(logging.INFO)  # Console shows INFO and above
            logger.addHandler(console_handler)
    
    # Set logger level
    logger.setLevel(logging.DEBUG)
    
    # Return wrapped logger with context
    default_context = {"username": "-"}  # Backward compatibility
    if context:
        default_context.update(context)
    
    return ContextLoggerAdapter(logger, default_context)

