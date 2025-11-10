"""
Vercel serverless function entry point for FastAPI app.
Files are copied into api/ directory during build via buildCommand in vercel.json
"""
import os
import sys
from pathlib import Path

try:
    # In Vercel, app/, templates/, and static/ are copied into api/ during build
    # So we set the api directory as the project root
    api_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(api_dir))
    
    # Set environment variable to help modules find files
    os.environ["PROJECT_ROOT"] = str(api_dir)
    
    # Debug: Print directory structure
    print(f"=== DEBUG: API directory: {api_dir}", file=sys.stderr)
    print(f"=== DEBUG: Current working directory: {Path.cwd()}", file=sys.stderr)
    print(f"=== DEBUG: Files in api directory:", file=sys.stderr)
    for item in api_dir.iterdir():
        print(f"  - {item.name}", file=sys.stderr)
    
    app_dir = api_dir / "app"
    if app_dir.exists():
        print(f"=== DEBUG: Files in api/app/:", file=sys.stderr)
        for item in app_dir.iterdir():
            print(f"  - {item.name}", file=sys.stderr)
        
        data_dir = app_dir / "data"
        if data_dir.exists():
            print(f"=== DEBUG: Files in api/app/data/:", file=sys.stderr)
            for item in data_dir.iterdir():
                print(f"  - {item.name}", file=sys.stderr)
    else:
        print(f"=== DEBUG: api/app/ directory NOT FOUND", file=sys.stderr)
    
    templates_dir = api_dir / "templates"
    if templates_dir.exists():
        print(f"=== DEBUG: Files in api/templates/:", file=sys.stderr)
        for item in templates_dir.iterdir():
            print(f"  - {item.name}", file=sys.stderr)
    else:
        print(f"=== DEBUG: api/templates/ directory NOT FOUND", file=sys.stderr)
    
    print(f"=== DEBUG: Attempting to import app.main", file=sys.stderr)
    from app.main import app
    print(f"=== DEBUG: Successfully imported app", file=sys.stderr)
    
    # Vercel expects the app to be exported as 'handler' for Python serverless functions
    handler = app
    
except Exception as e:
    import traceback
    print(f"=== FATAL ERROR during initialization:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

