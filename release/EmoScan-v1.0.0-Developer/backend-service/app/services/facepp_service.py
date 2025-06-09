"""
Face++ API服务
处理人脸情绪识别
"""

import os
import requests
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from PIL import Image
from io import BytesIO

from ..models.emotion import (
    EmotionResult, 
    FACEPP_EMOTION_MAPPING, 
    normalize_probabilities,
    get_dominant_emotion
)

logger = logging.getLogger(__name__)


class FacePPService:
    """Face++ API服务类"""
    
    def __init__(self):
        self.api_key = os.getenv("FACEPP_API_KEY", "wvv-yzcDhvSx-vIs7tl3DZ2vJnEp-NCr")
        self.api_secret = os.getenv("FACEPP_API_SECRET", "Q82rf7NWaheJEQ6Az5_aJoN1MlpfDipT")
        self.base_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"        
    def compress_image(self, image_data: bytes, max_size_kb: int = 700, 
                      max_width: int = 1024) -> BytesIO:
        """压缩图像以满足API要求"""
        try:
            img = Image.open(BytesIO(image_data))
            
            # 限制宽度
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为RGB格式
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # 循环压缩直到小于max_size_kb
            quality = 90
            while True:
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=quality)
                size_kb = buffer.tell() / 1024
                
                if size_kb <= max_size_kb or quality < 30:
                    buffer.seek(0)
                    return buffer
                    
                quality -= 10
                
        except Exception as e:
            logger.error(f"图像压缩失败: {e}")
            raise ValueError(f"图像处理失败: {e}")    
    def parse_facepp_response(self, response_data: Dict) -> Dict[str, float]:
        """解析Face++ API响应，转换为标准情绪格式"""
        try:
            faces = response_data.get("faces", [])
            if not faces:
                logger.warning("Face++ API未检测到人脸")
                return {"neutral": 1.0}
            
            # 取第一个检测到的人脸
            face = faces[0]
            attributes = face.get("attributes", {})
            emotion_data = attributes.get("emotion", {})
            
            if not emotion_data:
                logger.warning("Face++ API未返回情绪数据")
                return {"neutral": 1.0}
            
            # 转换Face++格式到标准格式
            standard_emotions = {}
            for facepp_emotion, value in emotion_data.items():
                standard_emotion = FACEPP_EMOTION_MAPPING.get(facepp_emotion)
                if standard_emotion:
                    # Face++返回的是百分比，需要转换为0-1的概率
                    standard_emotions[standard_emotion] = value / 100.0
            
            # 标准化概率
            return normalize_probabilities(standard_emotions)
            
        except Exception as e:
            logger.error(f"解析Face++ API响应失败: {e}")
            return {"neutral": 1.0}    
    async def analyze_emotion(self, image_data: bytes) -> EmotionResult:
        """分析图像中的情绪"""
        try:
            # 压缩图像
            compressed_image = self.compress_image(image_data)
            
            # 准备API请求
            files = {"image_file": ("image.jpg", compressed_image, "image/jpeg")}
            data = {
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "return_attributes": "emotion"
            }
            
            # 发送请求
            response = requests.post(self.base_url, data=data, files=files, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            # 检查API错误
            if "error_message" in response_data:
                raise Exception(f"Face++ API错误: {response_data['error_message']}")
            
            # 解析情绪数据
            emotions = self.parse_facepp_response(response_data)
            dominant_emotion = get_dominant_emotion(emotions)
            
            # 计算置信度（使用主导情绪的概率）
            confidence = emotions.get(dominant_emotion, 0.0)
            
            return EmotionResult(
                emotions=emotions,
                dominant_emotion=dominant_emotion,
                confidence=confidence,
                source="facepp",
                timestamp=datetime.now(),
                raw_data=response_data
            )
            
        except Exception as e:
            logger.error(f"Face++ API调用失败: {e}")
            raise Exception(f"Face++ 情绪分析失败: {str(e)}")