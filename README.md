# EALogger

**Enhanced Async Logging for FastAPI Projects**

A production-ready Python logging library with JSON formatting, performance tracking, async support, and fast log search capabilities.

## Features

✨ **Core Features:**
- 📄 **JSON Logging** - Structured, EFK-ready output with UTC timestamps
- 🔄 **Log Rotation** - Automatic file rotation (10MB, 5 backups)
- 🎨 **Colored Console** - Readable terminal output with ANSI colors
- ⚡ **High Performance** - Uses orjson for 3-5x faster JSON operations
- 🔍 **Fast Search** - NDJSON search utilities with optional orjson
- 🧵 **Async Support** - Decorators work with async functions
- 📊 **Performance Tracking** - Built-in execution time monitoring
- 🎯 **Context Injection** - User, session, and custom context fields

## Installation

### Basic Installation

```bash
pip install EALogger
```

### With Fast JSON Support (Recommended)

```bash
pip install "EALogger[fast]"
```

This installs `orjson` for 3-5x faster JSON parsing when searching logs.

### Development Installation

```bash
git clone https://github.com/hasanmasudnet/EALogger.git
cd EALogger
pip install -e ".[dev,fast]"
```

## Quick Start

### Basic Usage

```python
from EALogger import get_logger, set_default_app_name

# Set default app name
set_default_app_name("myapp")

# Get logger
logger = get_logger(__name__)

# Log messages
logger.info("Application started")
logger.error("An error occurred", exc_info=True)
```

### With Context

```python
from EALogger import get_logger

# Logger with context
logger = get_logger(
    __name__,
    context={
        "user_id": 123,
        "session_id": "abc-xyz",
        "ip_address": "1.2.3.4"
    }
)

logger.info("User action performed")
```

### Decorators

```python
from EALogger import log_entry_exit, log_entry_exit_async, log_performance

# Track function entry/exit
@log_entry_exit
def my_function(x, y):
    return x + y

# Track async functions
@log_entry_exit_async
async def my_async_function():
    await some_async_operation()

# Track performance (warns if >1000ms by default)
@log_performance(threshold_ms=500)
def slow_function():
    time.sleep(2)  # Will log warning

# All decorators can be combined
@log_entry_exit
@log_performance(threshold_ms=100)
def complex_function():
    # ... your code
    pass
```

### Log Search

```python
from EALogger import LogSearcher

searcher = LogSearcher(base_log_dir="logs")

# Search logs by text
results = searcher.search_logs(
    app_name="myapp",
    query="error",
    level="ERROR",
    days_back=7
)

# Count logs by level
counts = searcher.count_logs(app_name="myapp")
# {'ERROR': 42, 'WARNING': 15, 'INFO': 1000}

# Get logs by time range
from datetime import datetime, timedelta
results = searcher.get_logs_by_time_range(
    app_name="myapp",
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now()
)
```

## Configuration

### Environment Variables

```bash
# Base log directory
export LOG_BASE_DIR="/var/log/myapp"

# Enable/disable console output
export LOG_CONSOLE="true"  # or "false"
```

### Programmatic Configuration

```python
from EALogger import set_default_app_name, set_default_log_dir

# Set default app name for all loggers
set_default_app_name("myapplication")

# Set default log directory
set_default_log_dir("/var/log/myapp")
```

### Advanced Logger Options

```python
from EALogger import get_logger

logger = get_logger(
    __name__,
    app_name="myapp",
    use_json=True,              # Use JSON formatting
    context={"user_id": 123},   # Inject context
    enable_console=True,        # Colored console output
    enable_rotation=True,       # Log rotation (default: True)
    rotation_size=10*1024*1024, # 10MB (default)
    backup_count=5              # Keep 5 backups (default)
)
```

## Log File Structure

```
logs/
└── myapp/
    └── 2025-01/
        ├── myapp-2025-01-15.log
        ├── myapp-2025-01-15.log.1
        └── myapp-2025-01-15.log.2
```

## JSON Log Format

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "myapp.main",
  "module": "main",
  "function": "setup",
  "line": 42,
  "message": "Application started",
  "user_id": 123,
  "session_id": "abc-xyz"
}
```

## Migration from v0.1.x

The new version is mostly backward compatible:

```python
# Old API (still works)
from EALogger import get_logger, set_default_app_name
logger = get_logger(__name__, username="john")

# New API (recommended)
from EALogger import get_logger, set_default_app_name
logger = get_logger(__name__, context={"username": "john"})
```

**Breaking Changes:**
- `log_entry_exit` decorator signature unchanged
- `UserLoggerAdapter` renamed to `ContextLoggerAdapter` (internal)
- Some internal classes renamed for clarity

## Performance

With `orjson` installed (install with `pip install "EALogger[fast]"`):

- **JSON Encoding**: 3-5x faster than standard library
- **JSON Decoding**: 3-5x faster when searching logs
- **Memory**: Lower memory footprint for large log files

## Examples

### FastAPI Integration

```python
from fastapi import FastAPI
from EALogger import get_logger, set_default_app_name, log_entry_exit

app = FastAPI()
set_default_app_name("myapi")

logger = get_logger(__name__)

@app.get("/health")
@log_entry_exit
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}
```

### Django Integration

```python
# settings.py
from EALogger import set_default_app_name, set_default_log_dir
import os

set_default_app_name("myproject")
set_default_log_dir(os.path.join(BASE_DIR, "logs"))

# views.py
from EALogger import get_logger, log_performance
logger = get_logger(__name__)

@log_performance(threshold_ms=500)
def my_view(request):
    logger.info("View accessed", extra={"user": request.user.username})
    return render(request, "template.html")
```

## Requirements

- **Python**: >=3.9
- **Dependencies**: None (stdlib only)
- **Optional**: `orjson>=3.11.0` for faster JSON operations

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Links

- **GitHub**: https://github.com/hasanmasudnet/EALogger
- **Issues**: https://github.com/hasanmasudnet/EALogger/issues
- **Documentation**: Coming soon

## Changelog

### Version 0.2.0

**New Features:**
- ✨ Async decorator support (`log_entry_exit_async`, `log_performance_async`)
- 🎨 Colored console output
- 🔄 Automatic log rotation
- 🔍 Fast log search utilities (`LogSearcher`)
- ⚡ orjson integration for better performance
- 📊 Performance tracking decorators
- 🎯 Enhanced context injection

**Improvements:**
- Better JSON formatting with comprehensive fields
- Improved error handling
- More flexible configuration options
- Cleaner package structure

**Compatibility:**
- Backward compatible with v0.1.x API
- `username` parameter deprecated (use `context` instead)

### Version 0.1.6

- Initial release with basic logging functionality
