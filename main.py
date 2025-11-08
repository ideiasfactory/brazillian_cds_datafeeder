#!/usr/bin/env python3
"""Main entry point for local development."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.api.main import app

# For running with uvicorn: uvicorn main:app --reload
# Or simply: python scripts/start_api.py

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
