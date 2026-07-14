from waitress import serve
from app import create_app
import socket

print("正在创建应用...")
app = create_app("development")
print("应用创建成功！")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "无法获取"

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 50)
    print("服务器启动信息:")
    print(f"  - 本地访问: http://127.0.0.1:8080")
    print("=" * 50)
    print("服务器正在运行，按 Ctrl+C 停止")
    print()

    serve(app, host="0.0.0.0", port=5000)