#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""服务器部署打包脚本"""

import zipfile
import os
import datetime

def create_deployment_package():
    """创建服务器部署压缩包"""
    source_dir = "ai-service"
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"ai-service-deploy-{timestamp}.zip"

    # 需要排除的模式
    exclude_patterns = [
        '.db',           # 数据库文件
        '__pycache__',   # Python缓存
        '.pyc',          # 编译文件
        '.pyo',          # 编译文件
        '.git',          # Git仓库
        '.gitignore',    # Git配置
        '*.md',          # 文档文件（可选）
        'tests/',        # 测试目录
        'test_*.py',     # 测试文件
        'logs/',         # 日志目录（服务器上会有新的）
        '.pytest_cache/',# pytest缓存
        '*.log',         # 日志文件
        '.env',          # 环境变量文件（需要单独配置）
        'node_modules/', # Node模块
        'pack_*.py',     # 打包脚本
        '.vscode/',      # VSCode配置
        '.idea/',        # IDE配置
    ]

    # 必须包含的核心文件
    required_files = [
        'app/',
        'openclaw/',
        'routers/',
        'services/',
        'plugins/',
        'skills/',
        'tools/',
        'requirements.txt',
        'main.py',
        'config.py',
        '.env.example',
    ]

    files_added = []
    total_size = 0

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]

            for file in files:
                # 跳过测试文件
                if file.startswith('test_') and file.endswith('.py'):
                    continue

                # 跳过其他需要排除的文件
                if any(file.endswith(p.replace('*', '')) for p in exclude_patterns if '*' in p):
                    continue
                if any(p in file for p in exclude_patterns if '/' not in p and '*' not in p):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zf.write(file_path, arcname)
                file_size = os.path.getsize(file_path)
                total_size += file_size
                files_added.append((arcname, file_size))

    print(f"\n{'='*60}")
    print(f"  服务器部署包创建完成")
    print(f"{'='*60}")
    print(f"文件名: {zip_filename}")
    print(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
    print(f"文件数量: {len(files_added)}")
    print(f"\n包含目录:")
    for item in required_files:
        print(f"  - {item}")

    print(f"\n{'='*60}")
    print(f"部署说明:")
    print(f"1. 解压到服务器目录")
    print(f"2. 配置 .env 文件（参考 .env.example）")
    print(f"3. 安装依赖: pip install -r requirements.txt")
    print(f"4. 运行服务: python main.py")
    print(f"{'='*60}")

if __name__ == "__main__":
    create_deployment_package()
