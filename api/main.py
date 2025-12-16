"""
FastAPI Backend for Data Cleaning Pipeline
Main application entry point with security and authentication
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from pathlib import Path

try:
    from api.auth import verify_token, create_access_token, get_current_user, get_password_hash
    from api.models import (
        PipelineRequest, PipelineResponse, TaskStatus, 
        ValidationRequest, ValidationResponse,
        FeatureEngineeringRequest, FeatureEngineeringResponse,
        RegisterRequest, RegisterResponse, LoginResponse
    )
    from api.utils import (
        save_uploaded_file, validate_file_type, 
        get_task_status, cleanup_old_files
    )
    from api.tasks import process_pipeline_task
    from api.config import settings
    from api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
    from api.user_storage import user_storage
except ImportError:
    # If running from api directory
    from auth import verify_token, create_access_token, get_current_user, get_password_hash
    from models import (
        PipelineRequest, PipelineResponse, TaskStatus, 
        ValidationRequest, ValidationResponse,
        FeatureEngineeringRequest, FeatureEngineeringResponse,
        RegisterRequest, RegisterResponse, LoginResponse
    )
    from utils import (
        save_uploaded_file, validate_file_type, 
        get_task_status, cleanup_old_files
    )
    from tasks import process_pipeline_task
    from config import settings
    from middleware import RateLimitMiddleware, SecurityHeadersMiddleware
    from user_storage import user_storage

# Initialize FastAPI app
app = FastAPI(
    title="Data Cleaning Pipeline API",
    description="Comprehensive data cleaning and preprocessing API with AI-powered feature engineering",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# Security Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS
    )

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving outputs
output_dir = Path(settings.OUTPUT_DIR)
output_dir.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(output_dir)), name="outputs")

# Database will be used for tasks and users
# Import database dependencies
try:
    from api.database import get_db, init_db, close_db
    from api.db_service import UserService, TaskService
    from api.db_models import User, Task
except ImportError:
    from database import get_db, init_db, close_db
    from db_service import UserService, TaskService
    from db_models import User, Task


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Cleaning Pipeline API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "output_dir_exists": os.path.exists(settings.OUTPUT_DIR)
    }


@app.post("/auth/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Register a new user
    
    Requirements:
    - Username: 3-50 characters
    - Password: Minimum 8 characters
    - Password confirmation must match (if provided)
    """
    # Validate password confirmation if provided
    if request.confirm_password and request.password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Password and confirmation do not match"
        )
    
    # Check if user already exists
    if user_storage.user_exists(request.username):
        raise HTTPException(
            status_code=400,
            detail=f"Username '{request.username}' already exists"
        )
    
    # Validate username format (alphanumeric and underscores)
    if not request.username.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Username can only contain letters, numbers, underscores, and hyphens"
        )
    
    # Hash password
    hashed_password = get_password_hash(request.password)
    
    # Create user
    try:
        user_data = user_storage.create_user(
            username=request.username,
            hashed_password=hashed_password,
            email=request.email,
            role="user"
        )
        
        return RegisterResponse(
            message="User registered successfully",
            username=user_data["username"],
            email=user_data.get("email")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=LoginResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticate user and get access token
    
    Supports both registered users and default admin account
    """
    # Ensure default admin exists (lazy initialization)
    user_storage.ensure_default_admin()
    
    # Try to authenticate with user storage first
    if user_storage.verify_user(username, password):
        user = user_storage.get_user(username)
        token = create_access_token(
            data={
                "sub": user["username"],
                "role": user.get("role", "user")
            }
        )
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            username=user["username"],
            role=user.get("role", "user")
        )
    
    # Fallback to default admin (for backward compatibility)
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        # Create admin user if it doesn't exist yet
        if not user_storage.user_exists(username):
            user_storage.ensure_default_admin()
        
        # Try again after ensuring admin exists
        if user_storage.verify_user(username, password):
            user = user_storage.get_user(username)
            token = create_access_token(
                data={
                    "sub": user["username"],
                    "role": user.get("role", "admin")
                }
            )
            return LoginResponse(
                access_token=token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                username=user["username"],
                role=user.get("role", "admin")
            )
    
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/api/v1/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: str = Form("csv"),
    profile_data: bool = Form(True),
    include_visuals: bool = Form(False),
    apply_cleaning: bool = Form(True),
    enable_feature_suggestions: bool = Form(False),
    validate_final_data: bool = Form(True),
    export_formats: Optional[str] = Form(None),  # JSON string of list
    current_user: str = Depends(get_current_user)
):
    """
    Run complete data cleaning pipeline
    
    Requires authentication
    """
    try:
        # Validate file
        if not validate_file_type(file.filename, file_type):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = await save_uploaded_file(file, task_id)
        
        # Parse export formats
        formats_list = None
        if export_formats:
            try:
                formats_list = json.loads(export_formats)
            except:
                formats_list = export_formats.split(",") if isinstance(export_formats, str) else None
        
        # Create task
        task_storage[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "file_name": file.filename,
            "progress": 0,
            "message": "Task queued"
        }
        
        # Run pipeline in background
        background_tasks.add_task(
            process_pipeline_task,
            task_id=task_id,
            file_path=file_path,
            file_type=file_type,
            profile_data=profile_data,
            include_visuals=include_visuals,
            apply_cleaning=apply_cleaning,
            enable_feature_suggestions=enable_feature_suggestions,
            validate_final_data=validate_final_data,
            export_formats=formats_list or ['csv', 'excel', 'parquet'],
            task_storage=task_storage
        )
        
        return PipelineResponse(
            task_id=task_id,
            status="pending",
            message="Pipeline task started. Use /api/v1/tasks/{task_id} to check status."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting pipeline: {str(e)}")


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status_endpoint(
    task_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get status of a pipeline task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    return TaskStatus(**task)


@app.get("/api/v1/tasks/{task_id}/download")
async def download_task_output(
    task_id: str,
    file_type: str = "csv",
    current_user: str = Depends(get_current_user)
):
    """Download output files from completed task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    # Find output file
    output_dir = Path(settings.OUTPUT_DIR) / task_id
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output files not found")
    
    # Look for file with specified type
    files = list(output_dir.glob(f"*.{file_type}"))
    if not files:
        raise HTTPException(status_code=404, detail=f"No {file_type} file found")
    
    return FileResponse(
        path=files[0],
        filename=files[0].name,
        media_type="application/octet-stream"
    )


@app.post("/api/v1/validate", response_model=ValidationResponse)
async def validate_data_endpoint(
    file: UploadFile = File(...),
    schema: Optional[str] = Form(None, alias="schema"),  # JSON string (accepts "schema" for backward compatibility)
    constraints: Optional[str] = Form(None),  # JSON string
    current_user: str = Depends(get_current_user)
):
    """
    Validate data without running full pipeline
    
    Requires authentication
    """
    try:
        # Save and load file
        temp_file = await save_uploaded_file(file, f"validate_{uuid.uuid4()}")
        
        # Load data
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(temp_file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Parse schema and constraints
        schema_dict = json.loads(schema) if schema else None
        constraints_dict = json.loads(constraints) if constraints else None
        
        # Run validation
        from data_cleaning_pipeline.cleaning.final_validation import validate_data
        
        validation_report = validate_data(
            df=df,
            schema=schema_dict,
            constraints=constraints_dict,
            verbose=False
        )
        
        # Cleanup temp file
        os.remove(temp_file)
        
        summary = validation_report.get("summary", {})
        
        return ValidationResponse(
            status=summary.get("overall_status", "UNKNOWN"),
            score=summary.get("validation_score", 0),
            total_issues=summary.get("total_issues", 0),
            critical_issues=summary.get("critical_issues", []),
            warnings=summary.get("warnings", []),
            report=validation_report
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@app.post("/api/v1/features/suggest", response_model=FeatureEngineeringResponse)
async def suggest_features_endpoint(
    file: UploadFile = File(...),
    target_column: Optional[str] = Form(None),
    current_user: str = Depends(get_current_user)
):
    """
    Get AI-based feature engineering suggestions
    
    Requires authentication
    """
    try:
        # Save and load file
        temp_file = await save_uploaded_file(file, f"features_{uuid.uuid4()}")
        
        # Load data
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(temp_file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Get feature suggestions
        from data_cleaning_pipeline.cleaning.feature_engineering import suggest_features
        
        suggestions = suggest_features(
            df=df,
            target_column=target_column,
            verbose=False
        )
        
        # Cleanup temp file
        os.remove(temp_file)
        
        summary = suggestions.get("summary", {})
        
        return FeatureEngineeringResponse(
            total_suggestions=summary.get("total_suggestions", 0),
            suggestions_by_category=summary.get("by_category", {}),
            priority_features=summary.get("priority_features", []),
            quick_wins=summary.get("quick_wins", []),
            full_report=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature engineering error: {str(e)}")


@app.get("/api/v1/tasks")
async def list_tasks(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """List recent tasks (for current user)"""
    tasks = list(task_storage.values())
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"tasks": tasks[:limit], "total": len(tasks)}


@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a task and its outputs"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Cleanup output files
    output_dir = Path(settings.OUTPUT_DIR) / task_id
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    
    # Remove from storage
    del task_storage[task_id]
    
    return {"message": "Task deleted successfully"}


@app.get("/api/v1/users/me")
async def get_current_user_info(
    current_user: str = Depends(get_current_user)
):
    """Get current user information"""
    user = user_storage.get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user["username"],
        "email": user.get("email"),
        "role": user.get("role", "user"),
        "created_at": user.get("created_at"),
        "is_active": user.get("is_active", True)
    }


@app.get("/api/v1/users")
async def list_users(
    current_user: str = Depends(get_current_user),
    active_only: bool = True
):
    """List all users (admin only)"""
    # Check if user is admin
    user = user_storage.get_user(current_user)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"users": user_storage.list_users(active_only=active_only)}


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    # Create output directory
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Initialize user storage (creates default admin if needed, but lazily)
    # Admin creation is deferred to avoid bcrypt initialization issues at import time
    try:
        user_storage.ensure_default_admin()
    except Exception as e:
        # If admin creation fails, log but don't crash - it will be created on first login
        print(f"Warning: Could not create default admin at startup: {e}")
        print("Admin will be created on first login attempt")
    
    # Cleanup old files
    asyncio.create_task(cleanup_old_files(settings.OUTPUT_DIR, max_age_hours=24))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

