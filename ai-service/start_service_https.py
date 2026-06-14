#!/usr/bin/env python3
"""
启动服务脚本 - 支持HTTPS
"""

import os
import sys
import subprocess
import time

def check_database():
    """检查数据库表结构"""
    print("检查数据库表结构...")
    try:
        result = subprocess.run(
            [sys.executable, "fix_database.py"],
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        )
        print(result.stdout)
        if result.stderr:
            print(f"数据库检查错误: {result.stderr}")
        return True
    except Exception as e:
        print(f"数据库检查失败: {e}")
        return False

def check_redis():
    """检查 Redis 服务"""
    print("检查 Redis 服务...")
    try:
        result = subprocess.run(
            [sys.executable, "check_redis.py"],
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        )
        print(result.stdout)
        if result.stderr:
            print(f"Redis 检查错误: {result.stderr}")
        return "Redis 服务可用" in result.stdout
    except Exception as e:
        print(f"Redis 检查失败: {e}")
        return False

def check_ssl_certs():
    """检查SSL证书"""
    print("检查SSL证书...")
    from app.core.ssl_config import get_https_config

    try:
        https_config = get_https_config()

        if not https_config.enabled:
            print("HTTPS 未启用，使用HTTP模式")
            return True

        if https_config.is_valid():
            print(f"✓ SSL证书有效")
            print(f"  证书文件: {https_config.cert_file}")
            print(f"  私钥文件: {https_config.key_file}")
            if https_config.verify_client:
                print(f"  客户端验证: 已启用")
            return True
        else:
            print("✗ SSL证书无效或缺失")
            print("请运行以下命令生成证书:")
            print("  python scripts/ssl_cert_manager.py generate --domain localhost")
            return False

    except Exception as e:
        print(f"SSL证书检查失败: {e}")
        return False

def start_service():
    """启动服务"""
    print("启动 FastAPI 服务...")

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "config",
            os.path.join(os.path.dirname(__file__), "app", "core", "config.py")
        )
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        from app.core.ssl_config import get_https_config
        https_config = get_https_config()

        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.core.app:app",
            "--host", config.HOST,
            "--port", str(config.PORT),
            "--log-level", "info"
        ]

        if https_config.enabled and https_config.is_valid():
            print("[OK] 启用HTTPS模式")
            ssl_config = https_config.get_ssl_config()
            if ssl_config:
                cmd.extend([
                    "--ssl-certfile", ssl_config["certfile"],
                    "--ssl-keyfile", ssl_config["keyfile"]
                ])
                if "ca_certs" in ssl_config:
                    cmd.extend(["--ssl-ca-certs", ssl_config["ca_certs"]])

        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        print("服务启动中...")
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                print(line.strip())

        return True

    except Exception as e:
        print(f"服务启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 40)
    print("启动 AI 服务 (支持HTTPS)")
    print("=" * 40)

    if not check_database():
        print("数据库检查失败，服务可能无法正常运行！")

    redis_available = check_redis()
    if not redis_available:
        print("[WARN] Redis 服务不可用，系统将使用内存缓存")

    if not check_ssl_certs():
        print("[WARN] SSL证书检查失败，HTTPS将不可用")

    print("=" * 40)
    print("开始启动服务...")
    print("=" * 40)

    start_service()

if __name__ == "__main__":
    main()
