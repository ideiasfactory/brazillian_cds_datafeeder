#!/usr/bin/env python3
"""Script to start the FastAPI server."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from config import settings


def main():
    """Start the FastAPI server."""
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )


if __name__ == "__main__":
    main()
