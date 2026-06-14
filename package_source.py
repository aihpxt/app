#!/usr/bin/env python3
"""
打包源文件脚本 - 准备上传服务器
"""
import os
import zipfile
from datetime import datetime
import shutil

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 打包输出目录
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "releases")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 生成版本号
VERSION = datetime.now().strftime("%Y%m%d_%H%M%S")
ZIP_FILENAME = f"aiphxt-app_v{VERSION}.zip"
ZIP_PATH = os.path.join(OUTPUT_DIR, ZIP_FILENAME)

# 需要排除的文件和目录
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".git",
    ".gitignore",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "*.log",
    "logs/",
    ".pytest_cache",
    ".vscode",
    ".trae",
    "*.db",
    "*.sqlite",
    "*.zip",
    "releases/",
    "data/*.db",
    "*.pyc",
    "*.pyo",
    "__pycache__/",
    ".env",
    "*.key",
    "*.crt",
    "*.pem",
    ".DS_Store",
    "Thumbs.db",
    "tmp/",
    "temp/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".coverage",
    "*.coverage",
    "htmlcov/",
]

def should_exclude(path):
    """检查路径是否需要排除"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith("/"):
            # 目录排除
            if pattern[:-1] in path.split(os.sep):
                return True
        elif "*" in pattern:
            # 通配符匹配
            import fnmatch
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        else:
            # 精确匹配
            if pattern in path:
                return True
    return False

def create_package():
    """创建源码包"""
    print(f"🚀 开始打包源文件...")
    print(f"📦 版本: {VERSION}")
    print(f"📁 输出: {ZIP_PATH}")
    print()

    # 创建zip文件
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 遍历项目目录
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # 跳过排除的目录
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)
                
                # 检查是否需要排除
                if should_exclude(file_path):
                    continue

                # 获取相对路径
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                
                # 添加到zip
                zipf.write(file_path, rel_path)
                print(f"✓ 添加: {rel_path}")

    # 获取文件大小
    file_size = os.path.getsize(ZIP_PATH)
    size_mb = file_size / (1024 * 1024)

    print()
    print("=" * 50)
    print(f"✅ 打包完成!")
    print(f"📦 文件: {ZIP_FILENAME}")
    print(f"📊 大小: {size_mb:.2f} MB")
    print(f"📁 位置: {ZIP_PATH}")
    print("=" * 50)
    print()
    print("📋 上传说明:")
    print("  1. 将此zip文件上传到服务器")
    print("  2. 解压到目标目录")
    print("  3. 按照SYSTEM_README.md进行部署")
    print()

    return ZIP_PATH

def create_deployment_guide():
    """创建快速部署指南"""
    guide_content = f"""========================================
  快速部署指南
  版本: {VERSION}
========================================

📋 部署前检查清单:
[ ] 服务器已安装 Python 3.9+
[ ] 服务器已安装 Node.js 18+
[ ] 已准备好域名或服务器IP
[ ] 已配置好防火墙规则

🚀 部署步骤:

1. 上传并解压源码包
   $ unzip aiphxt-app_v{VERSION}.zip -d /opt/aiphxt-app
   $ cd /opt/aiphxt-app

2. 配置后端
   $ cd ai-service
   $ python -m venv .venv
   $ source .venv/bin/activate  # Linux/Mac
   # 或: .venv\\Scripts\\activate  # Windows
   $ pip install -r requirements.txt
   $ cp .env.example .env
   $ # 编辑 .env 填入真实配置

3. 配置前端
   $ cd ../frontend
   $ npm install
   $ npm run build

4. 启动服务
   # 后端:
   $ cd ../ai-service
   $ python start_service.py
   
   # 前端: 使用Nginx或其他web服务器托管 dist/ 目录

5. 验证部署
   # 检查健康状态
   $ curl http://localhost:8001/health

📚 详细文档:
- SYSTEM_README.md - 系统完整文档
- DEPLOYMENT.md - 详细部署指南
- OPS_DEPLOYMENT_GUIDE.md - 运维指南

⚠️  安全提醒:
- 务必修改默认密码和密钥
- 生产环境启用HTTPS
- 定期备份数据库
"""

    guide_path = os.path.join(OUTPUT_DIR, f"DEPLOYMENT_GUIDE_v{VERSION}.txt")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print(f"📄 部署指南已生成: {guide_path}")
    return guide_path

if __name__ == "__main__":
    try:
        zip_path = create_package()
        guide_path = create_deployment_guide()
        print("🎉 所有文件准备就绪，可以上传服务器了!")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
