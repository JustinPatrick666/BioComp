from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import dicom, tasks, ai
from app.config import settings
import uvicorn

app = FastAPI(
    title="医学影像分析系统",
    version=settings.VERSION,
    description="肿瘤影像分析后端API"
)

# 配置跨域中间件
origins = [
    "*"
   # "http://localhost:5173",  # 前端运行的地址
    # else 可能d的地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(dicom.router, prefix="/api/v1/dicom")
app.include_router(tasks.router, prefix="/api/v1/tasks")
app.include_router(ai.router, prefix="/api/v1/ai")

@app.on_event("startup")
async def startup():
    settings.setup()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )