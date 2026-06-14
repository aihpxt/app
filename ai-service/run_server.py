import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"Starting from: {os.getcwd()}")
print(f"Python: {sys.executable}")

import uvicorn

if __name__ == "__main__":
    print("Starting uvicorn on 0.0.0.0:8000...")
    uvicorn.run(
        "app.core.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
