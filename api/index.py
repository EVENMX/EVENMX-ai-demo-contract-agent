"""
Vercel serverless function entry point for FastAPI app.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app

# Vercel expects the app to be exported as 'handler' for Python serverless functions
# FastAPI app is ASGI-compatible, so we can export it directly
handler = app

