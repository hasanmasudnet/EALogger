# EALogger Installation Guide

## Quick Install

### From Local Build

```bash
# Navigate to EALogger directory
cd D:\Projects\PG.AI\EALogger

# Install the wheel package
pip install dist/EALogger-0.2.0-py3-none-any.whl

# Or with fast JSON support (recommended)
pip install dist/EALogger-0.2.0-py3-none-any.whl[fast]
```

### From Source (Development)

```bash
cd D:\Projects\PG.AI\EALogger
pip install -e ".[dev,fast]"
```

### From GitHub (Future)

```bash
pip install git+https://github.com/hasanmasudnet/EALogger.git
```

---

## Test Installation

```python
from EALogger import get_logger, set_default_app_name

set_default_app_name("test")
logger = get_logger(__name__)
logger.info("EALogger installed successfully!")
```

---

## Verify orjson is Working (Optional)

```python
try:
    import orjson
    print("✅ orjson installed - using fast JSON")
except ImportError:
    print("⚠️  orjson not found - using standard library (slower)")
    print("   Install with: pip install orjson")
```

---

## Next Steps

1. Read `README.md` for usage examples
2. Check `ANALYSIS.md` for technical details
3. See `SUMMARY.md` for what's new in v0.2.0

Happy Logging! 🎉

