"""
Background Task Processing
Async task execution for long-running pipeline operations
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_cleaning_pipeline.pipe import clean_data

try:
    from api.config import settings
    from api.database import AsyncSessionLocal
    from api.db_service import TaskService
    from api.utils import convert_numpy_types
except ImportError:
    from config import settings
    from database import AsyncSessionLocal
    from db_service import TaskService
    from utils import convert_numpy_types


async def process_pipeline_task(
    task_id: str,
    file_path: str,
    file_type: str,
    profile_data: bool,
    include_visuals: bool,
    apply_cleaning: bool,
    enable_feature_suggestions: bool,
    validate_final_data: bool,
    export_formats: List[str]
):
    """
    Process pipeline task in background
    
    Updates database with progress and results
    """
    async def update_task_in_db(**kwargs):
        async with AsyncSessionLocal() as db:
            await TaskService.update_task(db, task_id, **kwargs)

    try:
        # Update status to running
        await update_task_in_db(status="running", progress=10, message="Loading data...")
        
        # Run pipeline (this is CPU-bound, so we run it in executor)
        loop = asyncio.get_event_loop()
        
        # Create output directory for this task
        task_output_dir = Path(settings.OUTPUT_DIR) / task_id
        task_output_dir.mkdir(parents=True, exist_ok=True)
        
        await update_task_in_db(progress=20, message="Initializing ML Engine...")
        
        # We'll split the work or just simulate the status updates if it's one big call
        # Since clean_data is a single call, we'll keep it simple but refine the message
        
        await update_task_in_db(progress=30, message="Synthesizing Data Schema...")

        # Run pipeline in thread pool to avoid blocking
        result = await loop.run_in_executor(
            None,
            _run_pipeline_sync,
            file_path,
            file_type,
            profile_data,
            include_visuals,
            apply_cleaning,
            enable_feature_suggestions,
            validate_final_data,
            export_formats,
            str(task_output_dir)
        )
        
        await update_task_in_db(progress=90, message="Finalizing Standardized Outputs...")
        
        cleaned_df, reports, output_files = result
        
        # Update task with results
        await update_task_in_db(
            status="completed",
            progress=100,
            message="Pipeline completed successfully",
            result=convert_numpy_types({
                "shape": {
                    "rows": int(len(cleaned_df)) if cleaned_df is not None else 0,
                    "columns": int(len(cleaned_df.columns)) if cleaned_df is not None else 0
                },
                "summary": {
                    "cleaning": reports.get("cleaning", {}).get("overall_improvement", {}),
                    "profiling": reports.get("profiling", {}).get("summary", {}),
                    "features": reports.get("feature_engineering", {}).get("summary", {}),
                    "validation": reports.get("final_validation", {}).get("summary", {})
                },
                "visuals": [Path(p).name for p in output_files.get("visualizations", [])],
                "reports_generated": len(reports),
                "output_files": len(output_files.get("exports", []))
            }),
            output_files=output_files.get("exports", [])
        )
        
        # Cleanup uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
    except Exception as e:
        await update_task_in_db(
            status="failed",
            progress=0,
            message=f"Pipeline failed: {str(e)}",
            error=str(e)
        )


def _run_pipeline_sync(
    file_path: str,
    file_type: str,
    profile_data: bool,
    include_visuals: bool,
    apply_cleaning: bool,
    enable_feature_suggestions: bool,
    validate_final_data: bool,
    export_formats: List[str],
    output_dir: str
) -> tuple:
    """
    Synchronous pipeline execution
    Called from async context via executor
    """
    return clean_data(
        source=file_path,
        file_type=file_type,
        profile_data=profile_data,
        include_visuals=include_visuals,
        apply_cleaning=apply_cleaning,
        enable_feature_suggestions=enable_feature_suggestions,
        validate_final_data=validate_final_data,
        export_formats=export_formats,
        save_output=True,
        output_dir=output_dir
    )

