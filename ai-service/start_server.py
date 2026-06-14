import os
import sys
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))

cmd = [sys.executable, "-m", "uvicorn", "app.core.app:app", "--host", "0.0.0.0", "--port", "8000"]
print(f"启动命令: {cmd}")

try:
    subprocess.run(cmd, check=True)
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)
