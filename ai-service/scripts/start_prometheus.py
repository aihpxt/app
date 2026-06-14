#!/usr/bin/env python3
"""
Prometheus监控启动脚本
"""

import os
import sys
import subprocess
import time

def check_prometheus():
    """检查Prometheus是否安装"""
    try:
        result = subprocess.run(
            ["prometheus", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Prometheus已安装")
            return True
    except FileNotFoundError:
        pass

    print("✗ Prometheus未安装")
    print("\n请安装Prometheus:")
    print("  macOS: brew install prometheus")
    print("  Linux: sudo apt-get install prometheus")
    print("  Windows: 下载 prometheus-*.windows-amd64.tar.gz")
    print("\n或使用Docker:")
    print("  docker run -d --name prometheus -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus")

    return False

def start_prometheus():
    """启动Prometheus"""
    print("启动Prometheus...")

    config_file = os.path.join(os.path.dirname(__file__), "prometheus.yml")

    try:
        process = subprocess.Popen(
            ["prometheus", "--config.file", config_file],
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        print("Prometheus启动中...")
        time.sleep(3)

        if process.poll() is None:
            print("✓ Prometheus已启动")
            print("访问 http://localhost:9090 查看监控界面")
            return True
        else:
            print("✗ Prometheus启动失败")
            return False

    except Exception as e:
        print(f"启动失败: {e}")
        return False

def main():
    print("=" * 50)
    print("Prometheus 监控配置")
    print("=" * 50)

    if check_prometheus():
        start_prometheus()
    else:
        print("\n请先安装Prometheus")

if __name__ == "__main__":
    main()
