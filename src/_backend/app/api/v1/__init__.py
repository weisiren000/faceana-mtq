"""
API v1路由初始化
"""

from fastapi import APIRouter
from .generation import router as generation_router

router = APIRouter()

# 注册路由
router.include_router(generation_router) 