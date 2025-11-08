"""Vercel serverless function entry point for FastAPI."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.api.main import app

# Vercel expects a variable named 'app'
# This is the ASGI application that Vercel will run
handler = app
