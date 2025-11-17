from contextvars import ContextVar
current_app_name = ContextVar("current_app_name", default=None)
