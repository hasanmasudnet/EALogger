"""
Function decorators for automatic logging of entry, exit, exceptions, and performance
"""

import functools
import time
from typing import Callable, Any
from .logging_setup import get_logger, get_default_app_name


__all__ = ["log_entry_exit", "log_entry_exit_async", "log_performance", "log_performance_async"]


def log_entry_exit(func: Callable = None, *, app_name: str = None, use_json: bool = True):
    """
    Decorator to log function entry, exit, and exceptions.
    
    Logs:
    - Entry with args/kwargs
    - Exit with success
    - Exceptions with traceback
    
    Args:
        app_name: Application name (defaults to global default)
        use_json: Use JSON formatting (default: True)
    
    Example:
        @log_entry_exit
        def my_function(x, y):
            return x + y
        
        @log_entry_exit(app_name="myapp", use_json=False)
        def another_function():
            pass
    """
    
    def decorator(inner_func: Callable) -> Callable:
        logger = get_logger(
            inner_func.__module__,
            app_name=app_name or get_default_app_name(),
            use_json=use_json,
        )
        
        @functools.wraps(inner_func)
        def wrapper(*args, **kwargs):
            logger.debug(
                f"Entering {inner_func.__name__}",
                "ENTRY",               
                "CALL",
                "system",
                f"{app_name}",
                extra={}
            ) 
            try:
                result = inner_func(*args, **kwargs)
                logger.debug(
                    f"Exiting {inner_func.__name__}",
                    "EXIT",
                    "CALL",
                    "system",
                   f"{app_name}",
                  extra={}
                )
                return result
            except Exception as e:
                logger.error(
                    f"Exception in {inner_func.__name__}: {e}",
                    "EXCEPTION",
                    "CALL",
                    "system",
                    f"{app_name}",
                   extra={}
                )
                raise
        
        return wrapper
    
    return decorator(func) if func else decorator


def log_entry_exit_async(func: Callable = None, *, app_name: str = None, use_json: bool = True):
    """
    Async version of log_entry_exit decorator.
    
    Example:
        @log_entry_exit_async
        async def my_async_function(x, y):
            await some_async_op()
            return x + y
    """

    def decorator(inner_func: Callable) -> Callable:
        logger = get_logger(
            inner_func.__module__,
            app_name=app_name or get_default_app_name(),
            use_json=use_json,
        )
                
        @functools.wraps(inner_func)
        async def async_wrapper(*args, **kwargs):
          
            logger.debug(
                f"Entering {inner_func.__name__}",
                "ENTRY",
                "CALL",
                "system",
                f"{app_name}",
                extra={}
            )            
            try:
                result = await inner_func(*args, **kwargs)
                logger.debug(
                    f"Exiting {inner_func.__name__}",
                    "EXIT",
                    "CALL",
                    "system",
                    f"{app_name}",
                  extra={}
                )
                return result
            except Exception as e:
                logger.error(
                    f"Exception in {inner_func.__name__}: {e}",
                    "EXCEPTION",
                    "CALL",
                    "system",
                   f"{app_name}",
                   extra={}
                )
                raise
        
        return async_wrapper
    
    return decorator(func) if func else decorator


def log_performance(
    func: Callable = None,
    *,
    app_name: str = None,
    use_json: bool = True,
    threshold_ms: float = 1000.0
):
    """
    Decorator to log function execution time.
    
    Logs:
    - Slow execution warnings (default: >1000ms)
    
    Args:
        app_name: Application name (defaults to global default)
        use_json: Use JSON formatting (default: True)
        threshold_ms: Time threshold for warnings in milliseconds (default: 1000)
    
    Example:
        @log_performance(threshold_ms=500)
        def slow_function():
            time.sleep(2)  # Will log as slow
    """
    
    def decorator(inner_func: Callable) -> Callable:
        logger = get_logger(
            inner_func.__module__,
            app_name=app_name or get_default_app_name(),
            use_json=use_json,
        )
        
        @functools.wraps(inner_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = inner_func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > threshold_ms:
                    logger.warning(
                        "Slow execution in %s: %.2fms (threshold: %.2fms)",
                        inner_func.__name__,
                        duration_ms,
                        threshold_ms
                    )
                else:
                    logger.debug(
                        "Execution time in %s: %.2fms",
                        inner_func.__name__,
                        duration_ms
                    )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Exception in %s after %.2fms: %r",
                    inner_func.__name__,
                    duration_ms,
                    e,
                    exc_info=True
                )
                raise
        
        return wrapper
    
    return decorator(func) if func else decorator


def log_performance_async(
    func: Callable = None,
    *,
    app_name: str = None,
    use_json: bool = True,
    threshold_ms: float = 1000.0
):
    """
    Async version of log_performance decorator.
    
    Example:
        @log_performance_async(threshold_ms=500)
        async def slow_async_function():
            await asyncio.sleep(2)  # Will log as slow
    """
    
    def decorator(inner_func: Callable) -> Callable:
        logger = get_logger(
            inner_func.__module__,
            app_name=app_name or get_default_app_name(),
            use_json=use_json,
        )
        
        @functools.wraps(inner_func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await inner_func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > threshold_ms:
                    logger.warning(
                        "Slow execution in %s: %.2fms (threshold: %.2fms)",
                        inner_func.__name__,
                        duration_ms,
                        threshold_ms
                    )
                else:
                    logger.debug(
                        "Execution time in %s: %.2fms",
                        inner_func.__name__,
                        duration_ms
                    )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Exception in %s after %.2fms: %r",
                    inner_func.__name__,
                    duration_ms,
                    e,
                    exc_info=True
                )
                raise
        
        return async_wrapper
    
    return decorator(func) if func else decorator

