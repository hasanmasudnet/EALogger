"""
Enhanced logging setup with rotation, console output, and context support
+ CustomLogger for extended method signatures
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
    "CustomLogger",
]

# --- Globals ---
_default_app_name = "default"
_default_log_dir = os.getenv("LOG_BASE_DIR", os.path.join(".", "logs"))

# Configuration defaults
_LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10MB
_LOG_BACKUP_COUNT = 5
_LOG_CONSOLE_ENABLED = os.getenv("LOG_CONSOLE", "true").lower() == "true"


# ----------------------------------------------------------------------
# Custom Logger (extends base logger)
# ----------------------------------------------------------------------
class CustomLogger(logging.Logger):
    """
    Custom logger that supports calls like:
        logger.info("Message", "action", "method", extra={...})
    """

    def _inject_action_method(self, action, method, username, module_name, kwargs):
        """Merge 'action' and 'method' into extra fields."""
        extra = kwargs.get("extra", {})
        if action:
            extra["action"] = action
        if method:
            extra["method"] = method
        if username:
            extra["username"] = username
        if module_name:
            extra["module_name"] = module_name
        kwargs["extra"] = extra
        return kwargs

    def info(self, msg, action=None, method=None,username=None, module_name=None, *args, **kwargs):
        kwargs = self._inject_action_method(action, method,username, module_name, kwargs)
        super().info(msg, *args, **kwargs)

    def debug(self, msg, action=None, method=None, username=None, module_name=None, *args, **kwargs):       
        kwargs = self._inject_action_method(action, method,username, module_name, kwargs)       
        super().debug(msg, *args, **kwargs)

    def warning(self, msg, action=None, method=None,username=None, module_name=None, *args, **kwargs):
        kwargs = self._inject_action_method(action, method,username, module_name, kwargs)
        super().warning(msg, *args, **kwargs)

    def error(self, msg, action=None, method=None, username=None, module_name=None, *args, **kwargs):
        kwargs = self._inject_action_method(action, method,username, module_name, kwargs)
        super().error(msg, *args, **kwargs)

    def critical(self, msg, action=None, method=None, username=None, module_name=None, *args, **kwargs):
        kwargs = self._inject_action_method(action, method,username, module_name, kwargs)
        super().critical(msg, *args, **kwargs)


# ensure all future loggers are instances of CustomLogger
logging.setLoggerClass(CustomLogger)


# ----------------------------------------------------------------------
# Context Logger Adapter
# ----------------------------------------------------------------------
class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    Enhanced logger adapter that injects context fields into log records.
    Supports username and any other context fields.
    """

    def __init__(self, logger: logging.Logger, context: Dict[str, Any] = None):
        super().__init__(logger, context or {})

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}
        return msg, kwargs



    # --- override common logging methods to forward action/method ---
    def info(self, msg, action=None, method=None, username=None, module=None, *args, **kwargs):
        # print("HI SANJK inof")
        # print(kwargs)
        return self.logger.info(msg, action, method,username, module, *args, **kwargs)

    def debug(self, msg, action=None, method=None,username=None, module=None,  *args, **kwargs):
       
        return self.logger.debug(msg, action, method,username, module, *args, **kwargs)

    def warning(self, msg, action=None, method=None,username=None, module=None,  *args, **kwargs):
        return self.logger.warning(msg, action, method,username, module, *args, **kwargs)

    def error(self, msg, action=None, method=None,username=None, module=None,  *args, **kwargs):
        return self.logger.error(msg, action, method,username, module, *args, **kwargs)

    def critical(self, msg, action=None, method=None,username=None, module=None,  *args, **kwargs):
        return self.logger.critical(msg, action, method, username, module, *args, **kwargs)


# ----------------------------------------------------------------------
# Default app/log directory management
# ----------------------------------------------------------------------
def set_default_app_name(app_name: str):
    global _default_app_name
    _default_app_name = app_name


def get_default_app_name() -> str:
    return _default_app_name


def set_default_log_dir(path: str):
    global _default_log_dir
    _default_log_dir = path


def get_default_log_dir() -> str:
    return _default_log_dir


# ----------------------------------------------------------------------
# Main logger factory
# ----------------------------------------------------------------------
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
    - JSON by default for EFK/log aggregation
    - Optional log rotation (10MB, 5 backups)
    - Optional colored console output
    - Context injection support
    - CustomLogger supports shorthand signatures like:
        logger.info("msg", "action", "method", extra={})
    """

    # --- Ensure we rebuild this logger as a CustomLogger ---
    if name in logging.Logger.manager.loggerDict:
        del logging.Logger.manager.loggerDict[name]

    logger = logging.getLogger(name)

    # --- App name fallback ---
    if app_name is None:
        app_name = get_default_app_name()

    # --- Merge username into context (legacy support) ---
    if username is not None:
        if context is None:
            context = {}
        context["username"] = username + "SA"

    # --- Prepare log directory ---
    utc_today = datetime.now(timezone.utc).date()
    log_dir = os.path.join(get_default_log_dir(), app_name, utc_today.strftime("%Y-%m"))
    os.makedirs(log_dir, exist_ok=True)

    log_filename = f"{app_name}-{utc_today.strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(log_dir, log_filename)

    # --- File handler ---
    has_file_handler = any(
        isinstance(h, (logging.FileHandler, logging.handlers.RotatingFileHandler))
        and getattr(h, "baseFilename", None) == os.path.abspath(log_path)
        for h in logger.handlers
    )

    if not has_file_handler:
        if enable_rotation:
            handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=rotation_size,
                backupCount=backup_count,
                mode="a",
                encoding="utf-8",
            )
        else:
            handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")

        if use_json:
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s - "
                "action=%(action)s - method=%(method)s - details=%(details)s"
            )
            formatter.converter = time.gmtime  # force UTC
            handler.setFormatter(formatter)

        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    # --- Console handler ---
    if enable_console is None:
        enable_console = _LOG_CONSOLE_ENABLED

    if enable_console:
        has_console_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        if not has_console_handler:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                ColoredConsoleFormatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
            )
            console_handler.setLevel(logging.INFO)
            logger.addHandler(console_handler)

    # --- Set level and wrap in adapter ---
    logger.setLevel(logging.DEBUG)

    default_context = {"username": "-"}
    if context:
        default_context.update(context)

    return ContextLoggerAdapter(logger, default_context)
