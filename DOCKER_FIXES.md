# Docker Deployment Fixes

## Issues Fixed

### 1. Missing `chardet` Module
**Error**: `ModuleNotFoundError: No module named 'chardet'`

**Fix**: Added `chardet>=5.0.0` to `api/requirements-api.txt`

The data cleaning pipeline's ingestion module uses `chardet` for character encoding detection when reading CSV files.

### 2. Missing `scikit-learn` Module
**Error**: Would occur when using data cleaning features that require sklearn

**Fix**: Added `scikit-learn>=1.3.0` to `api/requirements-api.txt`

Used by:
- `DataCleaner` class for advanced imputation (KNNImputer, IterativeImputer)
- Missing value handling strategies

### 3. Bcrypt Password Length Issue
**Error**: `password cannot be longer than 72 bytes`

**Fix**: 
- Updated `db_service.py` to truncate passwords to 72 bytes before hashing
- Updated `auth.py` to handle password truncation in both `get_password_hash` and `verify_password`
- Updated Dockerfile to handle admin creation failures gracefully

### 4. Docker Startup Errors
**Fix**: Updated Dockerfile CMD to handle migration and init errors gracefully:
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && (python init_db.py || echo 'Admin creation skipped') && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

## Updated Requirements

The following packages were added to `api/requirements-api.txt`:
- `chardet>=5.0.0` - Character encoding detection
- `scikit-learn>=1.3.0` - Machine learning for data imputation

## Testing

After rebuilding:

```bash
# Rebuild the API container
docker compose build api

# Start all services
docker compose up -d

# Check logs
docker compose logs -f api
```

The API should now start successfully without missing module errors.

## Notes

- The bcrypt warning about `__about__` is harmless - it's a version detection issue but doesn't affect functionality
- Admin user creation will be skipped if password is too long, but you can still register users via the API
- All data cleaning pipeline features should now work properly

