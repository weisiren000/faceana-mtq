"""
图像生成API路由
提供从情绪数据生成图像的接口
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, List, Optional

from ....models.comfyui import GenerationRequest, GenerationResponse
from ....services.comfyui_service import ComfyUIService

router = APIRouter(prefix="/api/v1/generation", tags=["generation"])

# 服务实例
comfyui_service = ComfyUIService()

@router.post("/from-emotion", response_model=GenerationResponse)
async def generate_from_emotion(request: GenerationRequest):
    """
    从情绪数据生成图像
    
    Args:
        request: 包含情绪数据和生成参数的请求
        
    Returns:
        GenerationResponse: 生成响应
    """
    try:
        # 更新ComfyUI URL（如果提供）
        if request.comfyui_url:
            comfyui_service.base_url = request.comfyui_url
            
        # 检查连接
        connected = await comfyui_service.check_connection()
        if not connected:
            return GenerationResponse(
                success=False,
                status="error",
                error=f"无法连接到ComfyUI服务器: {comfyui_service.base_url}"
            )
            
        # 创建工作流
        workflow = comfyui_service.create_workflow_from_emotion(
            emotion=request.emotion,
            intensity=request.intensity,
            custom_prompt=request.custom_prompt
        )
        
        # 发送提示词
        result = await comfyui_service.send_prompt(workflow)
        
        if result["success"]:
            # 获取使用的提示词
            prompt = workflow["6"]["inputs"]["text"]
            
            return GenerationResponse(
                success=True,
                prompt_id=result["prompt_id"],
                prompt=prompt,
                status="generating"
            )
        else:
            return GenerationResponse(
                success=False,
                status="error",
                error=result.get("error", "发送提示词失败")
            )
            
    except Exception as e:
        return GenerationResponse(
            success=False,
            status="error",
            error=f"生成图像时出错: {str(e)}"
        ) 