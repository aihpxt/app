import sys
import os
from pathlib import Path

# 显式用绝对路径
script_path = Path("d:/aiphxt-app/ai-service")
os.chdir(script_path)
sys.path.insert(0, str(script_path))

output_file = Path("d:/aiphxt-app/ai-service/app_import_test.txt")

def log(msg):
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# 清空文件
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Testing app import at {script_path}\n")

log(f"Python: {sys.executable}")
log(f"CWD: {os.getcwd()}")

try:
    log("Loading .env...")
    from dotenv import load_dotenv
    env_file = script_path / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        log(f"Loaded .env from {env_file}")
    else:
        log(f"No .env file at {env_file}")
except Exception as e:
    log(f"ERROR loading dotenv: {e}")

log("SECRET_KEY: " + os.environ.get("SECRET_KEY", "<NOT SET>")[:10] + "..." if os.environ.get("SECRET_KEY") else "SECRET_KEY: <NOT SET>")
log("DATABASE_URL: " + os.environ.get("DATABASE_URL", "<NOT SET>"))

try:
    log("Importing app.core.app...")
    from app.core.app import app
    log("SUCCESS: app imported!")
    log(f"Number of routes: {len(app.routes)}")
    log("Key route paths:")
    for route in app.routes:
        path = getattr(route, 'path', str(route))
        methods = getattr(route, 'methods', set())
        log(f"  {sorted(list(methods)) if methods else 'GET'} {path}")
    log("\nDONE - App loaded successfully!")
except Exception as e:
    log(f"ERROR: {e}")
    import traceback
    tb = traceback.format_exc()
    log(tb)
    print(tb)
