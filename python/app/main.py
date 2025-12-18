from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import settings
from app.api.v1.router import router as v1_router
from app.core.exceptions import BusinessException, UnauthorizedException
from app.common.response import Result
from app.common.result_code import ResultCode
from app.utils.logger import setup_logger, logger
from app.client.mysql_client import mysql_client

# 设置日志
setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(f"{settings.app_name} 启动中...")
    # 连接数据库
    try:
        await mysql_client.connect()
        logger.info(f"数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    
    logger.info(f"{settings.app_name} 启动成功")
    yield
    # 关闭时
    logger.info(f"{settings.app_name} 关闭中...")
    # 断开数据库连接
    try:
        await mysql_client.disconnect()
        logger.info(f"数据库连接已断开")
    except Exception as e:
        logger.error(f"数据库断开连接失败: {e}")
    
    logger.info(f"{settings.app_name} 已关闭")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allowed_methods,
    allow_headers=settings.cors_allowed_headers,
    max_age=settings.cors_max_age,
)

# 全局异常处理
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """处理业务异常"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=Result.fail_with_code(exc.code, exc.message).model_dump()
    )

@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    """处理未授权异常"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=Result.fail(ResultCode.UNAUTHORIZED, exc.message).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理其他异常"""
    logger.exception(f"系统异常: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Result.fail(ResultCode.INTERNAL_SERVER_ERROR, "系统异常，请稍后重试").model_dump()
    )

# 注册路由
app.include_router(v1_router, prefix="/api/v1")

# 自定义支持CORS的静态文件服务
class CORSStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        # 允许所有源访问静态资源，这对Canvas处理图片至关重要
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

# 静态文件挂载（用于前端裁剪原图：/uploads/*）
import os
# 创建uploads目录（如果不存在）
uploads_path = os.path.abspath(settings.file_upload_path)
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", CORSStaticFiles(directory=uploads_path), name="uploads")

# 静态文件挂载（用于临时OSS图片：/temp_oss_images/*）
# 创建临时目录（如果不存在）
temp_oss_images_path = os.path.join(os.getcwd(), "temp_oss_images")
os.makedirs(temp_oss_images_path, exist_ok=True)
app.mount("/temp_oss_images", CORSStaticFiles(directory=temp_oss_images_path), name="temp_oss_images")

@app.get("/")
async def root():
    """根路径处理"""
    return {
        "message": f"{settings.app_name} API服务",
        "version": settings.app_version,
        "health": "ok",
        "api_prefix": "/api/v1",
        "endpoints": {
            "health": "/health",
            "api": "/api/v1",
            "upload": "/api/v1/upload",
            "recognition": "/api/v1/recognition",
            "auth": "/api/v1/auth",
            "ai": "/api/v1/ai"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}

# 添加定时清理临时OSS图片文件的任务
import asyncio
import time

async def cleanup_temp_oss_images():
    """定时清理过期的临时OSS图片文件"""
    while True:
        try:
            logger.info("开始清理临时OSS图片文件...")
            
            temp_oss_images_path = os.path.join(os.getcwd(), "temp_oss_images")
            if os.path.exists(temp_oss_images_path):
                current_time = time.time()
                # 删除24小时前的文件
                cutoff_time = current_time - 24 * 3600
                
                for filename in os.listdir(temp_oss_images_path):
                    file_path = os.path.join(temp_oss_images_path, filename)
                    if os.path.isfile(file_path):
                        file_mtime = os.path.getmtime(file_path)
                        if file_mtime < cutoff_time:
                            os.remove(file_path)
                            logger.info(f"删除过期临时文件: {file_path}")
            
            logger.info("临时OSS图片文件清理完成")
        except Exception as e:
            logger.error(f"清理临时OSS图片文件失败: {e}")
        
        # 每6小时执行一次清理
        await asyncio.sleep(6 * 3600)

# 启动定时清理任务
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 启动定时清理任务
    asyncio.create_task(cleanup_temp_oss_images())
    logger.info("定时清理临时OSS图片任务已启动")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

