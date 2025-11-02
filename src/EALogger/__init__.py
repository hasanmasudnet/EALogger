"""
EALogger - Enhanced Async Logging for FastAPI Projects
A production-ready logging library with JSON formatting, performance tracking, and async support.
"""

from .logging_setup import (
    get_logger,
    set_default_app_name,
    get_default_app_name,
    set_default_log_dir,
    get_default_log_dir,
)
from .decorators import log_entry_exit, log_entry_exit_async, log_performance, log_performance_async
from .formatters import JSONFormatter, ColoredConsoleFormatter
from .search import LogSearcher

__version__ = "0.2.0"

__all__ = [
    "get_logger",
    "set_default_app_name",
    "get_default_app_name",
    "set_default_log_dir",
    "get_default_log_dir",
    "log_entry_exit",
    "log_entry_exit_async",
    "log_performance",
    "log_performance_async",
    "JSONFormatter",
    "ColoredConsoleFormatter",
    "LogSearcher",
]

