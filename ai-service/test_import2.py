import sys
import traceback
import io

log_buffer = []

def log(msg):
    log_buffer.append(msg)

log("Start test")

try:
    log("Importing os and dotenv...")
    import os
    import dotenv
    dotenv.load_dotenv()
    log("Dotenv loaded")
    
    log("Importing app...")
    from app.core.app import app
    log("SUCCESS: app imported")
    log(f"Number of routes: {len(app.routes)}")
    
    log("\nRoutes (first 30):")
    for route in app.routes[:30]:
        methods = getattr(route, 'methods', set())
        path = getattr(route, 'path', str(route))
        log(f"  {sorted(methods) if methods else 'GET'} {path}")
    
    log("\n\nLooking for specific routes:")
    for route in app.routes:
        path = getattr(route, 'path', str(route))
        if '/policies' in path or '/metrics' in path or '/user' in path or '/auth' in path:
            methods = getattr(route, 'methods', set())
            log(f"  {sorted(methods) if methods else 'GET'} {path}")
    
    log("\nDone")
except Exception as e:
    log(f"ERROR: {e}")
    log(traceback.format_exc())

with open("test_import_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log_buffer))
