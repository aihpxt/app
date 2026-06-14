#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包源文件脚本"""

import zipfile
import os
import datetime

def create_source_package():
    """创建源代码压缩包"""
    source_dir = "ai-service"
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"ai-service-{timestamp}.zip"

    exclude_patterns = ['.db', '__pycache__', '.pyc', '.pyo', '.git']

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]

            for file in files:
                # 过滤文件
                if any(file.endswith(p) or p in file for p in exclude_patterns):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zf.write(file_path, arcname)
                print(f"添加: {arcname}")

    print(f"\n打包完成: {zip_filename}")
    print(f"文件大小: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    create_source_package()
