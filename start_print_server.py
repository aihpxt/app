# -*- coding: utf-8 -*-
import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    print("=" * 60)
    print("🖨️ 未央中学招生简章 - 印刷版生成器")
    print("=" * 60)
    
    # 检查HTML文件
    html_files = {
        '传统经典风格': 'weiyang-brochure-traditional-optimized.html',
        '科技未来风格': 'weiyang-brochure-futuristic-optimized.html',
        '自然生态风格': 'weiyang-brochure-ecological-optimized.html',
    }
    
    print(f"\n📁 可用的招生简章:")
    for style, filename in html_files.items():
        if os.path.exists(filename):
            print(f"   ✅ {style}")
        else:
            print(f"   ❌ {style} (文件不存在)")
    
    print(f"\n🚀 正在启动本地服务器...")
    print(f"📊 端口: {PORT}")
    
    # 切换到项目目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            server_url = f"http://localhost:{PORT}"
            
            print(f"\n✅ 服务器启动成功！")
            print(f"\n🌐 访问地址:")
            for style, filename in html_files.items():
                if os.path.exists(filename):
                    print(f"   {style}: {server_url}/{filename}")
            
            print(f"\n📋 生成印刷级PDF的步骤:")
            print("   1. 在Chrome浏览器中打开上方的任一地址")
            print("   2. 按 Ctrl+P (Windows) 或 Cmd+P (Mac)")
            print("   3. 在打印对话框中选择:")
            print(f"      - 目标打印机: 另存为PDF")
            print(f"      - 纸张尺寸: A3")
            print(f"      - 缩放: 实际大小 (100%)")
            print(f"      - 背景图形: 勾选")
            print("   4. 点击'保存'按钮")
            
            print(f"\n💡 提示:")
            print("   - 建议使用Chrome浏览器以获得最佳效果")
            print("   - 三种风格可以分别生成PDF进行比较")
            print(f"   - 按 Ctrl+C 停止服务器")
            
            print(f"\n{'=' * 60}")
            
            # 尝试自动打开浏览器
            try:
                first_file = next(f for f in html_files.values() if os.path.exists(f))
                webbrowser.open(f"{server_url}/{first_file}")
                print(f"\n🌐 已自动打开浏览器: {first_file}")
            except:
                pass
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动服务器失败: {e}")

if __name__ == '__main__':
    main()
