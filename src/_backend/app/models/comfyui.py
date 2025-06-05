"""
ComfyUI相关的数据模型
定义API请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class GenerationRequest(BaseModel):
    """图像生成请求模型"""
    emotion: str = Field(..., description="情绪类型，如happy、sad等")
    intensity: float = Field(0.8, description="情绪强度，0-1之间")
    custom_prompt: Optional[str] = Field(None, description="自定义提示词")
    negative_prompt: Optional[str] = Field(None, description="负面提示词")
    comfyui_url: Optional[str] = Field("http://localhost:8000", description="ComfyUI API地址")
    
class GenerationResponse(BaseModel):
    """图像生成响应模型"""
    success: bool = Field(..., description="是否成功")
    prompt_id: Optional[str] = Field(None, description="提示词ID")
    prompt: Optional[str] = Field(None, description="实际使用的提示词")
    status: str = Field(..., description="生成状态")
    error: Optional[str] = Field(None, description="错误信息")

class ProgressUpdate(BaseModel):
    """生成进度更新模型"""
    prompt_id: str = Field(..., description="提示词ID")
    progress: float = Field(..., description="进度，0-1之间")
    status: str = Field(..., description="状态")
    
class ImageResult(BaseModel):
    """图像结果模型"""
    prompt_id: str = Field(..., description="提示词ID")
    image_url: str = Field(..., description="图像URL")
    emotion: str = Field(..., description="情绪类型")
    prompt: str = Field(..., description="使用的提示词") 