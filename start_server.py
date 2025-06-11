import uvicorn
from pathlib import Path
import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

# 现在导入模块
from app.config import settings

# 创建上传目录
settings.setup()

if __name__ == "__main__":
    print(f"Starting server at http://localhost:{settings.PORT}")
    print(f"Backend path: {backend_dir}")
    os.chdir(backend_dir)  # 切换工作目录
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
