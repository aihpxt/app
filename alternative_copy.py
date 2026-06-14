import os

src = r"C:\Users\hp\AppData\Local\Temp\unified_school_data_copy.db"

# 尝试多个目标位置
targets = [
    r"e:\aiphxt-app\ai-service\sqlite\data\unified_school_data.db",
    r"e:\aiphxt-app\sqlite\unified_school_data.db",
    r"e:\aiphxt-app\database\unified_school_data.db",
    r"e:\aiphxt-app\data\unified_school_data.db"
]

print(f"源文件: {src}")
print(f"源文件存在: {os.path.exists(src)}")

if os.path.exists(src):
    size = os.path.getsize(src)
    print(f"源文件大小: {size} bytes")
    
    # 尝试每个目标位置
    for target in targets:
        target_dir = os.path.dirname(target)
        try:
            os.makedirs(target_dir, exist_ok=True)
            with open(src, 'rb') as f:
                data = f.read()
            with open(target, 'wb') as f:
                f.write(data)
            print(f"✅ 成功复制到: {target}")
            break
        except Exception as e:
            print(f"❌ 失败 {target}: {e}")