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
except ImportError:
    from config import settings


async def process_pipeline_task(
    task_id: str,
    file_path: str,
    file_type: str,
    profile_data: bool,
    include_visuals: bool,
    apply_cleaning: bool,
    enable_feature_suggestions: bool,
    validate_final_data: bool,
    export_formats: List[str],
    task_storage: Dict[str, Any]
):
    """
    Process pipeline task in background
    
    Updates task_storage with progress and results
    """
    try:
        # Update status to running
        task_storage[task_id]["status"] = "running"
        task_storage[task_id]["progress"] = 10
        task_storage[task_id]["message"] = "Loading data..."
        
        # Run pipeline (this is CPU-bound, so we run it in executor)
        loop = asyncio.get_event_loop()
        
        # Create output directory for this task
        task_output_dir = Path(settings.OUTPUT_DIR) / task_id
        task_output_dir.mkdir(parents=True, exist_ok=True)
        
        task_storage[task_id]["progress"] = 20
        task_storage[task_id]["message"] = "Running pipeline..."
        
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
        
        cleaned_df, reports, output_files = result
        
        # Update task with results
        task_storage[task_id]["status"] = "completed"
        task_storage[task_id]["progress"] = 100
        task_storage[task_id]["message"] = "Pipeline completed successfully"
        task_storage[task_id]["result"] = {
            "shape": {
                "rows": int(len(cleaned_df)) if cleaned_df is not None else 0,
                "columns": int(len(cleaned_df.columns)) if cleaned_df is not None else 0
            },
            "reports_generated": len(reports),
            "output_files": len(output_files.get("exports", []))
        }
        task_storage[task_id]["output_files"] = output_files.get("exports", [])
        
        # Cleanup uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
    except Exception as e:
        task_storage[task_id]["status"] = "failed"
        task_storage[task_id]["progress"] = 0
        task_storage[task_id]["message"] = f"Pipeline failed: {str(e)}"
        task_storage[task_id]["error"] = str(e)


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

