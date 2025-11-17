import functools
import inspect
import asyncio
import json
from typing import Callable
from fastapi import Request
from .logging_setup import get_logger, get_default_app_name
import time
 

__all__ = ["log_entry_exit", "log_entry_exit_async", "log_performance", "log_performance_async"]

from EALogger.context import current_app_name

async def get_request_body(request: Request):
    """
    Safely get the request body without consuming it for downstream handlers.
    Returns:
        dict or str or None
    """
    body_bytes = await request.body()

    # Reset the body so it can be read later by the endpoint
    async def receive() -> dict:
        return {"type": "http.request", "body": body_bytes}
    request._receive = receive  # override internal _receive

    # Try to parse JSON, fallback to string
    try:
        return json.loads(body_bytes.decode("utf-8"))  # dict if JSON
    except Exception:
        try:
            return body_bytes.decode("utf-8")  # raw string
        except Exception:
            return None


async def log_request_info(request: Request = None) -> dict:
    """Extracts detailed request info including body as key-value if JSON."""
    if not request:
        return {}

    try:
        client_host = request.client.host if request.client else "unknown"
    except Exception:
        client_host = "unknown"

    try:
        headers = dict(request.headers)
    except Exception:
        headers = {}

    try:
        query_params = dict(request.query_params)
    except Exception:
        query_params = {}

    body = await get_request_body(request) if request else None

    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": query_params,
        "headers": headers,
        "client_host": client_host,
        "body": body,  # JSON dict or raw string
    }


async def _extract_context(args, kwargs, inner_func) -> dict:
    """Extract context for logging."""
    request = next(
        (arg for arg in args if isinstance(arg, Request)),
        next((v for v in kwargs.values() if isinstance(v, Request)), None)
    )

    req_info = await log_request_info(request) if request else {}
    cls = args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else None
    function_name = inner_func.__qualname__
    file = inspect.getsourcefile(inner_func)
    line = inspect.getsourcelines(inner_func)[1]
    username = getattr(getattr(request, "state", 'system'), "username", 'system') if request else 'system'

    return {
        "request": request,
        "method": req_info.get("method"),
        "url": req_info.get("url"),
        "path": req_info.get("path"),
        "query_params": req_info.get("query_params"),
        "headers": req_info.get("headers"),
        "client_host": req_info.get("client_host"),
        "body": req_info.get("body"),
        "cls": cls,
        "function_name": function_name,
        "file": file,
        "line": line,
        "username": username,
    }


def log_entry_exit(func: Callable = None, *, app_name: str = None, use_json: bool = True):
    """
    Decorator to log function entry, exit, exceptions, and execution time,
    including request body as key-value if JSON.
    """

    def decorator(inner_func: Callable) -> Callable:
        logger = get_logger(
            inner_func.__module__,
            app_name=app_name or get_default_app_name(),
            use_json=use_json,
        )

        @functools.wraps(inner_func)
        async def async_wrapper(*args, **kwargs):
            token = current_app_name.set(app_name) 

            context = await _extract_context(args, kwargs, inner_func)
            start_time = time.perf_counter()

            extra_info = {k: v for k, v in context.items() if k not in ["request", "cls", "function_name", "file", "line", "url"]}

            extra_info['module_name'] =app_name


            logger.debug(
                f"Entering {context['function_name']}",
                f"ENTRY-{context.get('path')}",
                context.get("method"),
                context.get("username"),
                f"{app_name}",
                extra=extra_info
            )

            try:
                result = await inner_func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                extra_info['duration_ms'] = round(duration_ms, 2)
                extra_info['body'] = {}
                extra_info['headers'] = {}
                extra_info['query_params'] = {}

                logger.debug(
                    f"Exiting {context['function_name']}",
                    f"EXIT-{context.get('path')}",
                    context.get("method"),
                    context.get("username"),
                    f"{app_name}",
                    extra=extra_info
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                extra_info['duration_ms'] = round(duration_ms, 2)
                extra_info['body'] = {}
                extra_info['headers'] = {}
                extra_info['query_params'] = {}

                logger.error(
                    f"Exception in {context['function_name']}: {e}",
                    f"EXCEPTION-{context.get('path')}",
                    context.get("method"),
                    context.get("username"),
                    f"{app_name}",
                    extra=extra_info
                )
                raise
            finally:
                current_app_name.reset(token)

        @functools.wraps(inner_func)
        def sync_wrapper(*args, **kwargs):
            token = current_app_name.set(app_name) 
            # In sync context, we cannot read request body asynchronously, so body will be None
            context = asyncio.run(_extract_context(args, kwargs, inner_func))
            start_time = time.perf_counter()
            extra_info = {k: v for k, v in context.items() if k not in ["request", "cls", "function_name", "file", "line", "url"]}
            extra_info['module_name'] =app_name

            logger.debug(
                f"Entering {context['function_name']}",
                f"ENTRY-{context.get('path')}",
                context.get("method"),
                context.get("username"),
                f"{app_name}",
                extra=extra_info
            )

            try:
                result = inner_func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                extra_info['duration_ms'] = round(duration_ms, 2)
                extra_info['body'] = {}
                extra_info['headers'] = {}
                extra_info['query_params'] = {}

                logger.debug(
                    f"Exiting {context['function_name']}",
                    f"EXIT-{context.get('path')}",
                    context.get("method"),
                    context.get("username"),
                    f"{app_name}",
                    extra=extra_info
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                extra_info['duration_ms'] = round(duration_ms, 2)
                extra_info['body'] = {}
                extra_info['headers'] = {}
                extra_info['query_params'] = {}

                logger.error(
                    f"Exception in {context['function_name']}: {e}",
                    f"EXCEPTION-{context.get('path')}",
                    context.get("method"),
                    context.get("username"),
                    f"{app_name}",
                    extra=extra_info
                )
                raise
            finally:
                current_app_name.reset(token)  

        return async_wrapper if asyncio.iscoroutinefunction(inner_func) else sync_wrapper

    return decorator(func) if func else decorator
