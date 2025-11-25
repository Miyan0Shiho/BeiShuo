from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from api import auth_router, recognition_router, favorites_router, knowledge_router, ai_router

# 数据库初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("初始化数据库...")
    # 简单的内存数据库实现，用于演示
    print("数据库初始化完成")
    yield
    # 关闭时
    print("关闭应用...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(recognition_router, prefix="/api/v1/recognition", tags=["碑文识别"])
app.include_router(favorites_router, prefix="/api/v1/favorites", tags=["收藏管理"])
app.include_router(knowledge_router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI功能"])

# 健康检查路由根路径
@app.get("/")
def read_root():
    return {
        "message": "碑说API服务正在运行",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.DEBUG else False
    )