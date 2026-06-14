"""后端服务器 - 带超时和文件日志"""
import sys
import os
import time
import threading
import signal

os.chdir(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.getcwd()
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

log_path = os.path.join(BASE_DIR, "server_runtime.log")
log_file = open(log_path, "w", encoding="utf-8")

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    log_file.write(line + "\n")
    log_file.flush()
    print(line)

log(f"=== 服务器启动 PID={os.getpid()} ===")
log(f"工作目录: {BASE_DIR}")

# 1. 测试核心依赖
log("\n--- 检查依赖 ---")
deps_ok = True
try:
    import fastapi; log(f"[OK] fastapi {fastapi.__version__}")
    import uvicorn; log(f"[OK] uvicorn {uvicorn.__version__}")
    import sqlite3; log(f"[OK] sqlite3")
except ImportError as e:
    log(f"[FAIL] {e}")
    deps_ok = False

if not deps_ok:
    log("依赖不满足，退出")
    log_file.close()
    sys.exit(1)

# 2. 导入 app
log("\n--- 创建 app ---")
try:
    from app.core.app import app
    paths = sorted(set([getattr(r, 'path', None) for r in app.routes if getattr(r, 'path', None)]))
    log(f"[OK] app 创建成功, {len(paths)} 个路径")
    log(f"[OK] 主要路径: {paths[:50]}")
except Exception as e:
    log(f"[FAIL] app 创建失败: {type(e).__name__}: {e}")
    import traceback
    log(traceback.format_exc())
    log_file.close()
    sys.exit(1)

# 3. 启动 uvicorn
log("\n--- 启动 uvicorn 服务器: http://0.0.0.0:8000 ---")
log(f"日志文件: {log_path}")

try:
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    # 注册信号处理器
    stop_flag = threading.Event()
    
    def _handler(signum, frame):
        log(f"收到信号 {signum}，正在退出...")
        stop_flag.set()
        server.should_exit = True
    
    try:
        signal.signal(signal.SIGINT, _handler)
        signal.signal(signal.SIGTERM, _handler)
    except Exception:
        pass
    
    log("服务器启动中...")
    log("按 Ctrl+C 或关闭窗口以停止服务器")
    log("\n=== 服务器就绪 ===")
    log("可用端点示例:")
    log("  GET  http://localhost:8000/")
    log("  GET  http://localhost:8000/api/schools")
    log("  GET  http://localhost:8000/api/policies")
    log("  GET  http://localhost:8000/api/health")
    log("  POST http://localhost:8000/api/agent/chat")
    log("  POST http://localhost:8000/api/user/register")
    log("")
    
    server.run()
    
except KeyboardInterrupt:
    log("\n[OK] 用户中断，已退出")
except Exception as e:
    log(f"[ERROR] 服务器运行出错: {type(e).__name__}: {e}")
    import traceback
    log(traceback.format_exc())
finally:
    log("\n=== 服务器已停止 ===")
    log_file.close()
