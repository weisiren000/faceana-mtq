"""
JSA智能体 (Joint Sentiment Analysis Agent)
综合情感分析智能体，负责融合DSA和VSA的分析结果，给出最终判定
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

from ..config import config
from .dsa import run_dsa_analysis
from .vsa import run_vsa_analysis

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class JSAAgent:
    """综合情感分析智能体"""

    def __init__(self):
        """初始化JSA智能体"""
        self.dsa_weight = config.JSA_WEIGHT_DSA  # DSA权重
        self.vsa_weight = config.JSA_WEIGHT_VSA  # VSA权重

        # 情绪一致性阈值
        self.consistency_threshold = 0.7

        # 标准化情绪映射
        self.emotion_mapping = {
            'happiness': 'happiness',
            'sadness': 'sadness',
            'anger': 'anger',
            'fear': 'fear',
            'surprise': 'surprise',
            'disgust': 'disgust',
            'neutral': 'neutral'
        }

        logger.info("JSA智能体初始化成功")

    def _normalize_emotion_data(self, agent_result: Dict, agent_type: str) -> Dict:
        """
        标准化智能体结果数据

        Args:
            agent_result: 智能体分析结果
            agent_type: 智能体类型 ('DSA' 或 'VSA')

        Returns:
            Dict: 标准化后的数据
        """
        if 'error' in agent_result:
            return {'error': agent_result['error'], 'agent': agent_type}

        judgment = agent_result.get(f'{agent_type.lower()}_judgment', {})

        return {
            'agent': agent_type,
            'emotion_category': judgment.get('emotion_category', 'neutral'),
            'emotion_label': judgment.get('emotion_label', '中性'),
            'dominant_emotion': judgment.get('dominant_emotion', 'neutral'),
            'polarity_score': agent_result.get('polarity_score', 0),
            'confidence': judgment.get('confidence', 0),
            'intensity': judgment.get('intensity', 'medium'),
            'intensity_label': judgment.get('intensity_label', '中等'),
            'reliability': judgment.get('reliability', 'medium'),
            'reliability_label': judgment.get('reliability_label', '中等可信'),
            'summary': judgment.get('summary', '无法获取摘要'),
            'raw_result': agent_result
        }

    def _calculate_emotion_consistency(self, dsa_data: Dict, vsa_data: Dict) -> Dict:
        """
        计算两个智能体的情绪一致性

        Args:
            dsa_data: DSA标准化数据
            vsa_data: VSA标准化数据

        Returns:
            Dict: 一致性分析结果
        """
        # 情绪类别一致性
        emotion_match = dsa_data['dominant_emotion'] == vsa_data['dominant_emotion']
        category_match = dsa_data['emotion_category'] == vsa_data['emotion_category']

        # 极性分数差异
        polarity_diff = abs(dsa_data['polarity_score'] - vsa_data['polarity_score'])
        polarity_consistency = 1 - min(1, polarity_diff / 2)  # 归一化到0-1

        # 置信度差异
        confidence_diff = abs(dsa_data['confidence'] - vsa_data['confidence'])
        confidence_consistency = 1 - min(1, confidence_diff)

        # 综合一致性分数
        consistency_score = (
            (0.4 if emotion_match else 0) +
            (0.3 if category_match else 0) +
            (0.2 * polarity_consistency) +
            (0.1 * confidence_consistency)
        )

        # 一致性等级
        if consistency_score >= 0.8:
            consistency_level = "very_high"
            consistency_label = "非常高"
        elif consistency_score >= 0.6:
            consistency_level = "high"
            consistency_label = "高"
        elif consistency_score >= 0.4:
            consistency_level = "medium"
            consistency_label = "中等"
        elif consistency_score >= 0.2:
            consistency_level = "low"
            consistency_label = "低"
        else:
            consistency_level = "very_low"
            consistency_label = "非常低"

        return {
            'emotion_match': emotion_match,
            'category_match': category_match,
            'polarity_consistency': polarity_consistency,
            'confidence_consistency': confidence_consistency,
            'consistency_score': consistency_score,
            'consistency_level': consistency_level,
            'consistency_label': consistency_label
        }

    def _make_final_judgment(self, dsa_data: Dict, vsa_data: Dict,
                           consistency: Dict) -> Dict:
        """
        做出最终综合判定

        Args:
            dsa_data: DSA标准化数据
            vsa_data: VSA标准化数据
            consistency: 一致性分析结果

        Returns:
            Dict: 最终判定结果
        """
        # 加权计算最终极性分数
        final_polarity = (
            dsa_data['polarity_score'] * self.dsa_weight +
            vsa_data['polarity_score'] * self.vsa_weight
        )

        # 加权计算最终置信度
        final_confidence = (
            dsa_data['confidence'] * self.dsa_weight +
            vsa_data['confidence'] * self.vsa_weight
        )

        # 根据一致性调整置信度
        consistency_bonus = consistency['consistency_score'] * 0.2
        adjusted_confidence = min(1.0, final_confidence + consistency_bonus)

        # 确定最终情绪
        if consistency['emotion_match']:
            # 两个智能体一致
            final_emotion = dsa_data['dominant_emotion']
            decision_basis = "两智能体一致判定"
        else:
            # 两个智能体不一致，根据权重和置信度决定
            dsa_score = dsa_data['confidence'] * self.dsa_weight
            vsa_score = vsa_data['confidence'] * self.vsa_weight

            if dsa_score > vsa_score:
                final_emotion = dsa_data['dominant_emotion']
                decision_basis = f"DSA权重更高 ({dsa_score:.2f} > {vsa_score:.2f})"
            else:
                final_emotion = vsa_data['dominant_emotion']
                decision_basis = f"VSA权重更高 ({vsa_score:.2f} > {dsa_score:.2f})"

        # 确定最终情绪类别
        if final_polarity > 0.3:
            final_category = "positive"
            final_label = "积极"
        elif final_polarity < -0.3:
            final_category = "negative"
            final_label = "消极"
        else:
            final_category = "neutral"
            final_label = "中性"

        # 确定最终强度
        avg_intensity_score = (
            (0.8 if dsa_data['intensity'] in ['high', 'very_high'] else
             0.6 if dsa_data['intensity'] == 'medium' else 0.4) * self.dsa_weight +
            (0.8 if vsa_data['intensity'] in ['high', 'very_high'] else
             0.6 if vsa_data['intensity'] == 'medium' else 0.4) * self.vsa_weight
        )

        if avg_intensity_score > 0.7:
            final_intensity = "high"
            final_intensity_label = "强烈"
        elif avg_intensity_score > 0.5:
            final_intensity = "medium"
            final_intensity_label = "中等"
        else:
            final_intensity = "low"
            final_intensity_label = "轻微"

        # 确定最终可信度
        if adjusted_confidence >= 0.8:
            final_reliability = "high"
            final_reliability_label = "高可信"
        elif adjusted_confidence >= 0.6:
            final_reliability = "medium"
            final_reliability_label = "中等可信"
        else:
            final_reliability = "low"
            final_reliability_label = "低可信"

        return {
            'final_emotion': final_emotion,
            'final_category': final_category,
            'final_label': final_label,
            'final_polarity': final_polarity,
            'final_confidence': final_confidence,
            'adjusted_confidence': adjusted_confidence,
            'final_intensity': final_intensity,
            'final_intensity_label': final_intensity_label,
            'final_reliability': final_reliability,
            'final_reliability_label': final_reliability_label,
            'decision_basis': decision_basis,
            'weights_used': {
                'dsa_weight': self.dsa_weight,
                'vsa_weight': self.vsa_weight
            },
            'summary': f"综合判定：{final_intensity_label}的{final_label}情绪，主要表现为{final_emotion}，{final_reliability_label}（{decision_basis}）"
        }

    def analyze_combined_results(self, dsa_result: Dict, vsa_result: Dict) -> Dict:
        """
        分析DSA和VSA的综合结果

        Args:
            dsa_result: DSA分析结果
            vsa_result: VSA分析结果

        Returns:
            Dict: JSA综合分析结果
        """
        logger.info("JSA开始综合分析...")

        # 标准化数据
        dsa_data = self._normalize_emotion_data(dsa_result, 'DSA')
        vsa_data = self._normalize_emotion_data(vsa_result, 'VSA')

        # 检查错误
        if 'error' in dsa_data and 'error' in vsa_data:
            return {'error': 'DSA和VSA都分析失败'}
        elif 'error' in dsa_data:
            logger.warning("DSA分析失败，仅使用VSA结果")
            return {
                'agent': 'JSA',
                'timestamp': datetime.now().isoformat(),
                'warning': 'DSA分析失败，仅使用VSA结果',
                'final_judgment': vsa_data,
                'dsa_result': dsa_data,
                'vsa_result': vsa_data
            }
        elif 'error' in vsa_data:
            logger.warning("VSA分析失败，仅使用DSA结果")
            return {
                'agent': 'JSA',
                'timestamp': datetime.now().isoformat(),
                'warning': 'VSA分析失败，仅使用DSA结果',
                'final_judgment': dsa_data,
                'dsa_result': dsa_data,
                'vsa_result': vsa_data
            }

        # 计算一致性
        consistency = self._calculate_emotion_consistency(dsa_data, vsa_data)

        # 做出最终判定
        final_judgment = self._make_final_judgment(dsa_data, vsa_data, consistency)

        return {
            'agent': 'JSA',
            'timestamp': datetime.now().isoformat(),
            'dsa_analysis': dsa_data,
            'vsa_analysis': vsa_data,
            'consistency_analysis': consistency,
            'final_judgment': final_judgment,
            'processing_summary': {
                'dsa_available': True,
                'vsa_available': True,
                'consistency_score': consistency['consistency_score'],
                'consistency_label': consistency['consistency_label'],
                'decision_method': 'weighted_fusion'
            }
        }

    def process_capture_directory(self) -> Dict:
        """
        处理capture目录并进行完整的JSA分析

        Returns:
            Dict: JSA分析结果
        """
        logger.info("JSA开始完整分析流程...")

        try:
            # 并行运行DSA和VSA
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor(max_workers=2) as executor:
                dsa_future = executor.submit(run_dsa_analysis)
                vsa_future = executor.submit(run_vsa_analysis)

                dsa_result = dsa_future.result()
                vsa_result = vsa_future.result()

            # 综合分析
            jsa_result = self.analyze_combined_results(dsa_result, vsa_result)

            logger.info("JSA完整分析流程完成")
            return jsa_result

        except Exception as e:
            error_msg = f"JSA分析失败: {e}"
            logger.error(error_msg)
            return {'error': error_msg}

# 便捷函数
def run_jsa_analysis() -> Dict:
    """
    便捷函数：运行JSA综合分析

    Returns:
        Dict: JSA分析结果
    """
    agent = JSAAgent()
    return agent.process_capture_directory()

def run_complete_emotion_analysis() -> Dict:
    """
    便捷函数：运行完整的情绪分析流程
    包括图像捕获、标注、拼接和三智能体分析

    Returns:
        Dict: 完整分析结果
    """
    from ..core.capture import capture_face_images
    from ..core.tagger import tag_face_images
    from ..core.splicer import splice_images
    from ..core.cleaner import clean_capture_files, clean_tagger_files

    logger.info("开始完整情绪分析流程...")

    try:
        # 1. 图像捕获
        logger.info("步骤1: 图像捕获")
        captured_files = capture_face_images()
        if not captured_files:
            return {'error': '图像捕获失败'}

        # 2. 人脸标注
        logger.info("步骤2: 人脸标注")
        tagged_results = tag_face_images()
        if not tagged_results:
            return {'error': '人脸标注失败'}

        # 3. 图像拼接
        logger.info("步骤3: 图像拼接")
        spliced_result = splice_images()
        if not spliced_result:
            return {'error': '图像拼接失败'}

        # 4. JSA综合分析
        logger.info("步骤4: JSA综合分析")
        jsa_result = run_jsa_analysis()

        # 5. 清理临时文件
        logger.info("步骤5: 清理临时文件")
        clean_capture_files()
        clean_tagger_files()

        # 组合完整结果
        complete_result = {
            'workflow': 'complete_emotion_analysis',
            'timestamp': datetime.now().isoformat(),
            'steps': {
                'capture': {
                    'status': 'success',
                    'files_count': len(captured_files),
                    'files': captured_files
                },
                'tagging': {
                    'status': 'success',
                    'results_count': len(tagged_results),
                    'results': tagged_results
                },
                'splicing': {
                    'status': 'success',
                    'result_file': spliced_result
                },
                'analysis': jsa_result,
                'cleanup': {
                    'status': 'success'
                }
            },
            'final_result': jsa_result.get('final_judgment', {}),
            'summary': jsa_result.get('final_judgment', {}).get('summary', '分析完成')
        }

        logger.info("完整情绪分析流程成功完成")
        return complete_result

    except Exception as e:
        error_msg = f"完整分析流程失败: {e}"
        logger.error(error_msg)
        return {'error': error_msg}

if __name__ == "__main__":
    # 测试代码
    result = run_jsa_analysis()
    print(f"JSA分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
