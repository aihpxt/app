import sys
import traceback

with open("test_import_output.txt", "w", encoding="utf-8") as f:
    f.write("Testing app import...\n")
    try:
        from app.core.app import app
        f.write("SUCCESS: app imported\n")
        f.write(f"Number of routes: {len(app.routes)}\n")
        f.write("\nAll routes:\n")
        for route in app.routes:
            methods = getattr(route, 'methods', set())
            path = getattr(route, 'path', str(route))
            f.write(f"  {sorted(methods) if methods else 'GET'} {path}\n")
        f.write("\nDone\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")
        traceback.print_exc(file=f)
        sys.exit(1)
