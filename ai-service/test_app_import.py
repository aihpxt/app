import sys
import os
from pathlib import Path

work_dir = Path(__file__).parent
os.chdir(work_dir)
sys.path.insert(0, str(work_dir))

output_file = work_dir / "app_import_test.txt"

def log(msg):
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# 清空文件
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Testing app import at {work_dir}\n")

try:
    log("Loading .env...")
    from dotenv import load_dotenv
    env_file = work_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        log(f"Loaded .env")
    else:
        log("No .env file found")
except Exception as e:
    log(f"ERROR loading dotenv: {e}")

try:
    log("Importing app.core.app...")
    from app.core.app import app
    log("SUCCESS: app imported!")
    log(f"Number of routes: {len(app.routes)}")
    log("First 30 route paths:")
    for route in app.routes[:30]:
        path = getattr(route, 'path', str(route))
        methods = getattr(route, 'methods', set())
        log(f"  {sorted(methods) if methods else 'GET'} {path}")
    
    log("\nLooking for specific routes...")
    for route in app.routes:
        path = getattr(route, 'path', str(route))
        if 'policy' in path or 'user' in path or 'metrics' in path or 'auth' in path or 'vitals' in path:
            methods = getattr(route, 'methods', set())
            log(f"  FOUND: {sorted(methods) if methods else 'GET'} {path}")
    
    log("\nDONE - App loaded successfully!")
except Exception as e:
    log(f"ERROR: {e}")
    import traceback
    log(traceback.format_exc())

print("Test complete. See app_import_test.txt")
