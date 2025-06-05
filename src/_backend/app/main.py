"""
EmoScan后端主应用
FastAPI服务器，提供情绪分析API
"""

import logging
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .services.emotion_analyzer import EmotionAnalyzer
from .models.emotion import AnalysisResponse, BatchAnalysisResponse
from .api import router as api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="EmoScan API",
    description="情感分析API服务",
    version="1.0.0"
)

# 配置CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，包括ComfyUI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化情绪分析器
emotion_analyzer = EmotionAnalyzer()

# 注册API路由
app.include_router(api_router)

@app.get("/")
async def root():
    """健康检查端点"""
    return {"message": "EmoScan API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "service": "EmoScan API",
        "version": "1.0.0",
        "timestamp": "2025-05-29"
    }


@app.post("/api/v1/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    分析上传图像中的情绪
    
    Args:
        file: 上传的图像文件
        
    Returns:
        AnalysisResponse: 情绪分析结果
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="文件必须是图像格式")
        
        # 读取图像数据
        image_data = await file.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="图像文件为空")
        
        # 分析情绪
        result = await emotion_analyzer.analyze_image(image_data)
        
        logger.info(f"情绪分析完成: {file.filename}, 成功: {result.success}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析图像时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/v1/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch_images(files: List[UploadFile] = File(...)):
    """
    批量分析多张图像中的情绪，使用裁判员AI给出最终判断

    Args:
        files: 上传的图像文件列表（最多5张）

    Returns:
        BatchAnalysisResponse: 批量情绪分析结果
    """
    try:
        # 验证文件数量
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="至少需要上传一张图像")

        if len(files) > 5:
            raise HTTPException(status_code=400, detail="最多只能上传5张图像")

        images_data = []

        # 处理每个文件
        for i, file in enumerate(files):
            # 验证文件类型
            if file.content_type and not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"文件{i+1}必须是图像格式")

            # 读取图像数据
            image_data = await file.read()

            if len(image_data) == 0:
                raise HTTPException(status_code=400, detail=f"图像文件{i+1}为空")

            images_data.append(image_data)

        # 批量分析情绪
        result = await emotion_analyzer.analyze_batch_images(images_data)

        logger.info(f"批量情绪分析完成: {len(files)}张图像, 成功: {result.success}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量分析图像时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)