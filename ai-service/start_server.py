"""后端服务器启动脚本 - 自包含，不依赖外部命令"""
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.getcwd()
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print(f"工作目录: {BASE_DIR}")
print(f"Python: {sys.executable}")

# 验证关键模块
try:
    import fastapi
    print(f"FastAPI: {fastapi.__version__}")
except ImportError as e:
    print(f"[ERROR] fastapi 未安装: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"uvicorn: {uvicorn.__version__}")
except ImportError as e:
    print(f"[ERROR] uvicorn 未安装: {e}")
    sys.exit(1)

# 导入并验证 app
try:
    from app.core.app import app
    print(f"[OK] app 导入成功, 路由数量: {len(app.routes)}")
except Exception as e:
    print(f"[ERROR] app 导入失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 打印路由预览
paths = []
for r in app.routes:
    try:
        p = getattr(r, 'path', None)
        if p and p not in paths:
            paths.append(p)
    except Exception:
        pass
print(f"路由路径预览 (前30个): {sorted(paths)[:30]}")

# 启动服务器
print("\n=== 启动服务器: http://0.0.0.0:8000 ===")
try:
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        timeout_keep_alive=30,
    )
except KeyboardInterrupt:
    print("\n服务器已停止 (Ctrl+C)")
except Exception as e:
    print(f"[ERROR] 服务器运行失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
