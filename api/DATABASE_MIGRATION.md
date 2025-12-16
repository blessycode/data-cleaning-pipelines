# Database Migration Guide

## Overview

The API has been set up with PostgreSQL database support. The current `main.py` still uses the JSON-based `user_storage`. This guide shows how to migrate to the database.

## Current State

- ✅ Database models created (`db_models.py`)
- ✅ Database service layer created (`db_service.py`)
- ✅ Database connection configured (`database.py`)
- ✅ Alembic migrations set up
- ⚠️ `main.py` still uses `user_storage` (needs update)

## Migration Steps

### 1. Update main.py imports

Replace:
```python
from api.user_storage import user_storage
```

With:
```python
from api.database import get_db
from api.db_service import UserService, TaskService
```

### 2. Update registration endpoint

**Before:**
```python
if user_storage.user_exists(request.username):
    raise HTTPException(...)
user_data = user_storage.create_user(...)
```

**After:**
```python
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await UserService.get_user_by_username(db, request.username)
    if existing:
        raise HTTPException(...)
    user = await UserService.create_user(db, ...)
```

### 3. Update login endpoint

**Before:**
```python
if user_storage.verify_user(username, password):
    user = user_storage.get_user(username)
```

**After:**
```python
async def login(..., db: AsyncSession = Depends(get_db)):
    user = await UserService.verify_user(db, username, password)
    if user:
        # Use user object
```

### 4. Update task endpoints

Replace in-memory `task_storage` with database:

**Before:**
```python
task_storage[task_id] = {...}
```

**After:**
```python
task = await TaskService.create_task(
    db=db,
    user_id=current_user_id,
    file_name=file.filename,
    ...
)
```

### 5. Update startup event

Add database initialization:

```python
@app.on_event("startup")
async def startup_event():
    await init_db()
    # Create default admin if needed
    async with AsyncSessionLocal() as db:
        admin = await UserService.get_user_by_username(db, settings.ADMIN_USERNAME)
        if not admin:
            await UserService.create_user(...)
```

## Quick Migration Script

A complete updated `main.py` using the database is available. The key changes:

1. All endpoints use `db: AsyncSession = Depends(get_db)`
2. User operations use `UserService`
3. Task operations use `TaskService`
4. Remove `user_storage` imports and usage
5. Remove in-memory `task_storage` dict

## Testing After Migration

1. **Test registration**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test123","confirm_password":"test123"}'
   ```

2. **Test login**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -d "username=test&password=test123"
   ```

3. **Check database**
   ```bash
   psql -U postgres -d data_cleaning_db
   SELECT * FROM users;
   SELECT * FROM tasks;
   ```

## Rollback

If issues occur, you can temporarily keep using `user_storage` by:
1. Not importing database dependencies
2. Keeping `user_storage` imports
3. The JSON file will continue to work

## Notes

- Database is production-ready
- Service layer provides clean abstraction
- All operations are async for better performance
- Migrations handle schema changes automatically

