import os
import sys
import subprocess
from pathlib import Path

# 设置工作目录
work_dir = Path(__file__).parent
os.chdir(work_dir)

python_exe = work_dir / "venv" / "Scripts" / "python.exe"
server_script = work_dir / "run_server.py"
log_file = work_dir / "server_output.log"

# 启动后端服务器，将输出重定向到文件
with open(log_file, "w", encoding="utf-8") as log:
    log.write(f"Starting server at: {work_dir}\n")
    log.write(f"Python: {python_exe}\n")
    log.write(f"Server script: {server_script}\n")
    log.flush()
    
    process = subprocess.Popen(
        [str(python_exe), str(server_script)],
        cwd=str(work_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # 实时写入日志
    for line in process.stdout:
        log.write(line)
        log.flush()
        print(line, end="")
    
    process.wait()
    log.write(f"Server exited with code: {process.returncode}\n")

print("Server launcher done.")
