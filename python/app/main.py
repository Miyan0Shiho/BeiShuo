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
from app.services.temp_file_cleaner import temp_file_cleaner

# 设置日志
setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(f"{settings.app_name} 启动成功")
    
    # 启动临时文件清理服务
    try:
        await temp_file_cleaner.start()
        logger.info("临时文件清理服务启动成功")
    except Exception as e:
        logger.error(f"临时文件清理服务启动失败: {e}")
    
    yield
    
    # 关闭时
    logger.info(f"{settings.app_name} 关闭")
    
    # 停止临时文件清理服务
    try:
        await temp_file_cleaner.stop()
        logger.info("临时文件清理服务已停止")
    except Exception as e:
        logger.error(f"临时文件清理服务停止失败: {e}")

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

# 静态文件挂载（用于前端裁剪原图：/uploads/*）
app.mount("/uploads", StaticFiles(directory=settings.file_upload_path), name="uploads")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

