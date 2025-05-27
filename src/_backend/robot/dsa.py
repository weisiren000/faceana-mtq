"""
DSA智能体 (Data Sentiment Analysis Agent)
数据情感分析智能体，专注于处理Face++返回的结构化情绪数据
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

from ..config import config
from ..api.facepp import analyze_capture_directory

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DSAAgent:
    """数据情感分析智能体"""

    def __init__(self):
        """初始化DSA智能体"""
        self.confidence_threshold = config.DSA_CONFIDENCE_THRESHOLD
        self.emotion_weights = {
            'happiness': 1.0,
            'sadness': -0.8,
            'anger': -0.9,
            'fear': -0.7,
            'surprise': 0.3,
            'disgust': -0.6,
            'neutral': 0.0
        }
        logger.info("DSA智能体初始化成功")

    def analyze_facepp_data(self, facepp_results: List[Dict]) -> Dict:
        """
        分析Face++返回的数据

        Args:
            facepp_results: Face++分析结果列表

        Returns:
            Dict: DSA分析结果
        """
        if not facepp_results:
            return {'error': '没有Face++数据可分析'}

        valid_results = []
        total_faces = 0
        emotion_scores = {}
        confidence_scores = []

        # 处理每个分析结果
        for result in facepp_results:
            if 'error' in result:
                logger.warning(f"跳过错误结果: {result['error']}")
                continue

            emotions_data = result.get('emotions', [])
            if not emotions_data:
                continue

            valid_results.append(result)
            total_faces += len(emotions_data)

            # 提取情绪数据
            for emotion_data in emotions_data:
                emotions = emotion_data.get('emotions', {})
                confidence = emotion_data.get('confidence', 0)

                confidence_scores.append(confidence)

                # 累积情绪分数
                for emotion, score in emotions.items():
                    if emotion not in emotion_scores:
                        emotion_scores[emotion] = []
                    emotion_scores[emotion].append(score)

        if not valid_results:
            return {'error': '没有有效的Face++数据'}

        # 计算平均情绪分数
        avg_emotion_scores = {}
        for emotion, scores in emotion_scores.items():
            avg_emotion_scores[emotion] = np.mean(scores)

        # 确定主导情绪
        dominant_emotion = max(avg_emotion_scores.items(), key=lambda x: x[1])

        # 计算情绪极性分数
        polarity_score = self._calculate_polarity(avg_emotion_scores)

        # 计算整体置信度
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0

        # DSA判定
        dsa_judgment = self._make_judgment(
            dominant_emotion, polarity_score, overall_confidence
        )

        return {
            'agent': 'DSA',
            'timestamp': datetime.now().isoformat(),
            'total_images': len(facepp_results),
            'valid_results': len(valid_results),
            'total_faces': total_faces,
            'avg_emotion_scores': avg_emotion_scores,
            'dominant_emotion': {
                'emotion': dominant_emotion[0],
                'score': dominant_emotion[1]
            },
            'polarity_score': polarity_score,
            'overall_confidence': overall_confidence,
            'dsa_judgment': dsa_judgment,
            'raw_data': facepp_results
        }

    def _calculate_polarity(self, emotion_scores: Dict[str, float]) -> float:
        """
        计算情绪极性分数

        Args:
            emotion_scores: 情绪分数字典

        Returns:
            float: 极性分数 (-1到1，负数表示负面情绪，正数表示正面情绪)
        """
        weighted_sum = 0
        total_weight = 0

        for emotion, score in emotion_scores.items():
            weight = self.emotion_weights.get(emotion.lower(), 0)
            weighted_sum += score * weight
            total_weight += score

        if total_weight == 0:
            return 0

        # 归一化到-1到1范围
        polarity = weighted_sum / total_weight
        return max(-1, min(1, polarity))

    def _make_judgment(self, dominant_emotion: Tuple[str, float],
                      polarity_score: float, confidence: float) -> Dict:
        """
        做出DSA判定

        Args:
            dominant_emotion: 主导情绪元组 (情绪名, 分数)
            polarity_score: 极性分数
            confidence: 置信度

        Returns:
            Dict: DSA判定结果
        """
        emotion_name, emotion_score = dominant_emotion

        # 判定情绪类别
        if polarity_score > 0.3:
            emotion_category = "positive"
            emotion_label = "积极"
        elif polarity_score < -0.3:
            emotion_category = "negative"
            emotion_label = "消极"
        else:
            emotion_category = "neutral"
            emotion_label = "中性"

        # 判定强度
        if emotion_score > 80:
            intensity = "very_high"
            intensity_label = "非常强烈"
        elif emotion_score > 60:
            intensity = "high"
            intensity_label = "强烈"
        elif emotion_score > 40:
            intensity = "medium"
            intensity_label = "中等"
        elif emotion_score > 20:
            intensity = "low"
            intensity_label = "轻微"
        else:
            intensity = "very_low"
            intensity_label = "非常轻微"

        # 判定可信度
        if confidence >= self.confidence_threshold:
            reliability = "high"
            reliability_label = "高可信"
        elif confidence >= 0.5:
            reliability = "medium"
            reliability_label = "中等可信"
        else:
            reliability = "low"
            reliability_label = "低可信"

        return {
            'emotion_category': emotion_category,
            'emotion_label': emotion_label,
            'dominant_emotion': emotion_name,
            'emotion_score': emotion_score,
            'polarity_score': polarity_score,
            'intensity': intensity,
            'intensity_label': intensity_label,
            'reliability': reliability,
            'reliability_label': reliability_label,
            'confidence': confidence,
            'summary': f"检测到{intensity_label}的{emotion_label}情绪，主要表现为{emotion_name}，可信度{reliability_label}"
        }

    def process_capture_directory(self) -> Dict:
        """
        处理capture目录中的图像并进行DSA分析

        Returns:
            Dict: DSA分析结果
        """
        logger.info("DSA开始处理capture目录...")

        # 调用Face++分析
        facepp_results = analyze_capture_directory()

        if not facepp_results:
            return {'error': 'Face++分析未返回结果'}

        # 进行DSA分析
        dsa_result = self.analyze_facepp_data(facepp_results)

        logger.info("DSA分析完成")
        return dsa_result

# 便捷函数
def run_dsa_analysis() -> Dict:
    """
    便捷函数：运行DSA分析

    Returns:
        Dict: DSA分析结果
    """
    agent = DSAAgent()
    return agent.process_capture_directory()

if __name__ == "__main__":
    # 测试代码
    result = run_dsa_analysis()
    print(f"DSA分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
