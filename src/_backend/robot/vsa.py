"""
VSA智能体 (Visual Sentiment Analysis Agent)
视觉情感分析智能体，专注于整合多个AI模型的图像视觉分析结果
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..config import config
from ..api.openrouter import analyze_capture_with_openrouter
from ..api.gemini import analyze_capture_with_gemini

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class VSAAgent:
    """视觉情感分析智能体"""

    def __init__(self):
        """初始化VSA智能体"""
        self.confidence_threshold = config.VSA_CONFIDENCE_THRESHOLD
        self.emotion_mapping = {
            # 标准化情绪映射
            '快乐': 'happiness',
            '悲伤': 'sadness',
            '愤怒': 'anger',
            '恐惧': 'fear',
            '惊讶': 'surprise',
            '厌恶': 'disgust',
            '中性': 'neutral',
            'happiness': 'happiness',
            'sadness': 'sadness',
            'anger': 'anger',
            'fear': 'fear',
            'surprise': 'surprise',
            'disgust': 'disgust',
            'neutral': 'neutral'
        }

        self.emotion_weights = {
            'happiness': 1.0,
            'sadness': -0.8,
            'anger': -0.9,
            'fear': -0.7,
            'surprise': 0.3,
            'disgust': -0.6,
            'neutral': 0.0
        }

        logger.info("VSA智能体初始化成功")

    def _extract_emotion_from_ai_response(self, ai_result: Dict) -> Dict:
        """
        从AI响应中提取情绪信息

        Args:
            ai_result: AI分析结果

        Returns:
            Dict: 提取的情绪信息
        """
        if 'error' in ai_result:
            return {'error': ai_result['error']}

        emotion_analysis = ai_result.get('emotion_analysis', {})

        # 处理结构化响应
        if isinstance(emotion_analysis, dict) and 'primary_emotion' in emotion_analysis:
            primary_emotion = emotion_analysis.get('primary_emotion', 'neutral')
            intensity = emotion_analysis.get('emotion_intensity', 5)
            confidence = emotion_analysis.get('confidence', 5)

            # 标准化情绪名称
            normalized_emotion = self.emotion_mapping.get(primary_emotion.lower(), 'neutral')

            return {
                'primary_emotion': normalized_emotion,
                'intensity': intensity / 10.0,  # 归一化到0-1
                'confidence': confidence / 10.0,  # 归一化到0-1
                'raw_analysis': emotion_analysis
            }

        # 处理原始文本响应
        elif isinstance(emotion_analysis, dict) and 'raw_response' in emotion_analysis:
            raw_text = emotion_analysis['raw_response']
            return self._parse_text_response(raw_text)

        else:
            return {'error': '无法解析AI响应'}

    def _parse_text_response(self, text: str) -> Dict:
        """
        解析文本响应中的情绪信息

        Args:
            text: 原始文本响应

        Returns:
            Dict: 解析的情绪信息
        """
        text_lower = text.lower()

        # 简单的关键词匹配
        emotion_keywords = {
            'happiness': ['快乐', '开心', '高兴', '愉快', '喜悦', 'happy', 'joy', 'smile'],
            'sadness': ['悲伤', '难过', '沮丧', '忧郁', 'sad', 'sorrow', 'grief'],
            'anger': ['愤怒', '生气', '恼怒', 'angry', 'rage', 'fury'],
            'fear': ['恐惧', '害怕', '担心', 'fear', 'afraid', 'scared'],
            'surprise': ['惊讶', '意外', 'surprise', 'shocked', 'amazed'],
            'disgust': ['厌恶', '恶心', 'disgust', 'revulsion'],
            'neutral': ['中性', '平静', '无表情', 'neutral', 'calm']
        }

        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            confidence = min(1.0, emotion_scores[primary_emotion] / 3)  # 简单的置信度计算
        else:
            primary_emotion = 'neutral'
            confidence = 0.3

        return {
            'primary_emotion': primary_emotion,
            'intensity': 0.5,  # 默认中等强度
            'confidence': confidence,
            'raw_analysis': {'text_response': text}
        }

    def _calculate_visual_polarity(self, emotion_scores: Dict) -> float:
        """
        计算视觉情绪极性分数

        Args:
            emotion_scores: 情绪分数字典

        Returns:
            float: 极性分数 (-1到1)
        """
        weighted_sum = 0
        total_weight = 0

        for emotion, data in emotion_scores.items():
            weight = self.emotion_weights.get(emotion, 0)
            intensity = data['avg_intensity']
            count_weight = data['weight']

            weighted_sum += weight * intensity * count_weight
            total_weight += count_weight

        if total_weight == 0:
            return 0

        return max(-1, min(1, weighted_sum))

    def analyze_ai_results(self, openrouter_results: List[Dict],
                          gemini_results: List[Dict]) -> Dict:
        """
        分析AI模型的结果

        Args:
            openrouter_results: OpenRouter分析结果
            gemini_results: Gemini分析结果

        Returns:
            Dict: VSA分析结果
        """
        logger.info("VSA开始分析AI模型结果...")

        # 处理OpenRouter结果
        openrouter_emotions = []
        for result in openrouter_results:
            emotion_info = self._extract_emotion_from_ai_response(result)
            if 'error' not in emotion_info:
                emotion_info['source'] = 'openrouter'
                emotion_info['model'] = result.get('model', 'unknown')
                openrouter_emotions.append(emotion_info)

        # 处理Gemini结果
        gemini_emotions = []
        for result in gemini_results:
            emotion_info = self._extract_emotion_from_ai_response(result)
            if 'error' not in emotion_info:
                emotion_info['source'] = 'gemini'
                emotion_info['model'] = result.get('model', 'unknown')
                gemini_emotions.append(emotion_info)

        # 合并所有情绪分析结果
        all_emotions = openrouter_emotions + gemini_emotions

        if not all_emotions:
            return {'error': '没有有效的AI分析结果'}

        # 计算综合情绪分析
        emotion_counts = {}
        total_intensity = 0
        total_confidence = 0

        for emotion_info in all_emotions:
            emotion = emotion_info['primary_emotion']
            intensity = emotion_info['intensity']
            confidence = emotion_info['confidence']

            if emotion not in emotion_counts:
                emotion_counts[emotion] = {'count': 0, 'total_intensity': 0, 'total_confidence': 0}

            emotion_counts[emotion]['count'] += 1
            emotion_counts[emotion]['total_intensity'] += intensity
            emotion_counts[emotion]['total_confidence'] += confidence

            total_intensity += intensity
            total_confidence += confidence

        # 计算平均值
        avg_emotion_scores = {}
        for emotion, data in emotion_counts.items():
            avg_emotion_scores[emotion] = {
                'count': data['count'],
                'avg_intensity': data['total_intensity'] / data['count'],
                'avg_confidence': data['total_confidence'] / data['count'],
                'weight': data['count'] / len(all_emotions)
            }

        # 确定主导情绪（基于出现次数和平均强度）
        dominant_emotion = max(
            avg_emotion_scores.items(),
            key=lambda x: x[1]['count'] * x[1]['avg_intensity']
        )

        # 计算情绪极性分数
        polarity_score = self._calculate_visual_polarity(avg_emotion_scores)

        # 计算整体置信度
        overall_confidence = total_confidence / len(all_emotions) if all_emotions else 0

        # VSA判定
        vsa_judgment = self._make_visual_judgment(
            dominant_emotion, polarity_score, overall_confidence, len(all_emotions)
        )

        return {
            'agent': 'VSA',
            'timestamp': datetime.now().isoformat(),
            'total_ai_results': len(openrouter_results) + len(gemini_results),
            'valid_emotions': len(all_emotions),
            'openrouter_count': len(openrouter_emotions),
            'gemini_count': len(gemini_emotions),
            'emotion_analysis': avg_emotion_scores,
            'dominant_emotion': {
                'emotion': dominant_emotion[0],
                'data': dominant_emotion[1]
            },
            'polarity_score': polarity_score,
            'overall_confidence': overall_confidence,
            'vsa_judgment': vsa_judgment,
            'detailed_results': {
                'openrouter': openrouter_emotions,
                'gemini': gemini_emotions
            }
        }

    def _make_visual_judgment(self, dominant_emotion: Tuple, polarity_score: float,
                             confidence: float, sample_size: int) -> Dict:
        """
        做出VSA判定

        Args:
            dominant_emotion: 主导情绪元组
            polarity_score: 极性分数
            confidence: 置信度
            sample_size: 样本数量

        Returns:
            Dict: VSA判定结果
        """
        emotion_name, emotion_data = dominant_emotion

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
        avg_intensity = emotion_data['avg_intensity']
        if avg_intensity > 0.8:
            intensity = "very_high"
            intensity_label = "非常强烈"
        elif avg_intensity > 0.6:
            intensity = "high"
            intensity_label = "强烈"
        elif avg_intensity > 0.4:
            intensity = "medium"
            intensity_label = "中等"
        elif avg_intensity > 0.2:
            intensity = "low"
            intensity_label = "轻微"
        else:
            intensity = "very_low"
            intensity_label = "非常轻微"

        # 判定可信度（考虑样本数量）
        adjusted_confidence = confidence * min(1.0, sample_size / 5)  # 样本数量调整

        if adjusted_confidence >= self.confidence_threshold:
            reliability = "high"
            reliability_label = "高可信"
        elif adjusted_confidence >= 0.4:
            reliability = "medium"
            reliability_label = "中等可信"
        else:
            reliability = "low"
            reliability_label = "低可信"

        # 一致性评估
        consistency = emotion_data['count'] / sample_size if sample_size > 0 else 0
        if consistency > 0.7:
            consistency_label = "高一致性"
        elif consistency > 0.5:
            consistency_label = "中等一致性"
        else:
            consistency_label = "低一致性"

        return {
            'emotion_category': emotion_category,
            'emotion_label': emotion_label,
            'dominant_emotion': emotion_name,
            'avg_intensity': avg_intensity,
            'polarity_score': polarity_score,
            'intensity': intensity,
            'intensity_label': intensity_label,
            'reliability': reliability,
            'reliability_label': reliability_label,
            'confidence': confidence,
            'adjusted_confidence': adjusted_confidence,
            'consistency': consistency,
            'consistency_label': consistency_label,
            'sample_size': sample_size,
            'summary': f"通过{sample_size}个AI模型分析，检测到{intensity_label}的{emotion_label}情绪，主要表现为{emotion_name}，{consistency_label}，可信度{reliability_label}"
        }

    def process_capture_directory(self) -> Dict:
        """
        处理capture目录中的图像并进行VSA分析

        Returns:
            Dict: VSA分析结果
        """
        logger.info("VSA开始处理capture目录...")

        try:
            # 并行调用多个AI API
            with ThreadPoolExecutor(max_workers=2) as executor:
                # 提交任务
                openrouter_future = executor.submit(analyze_capture_with_openrouter)
                gemini_future = executor.submit(analyze_capture_with_gemini)

                # 获取结果
                openrouter_results = openrouter_future.result()
                gemini_results = gemini_future.result()

            # 分析结果
            vsa_result = self.analyze_ai_results(openrouter_results, gemini_results)

            logger.info("VSA分析完成")
            return vsa_result

        except Exception as e:
            error_msg = f"VSA处理失败: {e}"
            logger.error(error_msg)
            return {'error': error_msg}

# 便捷函数
def run_vsa_analysis() -> Dict:
    """
    便捷函数：运行VSA分析

    Returns:
        Dict: VSA分析结果
    """
    agent = VSAAgent()
    return agent.process_capture_directory()

if __name__ == "__main__":
    # 测试代码
    result = run_vsa_analysis()
    print(f"VSA分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")