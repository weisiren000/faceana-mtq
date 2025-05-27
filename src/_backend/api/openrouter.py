"""
OpenRouter API集成模块
提供多种AI模型的图像分析和情绪识别功能
"""

import requests
import logging
import base64
import json
from typing import Dict, List, Optional, Union
from pathlib import Path
import time

from ..config import config

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class OpenRouterClient:
    """OpenRouter API客户端"""

    def __init__(self, api_key: str = None):
        """
        初始化OpenRouter API客户端

        Args:
            api_key: API密钥，默认使用配置中的值
        """
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_API_URL
        self.models = config.OPENROUTER_MODELS

        # 验证配置
        if not self.api_key:
            raise ValueError("OpenRouter API密钥未配置")

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/faceana-mtq',
            'X-Title': 'FaceAna-MTQ'
        }

        logger.info("OpenRouter API客户端初始化成功")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        将图像编码为base64

        Args:
            image_path: 图像文件路径

        Returns:
            str: base64编码的图像数据
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')

                # 检测图像格式
                if image_path.lower().endswith(('.png', '.PNG')):
                    mime_type = 'image/png'
                elif image_path.lower().endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                    mime_type = 'image/jpeg'
                elif image_path.lower().endswith(('.bmp', '.BMP')):
                    mime_type = 'image/bmp'
                else:
                    mime_type = 'image/jpeg'  # 默认

                return f"data:{mime_type};base64,{base64_data}"

        except Exception as e:
            logger.error(f"图像编码失败: {e}")
            raise

    def _make_request(self, model: str, messages: List[Dict], max_tokens: int = 1000) -> Dict:
        """
        发送API请求

        Args:
            model: 模型名称
            messages: 消息列表
            max_tokens: 最大token数

        Returns:
            Dict: API响应
        """
        url = f"{self.base_url}/chat/completions"

        data = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.7
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=config.REQUEST_TIMEOUT
            )

            response.raise_for_status()
            result = response.json()

            # 检查API错误
            if 'error' in result:
                logger.error(f"OpenRouter API错误: {result['error']}")
                return {'error': result['error']}

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API请求失败: {e}")
            return {'error': str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"OpenRouter API响应解析失败: {e}")
            return {'error': 'Invalid JSON response'}

    def analyze_image_emotion(self, image_path: str, model: str = None) -> Dict:
        """
        分析图像情绪

        Args:
            image_path: 图像文件路径
            model: 使用的模型，默认使用第一个可用模型

        Returns:
            Dict: 情绪分析结果
        """
        if model is None:
            model = self.models[0] if self.models else "qwen/qwen2.5-vl-32b-instruct:free"

        try:
            # 编码图像
            base64_image = self._encode_image_to_base64(image_path)

            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请分析这张图片中人物的情绪状态。请从以下几个方面进行分析：

1. 主要情绪：识别图片中人物的主要情绪（如：快乐、悲伤、愤怒、惊讶、恐惧、厌恶、中性等）
2. 情绪强度：评估情绪的强烈程度（1-10分）
3. 面部表情特征：描述观察到的具体面部表情特征
4. 整体情绪评估：综合判断人物的情绪状态

请以JSON格式返回结果，包含以下字段：
{
    "primary_emotion": "主要情绪",
    "emotion_intensity": 情绪强度分数,
    "facial_features": "面部表情特征描述",
    "confidence": 置信度分数,
    "overall_assessment": "整体情绪评估"
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image
                            }
                        }
                    ]
                }
            ]

            # 发送请求
            result = self._make_request(model, messages)

            if 'error' in result:
                return result

            # 提取响应内容
            choices = result.get('choices', [])
            if not choices:
                return {'error': '没有返回分析结果'}

            content = choices[0].get('message', {}).get('content', '')

            # 尝试解析JSON响应
            try:
                # 提取JSON部分
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
                    'raw_result': result
                }

            except json.JSONDecodeError:
                # JSON解析失败，返回原始响应
                return {
                    'model': model,
                    'image_path': image_path,
                    'emotion_analysis': {'raw_response': content},
                    'raw_result': result
                }

        except Exception as e:
            error_msg = f"图像情绪分析失败: {e}"
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
            logger.info(f"OpenRouter分析第 {i+1}/{len(image_paths)} 张图像: {image_path}")

            result = self.analyze_image_emotion(image_path, model)
            result['image_index'] = i

            results.append(result)

            # 避免API限流
            if i < len(image_paths) - 1:
                time.sleep(1)  # OpenRouter需要更长的间隔

        logger.info(f"OpenRouter批量情绪分析完成，处理了 {len(image_paths)} 张图像")
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
        messages = [
            {
                "role": "user",
                "content": "Hello, this is a test message. Please respond with 'Test successful'."
            }
        ]

        result = self._make_request(model, messages, max_tokens=50)

        if 'error' in result:
            return {'model': model, 'available': False, 'error': result['error']}
        else:
            return {'model': model, 'available': True, 'response': result}

# 便捷函数
def analyze_image_with_openrouter(image_path: str, model: str = None) -> Dict:
    """
    便捷函数：使用OpenRouter分析图像情绪

    Args:
        image_path: 图像文件路径
        model: 使用的模型

    Returns:
        Dict: 情绪分析结果
    """
    client = OpenRouterClient()
    return client.analyze_image_emotion(image_path, model)

def batch_analyze_with_openrouter(image_paths: List[str], model: str = None) -> List[Dict]:
    """
    便捷函数：使用OpenRouter批量分析图像情绪

    Args:
        image_paths: 图像文件路径列表
        model: 使用的模型

    Returns:
        List[Dict]: 批量分析结果
    """
    client = OpenRouterClient()
    return client.batch_analyze_emotions(image_paths, model)

def analyze_capture_with_openrouter(model: str = None) -> List[Dict]:
    """
    便捷函数：使用OpenRouter分析capture目录中的所有图像

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
    return batch_analyze_with_openrouter(image_paths, model)

if __name__ == "__main__":
    # 测试代码
    try:
        client = OpenRouterClient()
        print("OpenRouter API客户端测试成功")

        # 测试可用模型
        models = client.get_available_models()
        print(f"可用模型: {models}")

    except Exception as e:
        print(f"OpenRouter API客户端测试失败: {e}")
