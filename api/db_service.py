"""
Database Service Layer
Service functions for database operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

try:
    from api.db_models import User, Task
    from api.auth import get_password_hash, verify_password
except ImportError:
    from db_models import User, Task
    from auth import get_password_hash, verify_password


class UserService:
    """User database service"""
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username (case-insensitive)"""
        result = await db.execute(
            select(User).where(User.username.ilike(username))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email (case-insensitive)"""
        if not email:
            return None
        result = await db.execute(
            select(User).where(User.email.ilike(email))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        password: str,
        email: Optional[str] = None,
        role: str = "user"
    ) -> User:
        """Create a new user"""
        # Check if user exists
        existing = await UserService.get_user_by_username(db, username)
        if existing:
            raise ValueError(f"Username '{username}' already exists")
        
        # Password is already truncated in get_password_hash, but ensure it's not too long
        # Bcrypt has 72-byte limit
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        hashed_password = await get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def verify_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Verify user credentials"""
        user = await UserService.get_user_by_username(db, username)
        if not user or not user.is_active:
            return None
        
        if await verify_password(password, user.hashed_password):
            return user
        return None
    
    @staticmethod
    async def list_users(db: AsyncSession, active_only: bool = True) -> List[User]:
        """List all users"""
        query = select(User)
        if active_only:
            query = query.where(User.is_active == True)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """Update user"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        allowed_fields = ["email", "role", "is_active", "hashed_password"]
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user


class TaskService:
    """Task database service"""
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        user_id: int,
        file_name: str,
        file_path: str,
        file_type: str,
        task_id: Optional[str] = None,
        status: str = "pending",
        progress: int = 0,
        message: str = "Task queued",
        **options
    ) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            task_id=task_id or str(uuid.uuid4()),
            status=status,
            progress=progress,
            message=message,
            **options
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: str) -> Optional[Task]:
        """Get task by task_id"""
        result = await db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_all_tasks(db: AsyncSession, limit: int = 50) -> List[Task]:
        """List all tasks across all users (admin only)"""
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.user))
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_tasks(
        db: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> List[Task]:
        """Get tasks for a user"""
        result = await db.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: str,
        **kwargs
    ) -> Optional[Task]:
        """Update task"""
        task = await TaskService.get_task_by_id(db, task_id)
        if not task:
            return None
        
        allowed_fields = [
            "status", "progress", "message", "error",
            "result", "output_files", "completed_at"
        ]
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(task, key, value)
        
        if kwargs.get("status") == "completed" and not task.completed_at:
            task.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: str) -> bool:
        """Delete a task"""
        task = await TaskService.get_task_by_id(db, task_id)
        if not task:
            return False
        
        await db.delete(task)
        await db.commit()
        return True

