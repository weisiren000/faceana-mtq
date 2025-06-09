"""
EmoScan后端主应用
FastAPI服务器，提供情绪分析API
"""

import logging
import os
from pathlib import Path
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .services.emotion_analyzer import EmotionAnalyzer
from .services.comfyui_service import ComfyUIService
from .models.emotion import AnalysisResponse, BatchAnalysisResponse
from .models.comfyui import GenerationRequest, GenerationResponse
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

# 设置输出目录
output_dir = Path(__file__).parent.parent.parent.parent / "output"
if not output_dir.exists():
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"已创建输出目录: {output_dir}")
    except Exception as e:
        logger.error(f"创建输出目录失败: {e}")

# 挂载输出目录为静态文件服务
app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
logger.info(f"已挂载输出目录为静态文件服务: {output_dir} -> /output")

# 挂载ComfyUI输出目录为静态文件服务
comfyui_output_dir = Path("C:/sw/ComfyUI/output")
if comfyui_output_dir.exists():
    app.mount("/comfyui-output", StaticFiles(directory=str(comfyui_output_dir)), name="comfyui_output")
    logger.info(f"已挂载ComfyUI输出目录为静态文件服务: {comfyui_output_dir} -> /comfyui-output")
else:
    logger.warning(f"ComfyUI输出目录不存在: {comfyui_output_dir}")

# 初始化情绪分析器
emotion_analyzer = EmotionAnalyzer()

# 初始化ComfyUI服务
comfyui_service = ComfyUIService()

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
        if not file.content_type or not file.content_type.startswith("image/"):
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


@app.post("/api/v1/analyze-and-generate")
async def analyze_and_generate_image(file: UploadFile = File(...), generate_image: bool = True):
    """
    分析图像情绪并生成对应的艺术图像

    Args:
        file: 上传的图像文件
        generate_image: 是否生成图像（默认True）

    Returns:
        dict: 包含情绪分析结果和图像生成结果
    """
    try:
        # 1. 验证文件类型
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="文件必须是图像格式")

        # 2. 读取图像数据
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="图像文件为空")

        # 3. 进行情绪分析
        analysis_result = await emotion_analyzer.analyze_image(image_data)

        if not analysis_result.success:
            return {
                "success": False,
                "emotion_analysis": analysis_result,
                "image_generation": None,
                "error_message": "情绪分析失败"
            }

        # 4. 如果需要生成图像
        generation_result = None
        if generate_image:
            try:
                # 找到主导情绪
                emotion_data_list = analysis_result.emotion_data
                if emotion_data_list:
                    dominant_emotion_data = max(emotion_data_list, key=lambda x: x.percentage)
                    dominant_emotion = dominant_emotion_data.emotion.lower()

                    # 映射情绪名称
                    emotion_mapping = {
                        "happy": "happy", "sad": "sad", "angry": "angry",
                        "surprised": "surprised", "neutral": "neutral",
                        "disgusted": "disgusted", "fearful": "fearful"
                    }

                    standard_emotion = emotion_mapping.get(dominant_emotion, "neutral")

                    # 创建生成请求
                    generation_request = GenerationRequest(emotion=standard_emotion)

                    # 生成图像
                    generation_result = await comfyui_service.generate_image(generation_request)

                    logger.info(f"情绪分析和图像生成完成: 主导情绪={standard_emotion}, 生成成功={generation_result.success}")

            except Exception as gen_error:
                logger.warning(f"图像生成失败，但情绪分析成功: {gen_error}")
                generation_result = GenerationResponse(
                    success=False,
                    error_message=f"图像生成失败: {str(gen_error)}"
                )

        return {
            "success": True,
            "emotion_analysis": analysis_result,
            "image_generation": generation_result,
            "message": "分析完成" + ("，图像生成成功" if generation_result and generation_result.success else "")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析和生成图像时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)