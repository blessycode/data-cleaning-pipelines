"""
Server Startup Script
Run the FastAPI server with proper configuration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uvicorn
    from api.config import settings
except ImportError:
    # If running from api directory
    import uvicorn
    from config import settings

if __name__ == "__main__":
    print("=" * 70)
    print("  Data Cleaning Pipeline API Server")
    print("=" * 70)
    print(f"  Starting server on {settings.HOST}:{settings.PORT}")
    print(f"  Debug mode: {settings.DEBUG}")
    print(f"  API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 70)
    print()
    
    # Determine the correct app path
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if (parent_dir / "api").exists() and current_dir.name == "api":
        # Running from api directory, parent has api subdirectory
        app_path = "api.main:app"
    elif (current_dir / "main.py").exists():
        # Running from api directory directly
        app_path = "main:app"
    else:
        # Running from project root
        app_path = "api.main:app"
    
    uvicorn.run(
        app_path,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

