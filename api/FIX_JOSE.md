# Fix for jose/python-jose Import Error

## Problem

If you see this error when starting the server:
```
File ".../jose.py", line 546
    print decrypt(deserialize_compact(jwt), {'k':key},
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
```

This means the **wrong** `jose` package is installed. The `jose` package is for Python 2, but we need `python-jose` for Python 3.

## Solution

### Quick Fix (Recommended)

Run the setup script:
```bash
cd api
python setup.py
```

Or on Linux/Mac:
```bash
cd api
bash setup.sh
```

### Manual Fix

1. **Uninstall the wrong package:**
   ```bash
   pip uninstall -y jose
   ```

2. **Install the correct package:**
   ```bash
   pip install python-jose[cryptography]>=3.3.0
   ```

3. **Verify it works:**
   ```bash
   python -c "from jose import jwt; print('OK')"
   ```

4. **Install all requirements:**
   ```bash
   pip install -r requirements-api.txt
   ```

## Why This Happens

- The `jose` package (without "python-") is an old Python 2 package
- The `python-jose` package is the Python 3 compatible version
- Both can be installed at the same time, but Python will import the wrong one
- The import statement `from jose import ...` is correct for both, but only `python-jose` works with Python 3

## Prevention

Always use `requirements-api.txt` which specifies `python-jose[cryptography]` instead of `jose`.

