"""
Utility Functions for API
File handling, validation, and helper functions
"""

import os
import shutil
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from fastapi import UploadFile, HTTPException

try:
    from api.config import settings
except ImportError:
    from config import settings


async def save_uploaded_file(file: UploadFile, task_id: str) -> str:
    """
    Save uploaded file to disk
    
    Returns:
        file_path: Path to saved file
    """
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Generate file path
    file_extension = Path(file.filename).suffix
    file_path = upload_dir / f"{task_id}{file_extension}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)} MB"
            )
        
        buffer.write(content)
    
    return str(file_path)


def validate_file_type(filename: str, file_type: str) -> bool:
    """Validate file type matches expected type"""
    from api.config import settings
    
    if not filename:
        return False
    
    file_ext = Path(filename).suffix.lower()
    
    # Check if extension is allowed
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        return False
    
    # Check if extension matches file_type
    type_mapping = {
        "csv": ".csv",
        "excel": [".xlsx", ".xls"],
        "parquet": ".parquet"
    }
    
    expected_exts = type_mapping.get(file_type.lower(), [file_ext])
    if isinstance(expected_exts, str):
        expected_exts = [expected_exts]
    
    return file_ext in expected_exts


def get_task_status(task_id: str, task_storage: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get task status from storage"""
    return task_storage.get(task_id)


async def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """Cleanup old files in background"""
    while True:
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            directory_path = Path(directory)
            
            if not directory_path.exists():
                await asyncio.sleep(3600)  # Check every hour
                continue
            
            for item in directory_path.iterdir():
                if item.is_file():
                    file_time = datetime.fromtimestamp(item.stat().st_mtime)
                    if file_time < cutoff_time:
                        item.unlink()
                elif item.is_dir():
                    dir_time = datetime.fromtimestamp(item.stat().st_mtime)
                    if dir_time < cutoff_time:
                        shutil.rmtree(item)
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            print(f"Error in cleanup: {str(e)}")
            await asyncio.sleep(3600)


def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    """Load dataframe from file"""
    if file_type.lower() == "csv":
        return pd.read_csv(file_path)
    elif file_type.lower() in ["excel", "xlsx", "xls"]:
        return pd.read_excel(file_path)
    elif file_type.lower() == "parquet":
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

