"""
Vercel serverless function entry point for FastAPI app.
"""
import os
import sys
from pathlib import Path

try:
    # Add parent directory to path so we can import app modules
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variable to help modules find project root
    os.environ["PROJECT_ROOT"] = str(project_root)
    
    # Debug: Print directory structure
    print(f"=== DEBUG: Project root: {project_root}", file=sys.stderr)
    print(f"=== DEBUG: Current working directory: {Path.cwd()}", file=sys.stderr)
    print(f"=== DEBUG: Files in project root:", file=sys.stderr)
    for item in project_root.iterdir():
        print(f"  - {item.name}", file=sys.stderr)
    
    app_dir = project_root / "app"
    if app_dir.exists():
        print(f"=== DEBUG: Files in app/:", file=sys.stderr)
        for item in app_dir.iterdir():
            print(f"  - {item.name}", file=sys.stderr)
        
        data_dir = app_dir / "data"
        if data_dir.exists():
            print(f"=== DEBUG: Files in app/data/:", file=sys.stderr)
            for item in data_dir.iterdir():
                print(f"  - {item.name}", file=sys.stderr)
    else:
        print(f"=== DEBUG: app/ directory NOT FOUND", file=sys.stderr)
    
    templates_dir = project_root / "templates"
    if templates_dir.exists():
        print(f"=== DEBUG: Files in templates/:", file=sys.stderr)
        for item in templates_dir.iterdir():
            print(f"  - {item.name}", file=sys.stderr)
    else:
        print(f"=== DEBUG: templates/ directory NOT FOUND", file=sys.stderr)
    
    print(f"=== DEBUG: Attempting to import app.main", file=sys.stderr)
    from app.main import app
    print(f"=== DEBUG: Successfully imported app", file=sys.stderr)
    
    # Vercel expects the app to be exported as 'handler' for Python serverless functions
    # FastAPI app is ASGI-compatible, so we can export it directly
    handler = app
    
except Exception as e:
    import traceback
    print(f"=== FATAL ERROR during initialization:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

