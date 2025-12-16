"""
Configuration Settings
Environment-based configuration with security defaults
"""

import os
from typing import List, Optional

# Try to import BaseSettings from pydantic-settings (Pydantic v2)
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        # Fallback for older pydantic versions
        from pydantic import BaseSettings
    except ImportError:
        # If both fail, create a simple BaseSettings class
        from pydantic import BaseModel
        class BaseSettings(BaseModel):
            class Config:
                env_file = ".env"
                case_sensitive = True


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Authentication (in production, use database)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".xlsx", ".xls", ".parquet"]
    UPLOAD_DIR: str = "uploads"
    
    # Output
    OUTPUT_DIR: str = "data_pipeline_output"
    CLEANUP_AFTER_HOURS: int = 24
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "data_cleaning_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        None  # Will be constructed from components if not provided
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

