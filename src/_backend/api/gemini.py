"""
Gemini API集成模块
提供Google Gemini模型的图像分析和情绪识别功能
"""

import google.generativeai as genai
import logging
import json
from typing import Dict, List, Optional, Union
from pathlib import Path
import time
from PIL import Image

from ..config import config

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini API客户端"""

    def __init__(self, api_key: str = None):
        """
        初始化Gemini API客户端

        Args:
            api_key: API密钥，默认使用配置中的值
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        self.models = config.GEMINI_MODELS

        # 验证配置
        if not self.api_key:
            raise ValueError("Gemini API密钥未配置")

        # 配置API
        genai.configure(api_key=self.api_key)

        # 默认使用第一个可用模型
        self.default_model = self.models[0] if self.models else "gemini-2.0-flash-lite"

        logger.info("Gemini API客户端初始化成功")

    def _load_image(self, image_path: str) -> Image.Image:
        """
        加载图像文件

        Args:
            image_path: 图像文件路径

        Returns:
            Image.Image: PIL图像对象
        """
        try:
            image = Image.open(image_path)
            # 确保图像是RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            logger.error(f"加载图像失败: {e}")
            raise

    def analyze_image_emotion(self, image_path: str, model: str = None) -> Dict:
        """
        分析图像情绪

        Args:
            image_path: 图像文件路径
            model: 使用的模型，默认使用配置中的第一个模型

        Returns:
            Dict: 情绪分析结果
        """
        if model is None:
            model = self.default_model

        try:
            # 加载图像
            image = self._load_image(image_path)

            # 创建模型实例
            model_instance = genai.GenerativeModel(model)

            # 构建提示词
            prompt = """请分析这张图片中人物的情绪状态。请从以下几个方面进行详细分析：

1. 主要情绪：识别图片中人物的主要情绪（如：快乐、悲伤、愤怒、惊讶、恐惧、厌恶、中性等）
2. 情绪强度：评估情绪的强烈程度（1-10分，10分为最强烈）
3. 面部表情特征：描述观察到的具体面部表情特征（眼部、嘴部、眉毛等）
4. 身体语言：如果可见，描述身体姿态传达的情绪信息
5. 置信度：对分析结果的置信度评估（1-10分）
6. 整体情绪评估：综合判断人物的情绪状态和可能的情绪背景

请以JSON格式返回结果，包含以下字段：
{
    "primary_emotion": "主要情绪",
    "emotion_intensity": 情绪强度分数(1-10),
    "facial_features": "面部表情特征详细描述",
    "body_language": "身体语言描述（如果可见）",
    "confidence": 置信度分数(1-10),
    "overall_assessment": "整体情绪评估和分析",
    "secondary_emotions": ["可能的次要情绪列表"]
}

请确保返回有效的JSON格式。"""

            # 发送请求
            response = model_instance.generate_content([prompt, image])

            if not response.text:
                return {'error': '模型没有返回响应'}

            # 尝试解析JSON响应
            try:
                # 提取JSON部分
                content = response.text
                json_start = content.find('{')
                json_end = content.rfind('}') + 1

                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    emotion_data = json.loads(json_content)
                else:
                    # 如果没有找到JSON，返回原始内容
                    emotion_data = {'raw_response': content}

                return {
                    'model': model,
                    'image_path': image_path,
                    'emotion_analysis': emotion_data,
                    'raw_response': response.text
                }

            except json.JSONDecodeError:
                # JSON解析失败，返回原始响应
                return {
                    'model': model,
                    'image_path': image_path,
                    'emotion_analysis': {'raw_response': response.text},
                    'raw_response': response.text
                }

        except Exception as e:
            error_msg = f"Gemini图像情绪分析失败: {e}"
            logger.error(error_msg)
            return {'error': error_msg}

    def batch_analyze_emotions(self, image_paths: List[str], model: str = None) -> List[Dict]:
        """
        批量分析图像情绪

        Args:
            image_paths: 图像文件路径列表
            model: 使用的模型

        Returns:
            List[Dict]: 批量分析结果
        """
        results = []

        for i, image_path in enumerate(image_paths):
            logger.info(f"Gemini分析第 {i+1}/{len(image_paths)} 张图像: {image_path}")

            result = self.analyze_image_emotion(image_path, model)
            result['image_index'] = i

            results.append(result)

            # 避免API限流
            if i < len(image_paths) - 1:
                time.sleep(1)  # Gemini API限流控制

        logger.info(f"Gemini批量情绪分析完成，处理了 {len(image_paths)} 张图像")
        return results

    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        Returns:
            List[str]: 可用模型列表
        """
        return self.models.copy()

    def test_model(self, model: str) -> Dict:
        """
        测试指定模型是否可用

        Args:
            model: 模型名称

        Returns:
            Dict: 测试结果
        """
        try:
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content("Hello, this is a test message. Please respond with 'Test successful'.")

            if response.text:
                return {'model': model, 'available': True, 'response': response.text}
            else:
                return {'model': model, 'available': False, 'error': 'No response from model'}

        except Exception as e:
            return {'model': model, 'available': False, 'error': str(e)}

# 便捷函数
def analyze_image_with_gemini(image_path: str, model: str = None) -> Dict:
    """
    便捷函数：使用Gemini分析图像情绪

    Args:
        image_path: 图像文件路径
        model: 使用的模型

    Returns:
        Dict: 情绪分析结果
    """
    client = GeminiClient()
    return client.analyze_image_emotion(image_path, model)

def batch_analyze_with_gemini(image_paths: List[str], model: str = None) -> List[Dict]:
    """
    便捷函数：使用Gemini批量分析图像情绪

    Args:
        image_paths: 图像文件路径列表
        model: 使用的模型

    Returns:
        List[Dict]: 批量分析结果
    """
    client = GeminiClient()
    return client.batch_analyze_emotions(image_paths, model)

def analyze_capture_with_gemini(model: str = None) -> List[Dict]:
    """
    便捷函数：使用Gemini分析capture目录中的所有图像

    Args:
        model: 使用的模型

    Returns:
        List[Dict]: 分析结果
    """
    from pathlib import Path

    # 获取capture目录中的图像文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []

    for ext in image_extensions:
        image_files.extend(config.CAPTURE_DIR.glob(f"*{ext}"))
        image_files.extend(config.CAPTURE_DIR.glob(f"*{ext.upper()}"))

    if not image_files:
        logger.warning("capture目录中没有找到图像文件")
        return []

    # 转换为字符串路径
    image_paths = [str(path) for path in sorted(image_files)]

    # 批量分析
    return batch_analyze_with_gemini(image_paths, model)

if __name__ == "__main__":
    # 测试代码
    try:
        client = GeminiClient()
        print("Gemini API客户端测试成功")

        # 测试可用模型
        models = client.get_available_models()
        print(f"可用模型: {models}")

    except Exception as e:
        print(f"Gemini API客户端测试失败: {e}")
