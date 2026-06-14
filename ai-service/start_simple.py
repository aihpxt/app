import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.core.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
