#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
import os

src = r'E:\aiphxt-app\ai-service\data\unified_school_data.db'
dst = r'E:\aiphxt-app\backend\src\main\resources\data\aiphxt.db'

print(f"源文件: {src}")
print(f"源文件存在: {os.path.exists(src)}")

# 确保目标目录存在
dst_dir = os.path.dirname(dst)
os.makedirs(dst_dir, exist_ok=True)
print(f"目标目录: {dst_dir}")
print(f"目标目录存在: {os.path.exists(dst_dir)}")

# 如果目标文件存在，先删除
if os.path.exists(dst):
    try:
        os.remove(dst)
        print("已删除旧的目标文件")
    except Exception as e:
        print(f"删除旧文件失败: {e}")
        # 尝试重命名
        bak = dst + '.old'
        try:
            os.rename(dst, bak)
            print(f"已将旧文件重命名为: {bak}")
        except Exception as e2:
            print(f"重命名也失败: {e2}")

# 复制文件
try:
    shutil.copy2(src, dst)
    print(f"复制成功: {dst}")

    # 验证
    if os.path.exists(dst):
        src_size = os.path.getsize(src)
        dst_size = os.path.getsize(dst)
        print(f"源文件大小: {src_size}")
        print(f"目标文件大小: {dst_size}")
        if src_size == dst_size:
            print("✅ 文件验证通过")
        else:
            print("⚠️ 文件大小不匹配")
except Exception as e:
    print(f"复制失败: {e}")
