# 导出所有API路由，便于在主应用中导入
from api.auth import router as auth_router
from api.recognition import router as recognition_router
from api.favorites import router as favorites_router
from api.knowledge import router as knowledge_router
from api.ai import router as ai_router

__all__ = [
    "auth_router",
    "recognition_router",
    "favorites_router",
    "knowledge_router",
    "ai_router"
]