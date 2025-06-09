"""
图像生成API路由
基于情绪分析结果调用ComfyUI生成图像
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException

from ...models.comfyui import (
    GenerationRequest, GenerationResponse, ComfyUIStatus, WorkflowInfo
)
from ...services.comfyui_service import ComfyUIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/generation", tags=["图像生成"])

# ComfyUI服务实例
comfyui_service = ComfyUIService()


@router.get("/status", response_model=ComfyUIStatus)
async def get_comfyui_status():
    """
    获取ComfyUI服务状态
    
    Returns:
        ComfyUIStatus: ComfyUI服务状态信息
    """
    try:
        status = await comfyui_service.check_status()
        return status
    except Exception as e:
        logger.error(f"获取ComfyUI状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.get("/workflows", response_model=List[WorkflowInfo])
async def list_workflows():
    """
    列出所有可用的工作流
    
    Returns:
        List[WorkflowInfo]: 工作流信息列表
    """
    try:
        workflows = await comfyui_service.list_workflows()
        return workflows
    except Exception as e:
        logger.error(f"列出工作流失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出工作流失败: {str(e)}")


@router.post("/generate", response_model=GenerationResponse)
async def generate_image(request: GenerationRequest):
    """
    根据情绪生成图像
    
    Args:
        request: 图像生成请求，包含情绪类型和可选参数
        
    Returns:
        GenerationResponse: 图像生成结果
    """
    try:
        # 验证情绪类型
        from ...models.comfyui import validate_emotion
        if not validate_emotion(request.emotion):
            raise HTTPException(
                status_code=400, 
                detail=f"无效的情绪类型: {request.emotion}。支持的情绪: happy, sad, angry, surprised, neutral, disgusted, fearful"
            )
        
        # 生成图像
        result = await comfyui_service.generate_image(request)
        
        if result.success:
            logger.info(f"图像生成成功: 情绪={request.emotion}, 图像数量={len(result.images or [])}")
        else:
            logger.warning(f"图像生成失败: 情绪={request.emotion}, 错误={result.error_message}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"图像生成失败: {str(e)}")


from pydantic import BaseModel

class EmotionAnalysisRequest(BaseModel):
    """基于情绪分析结果生成图像的请求模型"""
    emotion_data: List[dict]
    seed: Optional[int] = None
    custom_workflow: Optional[str] = None

@router.post("/generate-from-analysis", response_model=GenerationResponse)
async def generate_from_emotion_analysis(request: EmotionAnalysisRequest):
    """
    基于情绪分析结果生成图像
    自动选择主导情绪进行图像生成
    
    Args:
        emotion_data: 情绪分析数据列表 [{"emotion": "Happy", "percentage": 75.5, "color": "#00ff88"}, ...]
        seed: 可选的随机种子
        custom_workflow: 可选的自定义工作流名称
        
    Returns:
        GenerationResponse: 图像生成结果
    """
    try:
        # 解析情绪数据，找到主导情绪
        if not request.emotion_data:
            raise HTTPException(status_code=400, detail="情绪数据不能为空")

        # 找到百分比最高的情绪
        dominant_emotion_data = max(request.emotion_data, key=lambda x: x.get("percentage", 0))
        dominant_emotion = dominant_emotion_data.get("emotion", "").lower()

        # 映射前端情绪名称到后端标准名称
        emotion_mapping = {
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "surprised": "surprised",
            "neutral": "neutral",
            "disgusted": "disgusted",
            "fearful": "fearful"
        }

        standard_emotion = emotion_mapping.get(dominant_emotion)
        if not standard_emotion:
            raise HTTPException(
                status_code=400,
                detail=f"无法识别的情绪类型: {dominant_emotion}"
            )

        # 创建生成请求
        generation_request = GenerationRequest(
            emotion=standard_emotion,
            workflow_name=request.custom_workflow,
            seed=request.seed
        )

        # 生成图像
        result = await comfyui_service.generate_image(generation_request)
        
        logger.info(f"基于情绪分析生成图像: 主导情绪={standard_emotion}, 置信度={dominant_emotion_data.get('percentage', 0):.1f}%")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"基于情绪分析生成图像异常: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    图像生成服务健康检查
    
    Returns:
        dict: 健康状态信息
    """
    try:
        # 检查ComfyUI状态
        comfyui_status = await comfyui_service.check_status()
        
        # 检查工作流文件
        workflows = await comfyui_service.list_workflows()
        available_workflows = [w for w in workflows if w.exists]
        
        return {
            "status": "healthy",
            "service": "图像生成服务",
            "comfyui_available": comfyui_status.available,
            "comfyui_queue_running": comfyui_status.queue_running,
            "comfyui_queue_pending": comfyui_status.queue_pending,
            "available_workflows": len(available_workflows),
            "total_workflows": len(workflows)
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "图像生成服务",
            "error": str(e)
        }
