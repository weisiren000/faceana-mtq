"""
ComfyUI相关数据模型
用于图像生成API的请求和响应格式
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass
class ImageInfo:
    """生成的图像信息"""
    filename: str
    subfolder: str = ""
    type: str = "output"
    url: Optional[str] = None


@dataclass
class GenerationRequest:
    """图像生成请求"""
    emotion: str                    # 情绪类型 (happy, sad, angry, etc.)
    workflow_name: Optional[str] = None  # 可选的自定义工作流名称
    seed: Optional[int] = None      # 可选的随机种子
    custom_params: Optional[Dict[str, Any]] = None  # 自定义参数


@dataclass
class GenerationResponse:
    """图像生成响应"""
    success: bool
    prompt_id: Optional[str] = None
    images: List[ImageInfo] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None  # 生成耗时（秒）


@dataclass
class ComfyUIStatus:
    """ComfyUI服务状态"""
    available: bool
    queue_running: int = 0
    queue_pending: int = 0
    system_stats: Optional[Dict] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowInfo:
    """工作流信息"""
    name: str
    emotion: str
    path: str
    exists: bool
    last_modified: Optional[datetime] = None


# 情绪到工作流文件的映射
EMOTION_WORKFLOW_MAPPING = {
    "happy": "happy.json",
    "sad": "sad.json", 
    "angry": "angry.json",
    "surprised": "surprised.json",
    "neutral": "neutral.json",
    "disgusted": "disgusted.json",
    "fearful": "fearful.json",  # 注意：fearful对应的是fearful.json，不是fear.json
}

# 默认工作流（当特定情绪工作流不存在时使用）
DEFAULT_WORKFLOW = "jimeng.json"

# ComfyUI配置
COMFYUI_CONFIG = {
    "base_url": "http://localhost:8188",
    "timeout": 10,
    "max_wait_time": 300,  # 最大等待时间（秒）
    "check_interval": 3,   # 状态检查间隔（秒）
}


def get_workflow_filename(emotion: str) -> str:
    """根据情绪获取对应的工作流文件名"""
    return EMOTION_WORKFLOW_MAPPING.get(emotion.lower(), DEFAULT_WORKFLOW)


def validate_emotion(emotion: str) -> bool:
    """验证情绪类型是否有效"""
    return emotion.lower() in EMOTION_WORKFLOW_MAPPING


def create_filename_prefix(emotion: str) -> str:
    """创建文件名前缀"""
    timestamp = int(datetime.now().timestamp())
    return f"emoscan_{emotion}_{timestamp}"


def parse_comfyui_outputs(outputs: Dict[str, Any], base_url: str) -> List[ImageInfo]:
    """解析ComfyUI输出，提取图像信息"""
    images = []
    
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for img in node_output["images"]:
                # 使用我们后端的静态文件服务URL
                backend_url = "http://localhost:8000/comfyui-output"
                image_info = ImageInfo(
                    filename=img["filename"],
                    subfolder=img.get("subfolder", ""),
                    type=img.get("type", "output"),
                    url=f"{backend_url}/{img['filename']}"
                )
                images.append(image_info)
    
    return images


def workflow_to_json(workflow: Dict[str, Any]) -> str:
    """将工作流转换为JSON字符串"""
    return json.dumps(workflow, ensure_ascii=False, indent=2)


def json_to_workflow(json_str: str) -> Dict[str, Any]:
    """从JSON字符串解析工作流"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Invalid workflow JSON: {e}")
