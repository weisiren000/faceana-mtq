"""
数据转换工具函数
提供各种数据格式转换和标准化功能
"""

import json
import base64
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

from ...config import config

# 配置日志
logger = logging.getLogger(__name__)


def image_to_base64(image_path: Union[str, Path]) -> Optional[str]:
    """
    将图像文件转换为base64编码
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        Optional[str]: base64编码字符串，失败返回None
    """
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            logger.error(f"图像文件不存在: {image_path}")
            return None
            
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
            
    except Exception as e:
        logger.error(f"图像转base64失败: {e}")
        return None


def base64_to_image(base64_string: str, save_path: Union[str, Path]) -> bool:
    """
    将base64编码转换为图像文件
    
    Args:
        base64_string: base64编码字符串
        save_path: 保存路径
        
    Returns:
        bool: 转换是否成功
    """
    try:
        image_data = base64.b64decode(base64_string)
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'wb') as image_file:
            image_file.write(image_data)
            
        logger.info(f"base64转图像成功: {save_path}")
        return True
        
    except Exception as e:
        logger.error(f"base64转图像失败: {e}")
        return False


def standardize_emotion_result(result: Dict, source: str) -> Dict:
    """
    标准化情绪分析结果
    
    Args:
        result: 原始结果字典
        source: 数据源（'facepp', 'openrouter', 'gemini'等）
        
    Returns:
        Dict: 标准化后的结果
    """
    standard_result = {
        'source': source,
        'timestamp': datetime.now().isoformat(),
        'emotion_category': 'neutral',
        'dominant_emotion': 'neutral',
        'polarity_score': 0.0,
        'confidence': 0.0,
        'intensity': 'low',
        'raw_data': result
    }
    
    try:
        if source == 'facepp':
            # Face++结果标准化
            if 'faces' in result and result['faces']:
                face = result['faces'][0]
                emotions = face.get('attributes', {}).get('emotion', {})
                
                # 找到最高分情绪
                max_emotion = max(emotions.items(), key=lambda x: x[1])
                standard_result['dominant_emotion'] = max_emotion[0]
                standard_result['confidence'] = max_emotion[1] / 100.0
                
                # 计算极性分数
                emotion_weights = {
                    'happiness': 1.0, 'surprise': 0.3, 'neutral': 0.0,
                    'disgust': -0.6, 'fear': -0.7, 'sadness': -0.8, 'anger': -0.9
                }
                
                weighted_sum = sum(emotions[emotion] * emotion_weights.get(emotion, 0) 
                                 for emotion in emotions)
                total_weight = sum(emotions.values())
                
                if total_weight > 0:
                    standard_result['polarity_score'] = weighted_sum / total_weight / 100.0
                    
        elif source in ['openrouter', 'gemini']:
            # AI模型结果标准化
            if 'primary_emotion' in result:
                standard_result['dominant_emotion'] = result['primary_emotion']
                standard_result['confidence'] = result.get('confidence', 0.5)
                standard_result['polarity_score'] = result.get('polarity_score', 0.0)
                
        # 确定情绪类别
        if standard_result['polarity_score'] > 0.1:
            standard_result['emotion_category'] = 'positive'
        elif standard_result['polarity_score'] < -0.1:
            standard_result['emotion_category'] = 'negative'
        else:
            standard_result['emotion_category'] = 'neutral'
            
        # 确定强度
        abs_polarity = abs(standard_result['polarity_score'])
        if abs_polarity > 0.7:
            standard_result['intensity'] = 'high'
        elif abs_polarity > 0.3:
            standard_result['intensity'] = 'medium'
        else:
            standard_result['intensity'] = 'low'
            
    except Exception as e:
        logger.error(f"标准化{source}结果失败: {e}")
        
    return standard_result


def merge_emotion_results(results: List[Dict]) -> Dict:
    """
    合并多个情绪分析结果
    
    Args:
        results: 情绪分析结果列表
        
    Returns:
        Dict: 合并后的结果
    """
    if not results:
        return {'error': 'No results to merge'}
        
    merged = {
        'sources': [r.get('source', 'unknown') for r in results],
        'timestamp': datetime.now().isoformat(),
        'results_count': len(results),
        'individual_results': results
    }
    
    try:
        # 计算平均极性分数
        polarity_scores = [r.get('polarity_score', 0.0) for r in results]
        merged['average_polarity'] = sum(polarity_scores) / len(polarity_scores)
        
        # 计算平均置信度
        confidences = [r.get('confidence', 0.0) for r in results]
        merged['average_confidence'] = sum(confidences) / len(confidences)
        
        # 统计主导情绪
        emotions = [r.get('dominant_emotion', 'neutral') for r in results]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
        merged['emotion_consensus'] = max(emotion_counts.items(), key=lambda x: x[1])
        merged['emotion_distribution'] = emotion_counts
        
        # 确定最终类别
        if merged['average_polarity'] > 0.1:
            merged['final_category'] = 'positive'
        elif merged['average_polarity'] < -0.1:
            merged['final_category'] = 'negative'
        else:
            merged['final_category'] = 'neutral'
            
    except Exception as e:
        logger.error(f"合并结果失败: {e}")
        merged['error'] = str(e)
        
    return merged


def convert_opencv_to_pil(cv_image: np.ndarray) -> Optional[Image.Image]:
    """
    将OpenCV图像转换为PIL图像
    
    Args:
        cv_image: OpenCV图像数组
        
    Returns:
        Optional[Image.Image]: PIL图像对象，失败返回None
    """
    try:
        # OpenCV使用BGR，PIL使用RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        return pil_image
        
    except Exception as e:
        logger.error(f"OpenCV转PIL失败: {e}")
        return None


def convert_pil_to_opencv(pil_image: Image.Image) -> Optional[np.ndarray]:
    """
    将PIL图像转换为OpenCV图像
    
    Args:
        pil_image: PIL图像对象
        
    Returns:
        Optional[np.ndarray]: OpenCV图像数组，失败返回None
    """
    try:
        # 确保是RGB模式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            
        # PIL使用RGB，OpenCV使用BGR
        rgb_array = np.array(pil_image)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        return bgr_array
        
    except Exception as e:
        logger.error(f"PIL转OpenCV失败: {e}")
        return None


def resize_image_proportional(image_path: Union[str, Path], max_size: int = 1024) -> Optional[str]:
    """
    按比例调整图像大小
    
    Args:
        image_path: 图像文件路径
        max_size: 最大尺寸（宽或高）
        
    Returns:
        Optional[str]: 调整后的图像路径，失败返回None
    """
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            return None
            
        with Image.open(image_path) as img:
            # 计算新尺寸
            width, height = img.size
            if max(width, height) <= max_size:
                return str(image_path)  # 不需要调整
                
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
                
            # 调整大小
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存到temp目录
            output_path = config.TEMP_DIR / f"resized_{image_path.name}"
            resized_img.save(output_path, quality=95)
            
            logger.info(f"图像已调整: {image_path} -> {output_path}")
            return str(output_path)
            
    except Exception as e:
        logger.error(f"调整图像大小失败: {e}")
        return None


def save_json_result(data: Dict, filename: str, directory: Optional[Union[str, Path]] = None) -> bool:
    """
    保存JSON结果到文件
    
    Args:
        data: 要保存的数据
        filename: 文件名
        directory: 保存目录，None则使用temp目录
        
    Returns:
        bool: 保存是否成功
    """
    try:
        if directory is None:
            directory = config.TEMP_DIR
        else:
            directory = Path(directory)
            
        directory.mkdir(parents=True, exist_ok=True)
        
        filepath = directory / filename
        if not filename.endswith('.json'):
            filepath = directory / f"{filename}.json"
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"JSON结果已保存: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"保存JSON失败: {e}")
        return False


def load_json_result(filepath: Union[str, Path]) -> Optional[Dict]:
    """
    从文件加载JSON结果
    
    Args:
        filepath: JSON文件路径
        
    Returns:
        Optional[Dict]: 加载的数据，失败返回None
    """
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"JSON文件不存在: {filepath}")
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        logger.info(f"JSON结果已加载: {filepath}")
        return data
        
    except Exception as e:
        logger.error(f"加载JSON失败: {e}")
        return None


def format_analysis_summary(result: Dict) -> str:
    """
    格式化分析结果摘要
    
    Args:
        result: 分析结果字典
        
    Returns:
        str: 格式化的摘要文本
    """
    try:
        summary_lines = []
        
        # 基本信息
        summary_lines.append("=== 情绪分析结果摘要 ===")
        summary_lines.append(f"分析时间: {result.get('timestamp', 'Unknown')}")
        
        # 最终判定
        if 'final_judgment' in result:
            judgment = result['final_judgment']
            summary_lines.append(f"最终情绪: {judgment.get('dominant_emotion', 'Unknown')}")
            summary_lines.append(f"情绪类别: {judgment.get('emotion_category', 'Unknown')}")
            summary_lines.append(f"极性分数: {judgment.get('polarity_score', 0.0):.3f}")
            summary_lines.append(f"置信度: {judgment.get('confidence', 0.0):.3f}")
            
        # 智能体结果
        if 'agent_results' in result:
            summary_lines.append("\n--- 智能体分析 ---")
            for agent, agent_result in result['agent_results'].items():
                if agent_result and 'emotion_category' in agent_result:
                    summary_lines.append(f"{agent}: {agent_result['emotion_category']} "
                                        f"({agent_result.get('confidence', 0.0):.3f})")
                    
        # 一致性分析
        if 'consistency_analysis' in result:
            consistency = result['consistency_analysis']
            summary_lines.append(f"\n一致性评分: {consistency.get('consistency_score', 0.0):.3f}")
            
        return "\n".join(summary_lines)
        
    except Exception as e:
        logger.error(f"格式化摘要失败: {e}")
        return f"摘要生成失败: {str(e)}"
