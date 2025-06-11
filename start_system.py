"""
启动完整医学影像分析系统
包括：模拟AI服务(5001) + 后端API(8000) + 前端(5175)
"""
import subprocess
import time
import sys
import os
from pathlib import Path

def start_service(name, command, cwd=None, port=None):
    """启动服务"""
    print(f"启动 {name}...")
    try:
        if cwd:
            process = subprocess.Popen(
                command, 
                shell=True, 
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        time.sleep(2)  # 等待服务启动
        
        if process.poll() is None:  # 进程仍在运行
            print(f"✅ {name} 启动成功 (PID: {process.pid})")
            if port:
                print(f"   访问地址: http://localhost:{port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {name} 启动失败")
            print(f"错误信息: {stderr.decode('utf-8', errors='ignore')}")
            return None
    except Exception as e:
        print(f"❌ 启动 {name} 时出错: {str(e)}")
        return None

def main():
    print("🏥 医学影像肿瘤分析系统启动器")
    print("=" * 50)
    
    # 获取项目根目录
    root_dir = Path(__file__).parent
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    
    processes = []
    
    try:
        # 1. 启动模拟AI服务
        print("\n1️⃣ 启动模拟AI服务...")
        ai_process = start_service(
            "模拟AI服务",
            "python mock_ai_service.py",
            cwd=str(root_dir),
            port=5002
        )
        if ai_process:
            processes.append(("模拟AI服务", ai_process))
        
        time.sleep(3)
        
        # 2. 启动后端API服务
        print("\n2️⃣ 启动后端API服务...")
        backend_process = start_service(
            "后端API服务",
            "python run_backend.py",
            cwd=str(backend_dir),
            port=8000
        )
        if backend_process:
            processes.append(("后端API服务", backend_process))
        
        time.sleep(3)
        
        # 3. 启动前端开发服务器
        print("\n3️⃣ 启动前端开发服务器...")
        frontend_process = start_service(
            "前端开发服务器",
            "npm run dev",
            cwd=str(frontend_dir),
            port=5173
        )
        if frontend_process:
            processes.append(("前端开发服务器", frontend_process))
        print("\n" + "=" * 50)
        print("🎉 系统启动完成!")
        
        print("\n📋 服务状态:")
        print("   • 模拟AI服务:    http://localhost:5002")
        print("   • 后端API:      http://localhost:8000")
        print("   • 前端界面:      http://localhost:5173")
        print("   • API文档:      http://localhost:8000/docs")
        
        print("\n🔧 测试链接:")
        print("   • AI健康检查:    http://localhost:5002/health")
        print("   • 后端健康检查:   http://localhost:8000/api/v1/ai/health")
        
        print("\n💡 使用说明:")
        print("   1. 访问前端界面上传DICOM文件")
        print("   2. 点击AI分析按钮进行肿瘤检测")
        print("   3. 查看分析结果和下载报告")
        
        print("\n⚠️  按 Ctrl+C 停止所有服务")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止所有服务...")
            
    except Exception as e:
        print(f"\n❌ 系统启动失败: {str(e)}")
    
    finally:
        # 停止所有进程
        for name, process in processes:
            try:
                print(f"停止 {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️ 强制停止 {name}...")
                process.kill()
            except Exception as e:
                print(f"❌ 停止 {name} 时出错: {str(e)}")
        
        print("\n👋 系统已停止")

if __name__ == "__main__":
    main()
