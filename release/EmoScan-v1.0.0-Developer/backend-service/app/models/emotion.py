"""
情绪分析数据模型
兼容前端EmotionData格式和Face++ API返回格式
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from datetime import datetime
import json


@dataclass
class EmotionData:
    """前端兼容的情绪数据格式"""
    emotion: str        # 情绪名称 (Happy, Sad, Angry, etc.)
    percentage: float   # 百分比 (0-100)
    color: str         # 显示颜色


@dataclass
class EmotionResult:
    """完整的情绪分析结果"""
    emotions: Dict[str, float]  # 7种标准情绪的概率 (0-1)
    dominant_emotion: str       # 主导情绪
    confidence: float          # 置信度 (0-1)
    source: str               # 数据来源 (facepp/gemini/openrouter)
    timestamp: datetime       # 时间戳
    raw_data: Optional[Dict]  # 原始API返回数据


@dataclass
class AnalysisResponse:
    """API响应格式"""
    success: bool
    emotion_data: List[EmotionData]
    analysis_text: str
    error_message: Optional[str] = None


@dataclass
class BatchAnalysisResponse:
    """批量分析API响应格式"""
    success: bool
    emotion_data: List[EmotionData]
    analysis_text: str
    detailed_results: List[Dict]  # 每张图片的详细结果
    judge_result: Optional[Dict]  # 裁判员AI的判断结果
    error_message: Optional[str] = None


# 7种标准情绪类别配置（与前端保持一致）
EMOTION_CONFIG = {
    "happy": {"name": "Happy", "color": "#00ff88"},
    "sad": {"name": "Sad", "color": "#0099ff"},
    "angry": {"name": "Angry", "color": "#ff0066"},
    "surprised": {"name": "Surprised", "color": "#ffaa00"},
    "neutral": {"name": "Neutral", "color": "#888888"},
    "disgusted": {"name": "Disgusted", "color": "#9d4edd"},
    "fearful": {"name": "Fearful", "color": "#f72585"},
}
# Face++ API情绪映射表
FACEPP_EMOTION_MAPPING = {
    "anger": "angry",
    "happiness": "happy", 
    "sadness": "sad",
    "surprise": "surprised",
    "fear": "fearful",
    "disgust": "disgusted",
    "neutral": "neutral"
}

# AI模型情绪映射表（中英文）
AI_EMOTION_MAPPING = {
    # 英文
    "happy": "happy", "sad": "sad", "angry": "angry",
    "surprised": "surprised", "neutral": "neutral", "disgusted": "disgusted",
    "fearful": "fearful", "fear": "fearful", "disgust": "disgusted",
    "anger": "angry", "happiness": "happy", "sadness": "sad",
    "surprise": "surprised",
    
    # 中文
    "开心": "happy", "高兴": "happy", "快乐": "happy",
    "悲伤": "sad", "难过": "sad", "愤怒": "angry", "生气": "angry",
    "惊讶": "surprised", "吃惊": "surprised", "平静": "neutral",
    "中性": "neutral", "无表情": "neutral", "厌恶": "disgusted",
    "恶心": "disgusted", "恐惧": "fearful", "害怕": "fearful", "担心": "fearful",
}


def normalize_emotion_name(emotion: str) -> str:
    """标准化情绪名称"""
    emotion_lower = emotion.lower().strip()
    return AI_EMOTION_MAPPING.get(emotion_lower, "neutral")


def create_emotion_data_list(emotions: Dict[str, float]) -> List[EmotionData]:
    """将情绪概率字典转换为前端兼容的EmotionData列表"""
    emotion_data_list = []
    
    for emotion_key, config in EMOTION_CONFIG.items():
        percentage = emotions.get(emotion_key, 0.0) * 100  # 转换为百分比
        emotion_data = EmotionData(
            emotion=config["name"],
            percentage=round(percentage, 1),
            color=config["color"]
        )
        emotion_data_list.append(emotion_data)
    
    return emotion_data_list
def normalize_probabilities(emotions: Dict[str, float]) -> Dict[str, float]:
    """标准化情绪概率，确保总和为1.0"""
    # 确保所有7种情绪都存在
    normalized = {}
    for emotion_key in EMOTION_CONFIG.keys():
        normalized[emotion_key] = emotions.get(emotion_key, 0.0)
    
    # 计算总和
    total = sum(normalized.values())
    
    # 如果总和为0，设置neutral为1.0
    if total == 0:
        normalized["neutral"] = 1.0
        return normalized
    
    # 标准化到总和为1.0
    for emotion_key in normalized:
        normalized[emotion_key] = normalized[emotion_key] / total
    
    return normalized


def get_dominant_emotion(emotions: Dict[str, float]) -> str:
    """获取主导情绪"""
    if not emotions:
        return "neutral"
    
    return max(emotions.items(), key=lambda x: x[1])[0]


def emotions_to_json(emotions: Dict[str, float]) -> str:
    """将情绪数据转换为JSON字符串"""
    return json.dumps(emotions, ensure_ascii=False, indent=2)


def json_to_emotions(json_str: str) -> Dict[str, float]:
    """从JSON字符串解析情绪数据"""
    try:
        data = json.loads(json_str)
        return normalize_probabilities(data)
    except (json.JSONDecodeError, TypeError):
        return {"neutral": 1.0}