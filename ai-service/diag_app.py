import sys
import os

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

OUTPUT_FILE = r"D:\aiphxt-app\ai-service\diag.txt"

def save(data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(data + "\n")
    print(data)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("")

save("Step 1: Starting diagnostic...")

try:
    save("Step 2: Testing app.core.config import...")
    from app.core.config import APP_NAME, APP_VERSION
    save(f"  Config OK: {APP_NAME} v{APP_VERSION}")
except Exception as e:
    save(f"  Config FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())

try:
    save("Step 3: Testing app.core.app module import...")
    import app.core.app
    save("  app.core.app import OK")
except Exception as e:
    save(f"  app.core.app import FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())

try:
    save("Step 4: Testing create_app function call...")
    from app.core.app import create_app
    app = create_app()
    save(f"  create_app OK, routes={len(app.routes)}")
except Exception as e:
    save(f"  create_app FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())

save("Step 5: Diagnostic complete!")
