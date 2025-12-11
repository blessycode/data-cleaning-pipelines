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
    schema: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


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

