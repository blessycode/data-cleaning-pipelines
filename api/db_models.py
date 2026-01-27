"""
Database Models
SQLAlchemy models for PostgreSQL
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

try:
    from api.database import Base
except ImportError:
    from database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    plan = Column(String(20), default="free", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class Task(Base):
    """Task model for pipeline jobs"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(20), nullable=True)
    progress = Column(Integer, default=0, nullable=False)
    message = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    output_files = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Pipeline options
    profile_data = Column(Boolean, default=True)
    include_visuals = Column(Boolean, default=False)
    apply_cleaning = Column(Boolean, default=True)
    enable_feature_suggestions = Column(Boolean, default=False)
    validate_final_data = Column(Boolean, default=True)
    export_formats = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(task_id='{self.task_id}', status='{self.status}')>"

