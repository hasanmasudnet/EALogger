"""
Enhanced formatters with orjson support and colored console output
"""

import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict

__all__ = ["JSONFormatter", "ColoredConsoleFormatter"]

# Try to use orjson for 3-5x better performance
try:
    import orjson
    USE_ORJSON = True
except ImportError:
    USE_ORJSON = False


class JSONFormatter(logging.Formatter):
    """
    Enhanced JSON log formatter with explicit UTC timestamps and comprehensive fields.
    Uses orjson for better performance when available.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_orjson = USE_ORJSON
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with comprehensive fields"""      
       # Base log record
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            # "module": record.module,
            "action": getattr(record, "action", None),
            "method": getattr(record, "method", None),
            "username": getattr(record, "username", None),
            "message": record.getMessage(),
        }

       # Standard fields to skip for extras
        standard_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
            'filename', 'module', 'lineno', 'funcName', 'created',
            'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
            'username', 'taskName', 'action', 'method'
        }     
        
         # Add extra fields from record.__dict__
        for key, value in record.__dict__.items():
            if key not in standard_fields:
                log_record[key] = value       

        # Serialize to JSON
        if self.use_orjson:
            return orjson.dumps(log_record, default=str).decode('utf-8')
        else:
            return json.dumps(log_record, default=str)
        
        
    
    def formatException(self, exc_info) -> str:
        """Format exception info as string"""
        if self.use_orjson:
            # orjson doesn't have formatException, fall back to standard
            import traceback
            return traceback.format_exception(*exc_info)
        else:
            return super().formatException(exc_info)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for better readability in terminal output.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset color
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Format the message
        formatted = super().format(record)
        return f"{log_color}{formatted}{reset_color}"

