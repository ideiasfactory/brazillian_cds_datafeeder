"""Vercel serverless function entry point for FastAPI.

Vercel uses @vercel/python runtime which automatically handles ASGI apps.
The 'app' variable is exposed for Vercel to run with its internal ASGI server.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.api.main import app

# Vercel expects a variable named 'app' or 'handler'
# This is the ASGI application that Vercel will run
# No need for uvicorn here - Vercel handles it internally
app = app
