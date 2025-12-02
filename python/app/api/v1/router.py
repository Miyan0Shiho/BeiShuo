from fastapi import APIRouter
from app.api.v1 import auth, inscription, knowledge, ai, upload, recognition, favorites, image_proxy, admin

router = APIRouter()

router.include_router(auth.router)
router.include_router(upload.router)
router.include_router(recognition.router)
router.include_router(inscription.router)  # 保留原有接口用于内部使用
router.include_router(ai.router)
router.include_router(knowledge.router)
router.include_router(favorites.router)
router.include_router(image_proxy.router)
router.include_router(admin.router)

