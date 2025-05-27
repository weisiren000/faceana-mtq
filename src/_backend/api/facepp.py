"""
Face++ API集成模块
提供人脸检测、情绪识别等功能
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

class FacePPClient:
    """Face++ API客户端"""

    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        初始化Face++ API客户端

        Args:
            api_key: API密钥，默认使用配置中的值
            api_secret: API密钥，默认使用配置中的值
        """
        self.api_key = api_key or config.FACEPP_API_KEY
        self.api_secret = api_secret or config.FACEPP_API_SECRET
        self.base_url = config.FACEPP_API_URL

        # 验证配置
        if not self.api_key or not self.api_secret:
            raise ValueError("Face++ API密钥未配置")

        logger.info("Face++ API客户端初始化成功")

    def _make_request(self, endpoint: str, data: Dict, files: Dict = None) -> Dict:
        """
        发送API请求

        Args:
            endpoint: API端点
            data: 请求数据
            files: 文件数据

        Returns:
            Dict: API响应
        """
        url = f"{self.base_url}/{endpoint}"

        # 添加API密钥
        data.update({
            'api_key': self.api_key,
            'api_secret': self.api_secret
        })

        try:
            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=config.REQUEST_TIMEOUT
            )

            response.raise_for_status()
            result = response.json()

            # 检查API错误
            if 'error_message' in result:
                logger.error(f"Face++ API错误: {result['error_message']}")
                return {'error': result['error_message']}

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Face++ API请求失败: {e}")
            return {'error': str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Face++ API响应解析失败: {e}")
            return {'error': 'Invalid JSON response'}

    def detect_face(self, image_path: str, return_attributes: List[str] = None) -> Dict:
        """
        人脸检测

        Args:
            image_path: 图像文件路径
            return_attributes: 返回的属性列表

        Returns:
            Dict: 检测结果
        """
        if return_attributes is None:
            return_attributes = [
                'emotion', 'age', 'gender', 'ethnicity',
                'beauty', 'expression', 'facequality'
            ]

        try:
            with open(image_path, 'rb') as f:
                files = {'image_file': f}
                data = {
                    'return_attributes': ','.join(return_attributes)
                }

                result = self._make_request('detect', data, files)

                if 'error' in result:
                    return result

                logger.info(f"Face++检测完成，发现 {len(result.get('faces', []))} 个人脸")
                return result

        except FileNotFoundError:
            error_msg = f"图像文件不存在: {image_path}"
            logger.error(error_msg)
            return {'error': error_msg}
        except Exception as e:
            error_msg = f"人脸检测失败: {e}"
            logger.error(error_msg)
            return {'error': error_msg}

    def analyze_emotion(self, image_path: str) -> Dict:
        """
        情绪分析

        Args:
            image_path: 图像文件路径

        Returns:
            Dict: 情绪分析结果
        """
        result = self.detect_face(image_path, ['emotion'])

        if 'error' in result:
            return result

        faces = result.get('faces', [])
        if not faces:
            return {'error': '未检测到人脸'}

        # 提取情绪信息
        emotions_data = []
        for i, face in enumerate(faces):
            attributes = face.get('attributes', {})
            emotion = attributes.get('emotion', {})

            if emotion:
                emotions_data.append({
                    'face_index': i,
                    'emotions': emotion,
                    'dominant_emotion': max(emotion.items(), key=lambda x: x[1])[0],
                    'confidence': max(emotion.values())
                })

        return {
            'total_faces': len(faces),
            'emotions': emotions_data,
            'raw_result': result
        }

    def batch_analyze_emotions(self, image_paths: List[str]) -> List[Dict]:
        """
        批量情绪分析

        Args:
            image_paths: 图像文件路径列表

        Returns:
            List[Dict]: 批量分析结果
        """
        results = []

        for i, image_path in enumerate(image_paths):
            logger.info(f"分析第 {i+1}/{len(image_paths)} 张图像: {image_path}")

            result = self.analyze_emotion(image_path)
            result['image_path'] = image_path
            result['image_index'] = i

            results.append(result)

            # 避免API限流
            if i < len(image_paths) - 1:
                time.sleep(0.5)

        logger.info(f"批量情绪分析完成，处理了 {len(image_paths)} 张图像")
        return results

    def get_emotion_summary(self, analysis_results: List[Dict]) -> Dict:
        """
        获取情绪分析摘要

        Args:
            analysis_results: 批量分析结果

        Returns:
            Dict: 情绪摘要统计
        """
        emotion_counts = {}
        total_faces = 0
        successful_analyses = 0

        for result in analysis_results:
            if 'error' not in result and 'emotions' in result:
                successful_analyses += 1
                total_faces += result.get('total_faces', 0)

                for emotion_data in result.get('emotions', []):
                    dominant_emotion = emotion_data.get('dominant_emotion')
                    if dominant_emotion:
                        emotion_counts[dominant_emotion] = emotion_counts.get(dominant_emotion, 0) + 1

        # 计算情绪分布百分比
        emotion_percentages = {}
        if total_faces > 0:
            for emotion, count in emotion_counts.items():
                emotion_percentages[emotion] = (count / total_faces) * 100

        return {
            'total_images': len(analysis_results),
            'successful_analyses': successful_analyses,
            'total_faces': total_faces,
            'emotion_counts': emotion_counts,
            'emotion_percentages': emotion_percentages,
            'dominant_overall_emotion': max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        }

# 便捷函数
def analyze_image_emotion(image_path: str) -> Dict:
    """
    便捷函数：分析单张图像的情绪

    Args:
        image_path: 图像文件路径

    Returns:
        Dict: 情绪分析结果
    """
    client = FacePPClient()
    return client.analyze_emotion(image_path)

def analyze_images_batch(image_paths: List[str]) -> List[Dict]:
    """
    便捷函数：批量分析图像情绪

    Args:
        image_paths: 图像文件路径列表

    Returns:
        List[Dict]: 批量分析结果
    """
    client = FacePPClient()
    return client.batch_analyze_emotions(image_paths)

def analyze_capture_directory() -> List[Dict]:
    """
    便捷函数：分析capture目录中的所有图像

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
    return analyze_images_batch(image_paths)

if __name__ == "__main__":
    # 测试代码
    try:
        client = FacePPClient()
        print("Face++ API客户端测试成功")
    except Exception as e:
        print(f"Face++ API客户端测试失败: {e}")
