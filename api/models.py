"""
Pydantic Models for API Request/Response
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PipelineRequest(BaseModel):
    """Request model for pipeline execution"""
    file_type: str = Field(default="csv", description="File type: csv, excel, etc.")
    profile_data: bool = Field(default=True, description="Generate data profiling")
    include_visuals: bool = Field(default=False, description="Include visualizations")
    apply_cleaning: bool = Field(default=True, description="Apply data cleaning")
    enable_feature_suggestions: bool = Field(default=False, description="Enable feature engineering suggestions")
    validate_final_data: bool = Field(default=True, description="Perform final validation")
    export_formats: Optional[List[str]] = Field(default=None, description="Export formats")


class PipelineResponse(BaseModel):
    """Response model for pipeline execution"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status: pending, running, completed, failed")
    message: str = Field(..., description="Status message")


class TaskStatus(BaseModel):
    """Task status model"""
    task_id: str
    status: str = Field(..., description="pending, running, completed, failed")
    created_at: str
    file_name: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    output_files: Optional[List[str]] = None


class ValidationRequest(BaseModel):
    """Request model for data validation"""
    data_schema: Optional[Dict[str, Any]] = Field(None, alias="schema", description="Data schema for validation")
    constraints: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True  # Allow both "schema" and "data_schema"


class ValidationResponse(BaseModel):
    """Response model for data validation"""
    status: str = Field(..., description="PASS, FAIL, or WARNING")
    score: int = Field(..., ge=0, le=100, description="Validation score")
    total_issues: int = Field(..., ge=0)
    critical_issues: List[str] = []
    warnings: List[str] = []
    report: Dict[str, Any] = {}


class FeatureEngineeringRequest(BaseModel):
    """Request model for feature engineering suggestions"""
    target_column: Optional[str] = None


class FeatureEngineeringResponse(BaseModel):
    """Response model for feature engineering suggestions"""
    total_suggestions: int = Field(..., ge=0)
    suggestions_by_category: Dict[str, int] = {}
    priority_features: List[Dict[str, Any]] = []
    quick_wins: List[str] = []
    full_report: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    email: Optional[str] = Field(None, description="Email address")
    confirm_password: Optional[str] = Field(None, description="Password confirmation")


class RegisterResponse(BaseModel):
    """Response model for user registration"""
    message: str = Field(..., description="Success message")
    username: str = Field(..., description="Registered username")
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Request model for login (alternative to form data)"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Response model for login"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    username: str = Field(..., description="Authenticated username")
    role: Optional[str] = Field(None, description="User role")

