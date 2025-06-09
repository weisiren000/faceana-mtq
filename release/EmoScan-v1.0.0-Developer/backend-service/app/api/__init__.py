"""
API路由初始化
"""

from fastapi import APIRouter
from .v1 import router as v1_router

router = APIRouter()

# 注册v1路由
router.include_router(v1_router) 