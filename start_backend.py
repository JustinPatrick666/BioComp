#!/usr/bin/env python3
"""
启动后端服务的脚本
"""
import subprocess
import sys
import os

def start_backend():
    """启动后端服务"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    print("正在启动后端服务...")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        # 启动FastAPI服务
        cmd = [sys.executable, "app/main.py"]
        print(f"执行命令: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # 输出启动信息
        for line in process.stdout:
            print(line.strip())
            
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        process.terminate()
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    start_backend()
