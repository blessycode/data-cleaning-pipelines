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
    
    uvicorn.run(
        "api.main:app" if Path("api").exists() else "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

