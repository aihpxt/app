import sys
import os
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Starting server initialization...")
print(f"Working directory: {os.getcwd()}")
print(f"Python: {sys.executable}")
print()

try:
    from app.core.app import app
    print("App imported successfully")
    print(f"App title: {app.title}")
    print(f"Number of routes: {len(app.routes)}")
    print()
    print("Routes:")
    for route in app.routes:
        methods = getattr(route, 'methods', set())
        path = getattr(route, 'path', '')
        if 'user' in path or 'register' in path or 'login' in path:
            print(f"  {list(methods)} {path}")
    print()
    import uvicorn
    print("Starting uvicorn server on 0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    print()
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
