# Installation Guide

## Quick Fix for pydantic-settings Error

If you see this error:
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

### Solution:

```bash
# Install the missing package
pip install pydantic-settings

# Or install all API requirements
pip install -r requirements-api.txt
```

### Verify Installation:

```bash
python -c "from pydantic_settings import BaseSettings; print('OK')"
```

If this works, you're good to go!

## Full Installation

```bash
# 1. Install all dependencies
pip install -r requirements-api.txt

# 2. Verify installation
python -c "import fastapi, uvicorn, pydantic_settings; print('All packages installed!')"
```

## Troubleshooting

### If pip install fails:
- Make sure you're in the correct virtual environment
- Try: `python -m pip install pydantic-settings`
- On Windows: `py -m pip install pydantic-settings`

### If still having issues:
- Check Python version: `python --version` (should be 3.8+)
- Upgrade pip: `python -m pip install --upgrade pip`
- Install manually: `pip install pydantic-settings==2.1.0`

