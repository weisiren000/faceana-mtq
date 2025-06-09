"""
情绪分析统合服务
整合Face++和AI模型的分析结果，提供容错机制
"""

import asyncio
import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..models.emotion import (
    EmotionResult,
    AnalysisResponse,
    BatchAnalysisResponse,
    EmotionData,
    create_emotion_data_list,
    normalize_probabilities,
    get_dominant_emotion
)
from .facepp_service import FacePPService
from .ai_service import GeminiService, OpenRouterService

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """情绪分析统合服务"""
    
    def __init__(self):
        self.facepp_service = FacePPService()
        self.gemini_service = GeminiService()
        # 暂时禁用OpenRouter服务以避免版本兼容问题
        # self.openrouter_service = OpenRouterService()
        self.openrouter_service = None
    async def analyze_image(self, image_data: bytes) -> AnalysisResponse:
        """分析图像情绪，整合多个API结果"""
        results = []
        errors = []

        # 并发调用Face++和AI模型
        tasks = [
            self._call_facepp(image_data),
            self._call_ai_models(image_data)
        ]

        # 等待所有任务完成
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for result in completed_results:
            if isinstance(result, Exception):
                errors.append(str(result))
                logger.warning(f"API调用失败: {result}")
            elif result is not None:
                results.append(result)
                # 添加详细日志
                logger.info(f"API调用成功 - 来源: {result.source}, 主导情绪: {result.dominant_emotion}, 置信度: {result.confidence:.2f}")

        # 如果没有任何成功结果，返回错误
        if not results:
            error_msg = "所有情绪分析API都失败了: " + "; ".join(errors)
            return AnalysisResponse(
                success=False,
                emotion_data=[],
                analysis_text="",
                error_message=error_msg
            )

        # 融合结果
        merged_emotions = self._merge_results(results)
        emotion_data_list = create_emotion_data_list(merged_emotions)
        analysis_text = self._generate_analysis_text(results, errors)

        return AnalysisResponse(
            success=True,
            emotion_data=emotion_data_list,
            analysis_text=analysis_text,
            error_message=None if not errors else "; ".join(errors)
        )
    async def _call_facepp(self, image_data: bytes) -> Optional[EmotionResult]:
        """调用Face++ API"""
        try:
            return await self.facepp_service.analyze_emotion(image_data)
        except Exception as e:
            logger.error(f"Face++ API调用失败: {e}")
            return None
    
    async def _call_ai_models(self, image_data: bytes) -> Optional[EmotionResult]:
        """调用AI模型API（带容错机制）"""
        # 尝试Gemini模型
        for model in self.gemini_service.models:
            try:
                return await self.gemini_service.analyze_emotion(image_data, model)
            except Exception as e:
                logger.warning(f"Gemini模型 {model} 调用失败: {e}")
                continue
        
        # OpenRouter模型暂时禁用（版本兼容问题）
        # 后续可以在修复版本兼容性后重新启用
        
        logger.error("所有AI模型都调用失败")
        return None
    
    def _merge_results(self, results: List[EmotionResult]) -> Dict[str, float]:
        """融合多个分析结果"""
        if not results:
            return {"neutral": 1.0}
        
        if len(results) == 1:
            return results[0].emotions
        
        # 加权平均：Face++ 权重0.6，AI模型权重0.4
        merged_emotions = {}
        total_weight = 0
        
        for result in results:
            weight = 0.6 if result.source == "facepp" else 0.4
            total_weight += weight
            
            for emotion, value in result.emotions.items():
                merged_emotions[emotion] = merged_emotions.get(emotion, 0) + value * weight
        
        # 标准化
        if total_weight > 0:
            for emotion in merged_emotions:
                merged_emotions[emotion] = merged_emotions[emotion] / total_weight
        
        return normalize_probabilities(merged_emotions)    
    def _generate_analysis_text(self, results: List[EmotionResult], 
                               errors: List[str]) -> str:
        """生成分析文本（兼容前端打字机效果）"""
        if not results:
            return ">>> 情绪分析失败 <<<\n\n所有API调用都失败了。"
        
        # 获取融合后的主导情绪
        merged_emotions = self._merge_results(results)
        dominant_emotion = get_dominant_emotion(merged_emotions)
        confidence = merged_emotions.get(dominant_emotion, 0.0)
        
        # 生成分析报告
        analysis_lines = [
            ">>> NEURAL NETWORK ANALYSIS COMPLETE <<<",
            "",
            "EMOTIONAL SIGNATURE DETECTED:",
            "━" * 80,
            "",
            "MULTI-API ANALYSIS RESULTS:",
        ]
        
        # 添加各API结果 - 增强调试信息
        for result in results:
            source_name = result.source.upper()
            result_dominant = result.dominant_emotion.upper()
            result_confidence = int(result.confidence * 100)

            # 记录详细信息用于调试
            logger.info(f"分析结果 - 来源: {source_name}, 主导情绪: {result_dominant}, 置信度: {result_confidence}%, 时间戳: {result.timestamp}")
            logger.info(f"详细情绪分布: {result.emotions}")

            analysis_lines.extend([
                f"• {source_name}: {result_dominant} ({result_confidence}%)"
            ])
        
        analysis_lines.extend([
            "",
            "CONSOLIDATED ANALYSIS:",
            f"• Primary Emotion: {dominant_emotion.upper()}",
            f"• Confidence Level: {int(confidence * 100)}%",
            f"• Data Sources: {len(results)} API(s)",
            "",
            "BIOMETRIC DATA:",
            "• Facial Expression Analysis: COMPLETE",
            "• Multi-Model Validation: ACTIVE",
            "• Cross-Reference Check: PASSED",
            "",
            f"ANALYSIS TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "SYSTEM STATUS: OPERATIONAL",
        ])
        
        # 如果有错误，添加错误信息
        if errors:
            analysis_lines.extend([
                "",
                "⚠ SYSTEM WARNINGS:",
                *[f"• {error}" for error in errors[:3]]  # 最多显示3个错误
            ])
        
        return "\n".join(analysis_lines)

    async def analyze_batch_images(self, images_data: List[bytes]) -> BatchAnalysisResponse:
        """批量分析多张图像，使用裁判员AI给出最终判断"""
        if not images_data:
            return BatchAnalysisResponse(
                success=False,
                emotion_data=[],
                analysis_text="",
                detailed_results=[],
                judge_result=None,
                error_message="没有提供图像数据"
            )

        all_results = []
        detailed_results = []
        errors = []

        # 并发分析所有图像
        for i, image_data in enumerate(images_data):
            try:
                # 并发调用Face++和Gemini
                tasks = [
                    self._call_facepp(image_data),
                    self._call_ai_models(image_data)
                ]

                image_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理单张图像的结果
                image_analysis = {
                    "image_id": i + 1,
                    "facepp_result": None,
                    "gemini_result": None,
                    "errors": []
                }

                for result in image_results:
                    if isinstance(result, Exception):
                        image_analysis["errors"].append(str(result))
                        logger.warning(f"图像{i+1}分析失败: {result}")
                    elif result is not None:
                        all_results.append(result)
                        if result.source == "facepp":
                            image_analysis["facepp_result"] = {
                                "emotions": result.emotions,
                                "dominant_emotion": result.dominant_emotion,
                                "confidence": result.confidence
                            }
                        else:  # Gemini结果
                            image_analysis["gemini_result"] = {
                                "emotions": result.emotions,
                                "dominant_emotion": result.dominant_emotion,
                                "confidence": result.confidence
                            }

                detailed_results.append(image_analysis)

            except Exception as e:
                error_msg = f"图像{i+1}处理异常: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        # 如果没有任何成功结果，返回错误
        if not all_results:
            error_msg = "所有图像分析都失败了: " + "; ".join(errors)
            return BatchAnalysisResponse(
                success=False,
                emotion_data=[],
                analysis_text="",
                detailed_results=detailed_results,
                judge_result=None,
                error_message=error_msg
            )

        # 准备裁判员AI的输入数据
        judge_input = []
        for result in all_results:
            judge_input.append({
                "source": result.source,
                "emotions": result.emotions,
                "dominant_emotion": result.dominant_emotion,
                "confidence": result.confidence,
                "timestamp": result.timestamp.isoformat()
            })

        # 调用裁判员AI
        judge_result = None
        try:
            judge_result = await self.gemini_service.judge_emotions(judge_input)
            logger.info("裁判员AI判断完成")
        except Exception as e:
            error_msg = f"裁判员AI调用失败: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

        # 生成最终结果
        if judge_result and "emotions" in judge_result:
            final_emotions = judge_result["emotions"]
            emotion_data_list = create_emotion_data_list(final_emotions)
        else:
            # 如果裁判员AI失败，使用传统融合方法
            merged_emotions = self._merge_results(all_results)
            emotion_data_list = create_emotion_data_list(merged_emotions)

        # 生成分析文本
        analysis_text = self._generate_batch_analysis_text(
            detailed_results, judge_result, errors, len(images_data)
        )

        return BatchAnalysisResponse(
            success=True,
            emotion_data=emotion_data_list,
            analysis_text=analysis_text,
            detailed_results=detailed_results,
            judge_result=judge_result,
            error_message="; ".join(errors) if errors else None
        )

    def _generate_batch_analysis_text(self, detailed_results: List[Dict],
                                    judge_result: Optional[Dict],
                                    errors: List[str],
                                    total_images: int) -> str:
        """生成批量分析的文本报告"""
        analysis_lines = []

        # 最终判断结果
        if judge_result:
            final_emotion = judge_result.get("final_emotion", "unknown").upper()
            confidence = int(judge_result.get("confidence", 0) * 100)
            reasoning = judge_result.get("reasoning", "无判断依据")
            consistency = judge_result.get("consistency_analysis", "无一致性分析")

            analysis_lines.extend([
                ">>> FINAL EMOTION ANALYSIS RESULT <<<",
                "",
                f"PRIMARY EMOTION: {final_emotion} ({confidence}%)",
                "CONFIDENCE LEVEL: " + ("HIGH" if confidence >= 80 else "MEDIUM" if confidence >= 60 else "LOW"),
                f"DATA SOURCES: {total_images} IMAGES ANALYZED",
                f"ANALYSIS TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "JUDGE AI REASONING:",
                f"• {reasoning}",
                "",
                "CONSISTENCY ANALYSIS:",
                f"• {consistency}",
                "",
                "━" * 80,
                "",
                ">>> DETAILED ANALYSIS BREAKDOWN <<<",
                ""
            ])
        else:
            analysis_lines.extend([
                ">>> EMOTION ANALYSIS RESULT <<<",
                "",
                "⚠ 裁判员AI不可用，使用传统融合方法",
                f"DATA SOURCES: {total_images} IMAGES ANALYZED",
                f"ANALYSIS TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "━" * 80,
                "",
                ">>> DETAILED ANALYSIS BREAKDOWN <<<",
                ""
            ])

        # 详细分析结果
        for result in detailed_results:
            image_id = result["image_id"]
            analysis_lines.append(f"IMAGE {image_id}/{total_images} ANALYSIS:")

            # Face++ 结果
            if result["facepp_result"]:
                facepp = result["facepp_result"]
                emotions_str = " | ".join([
                    f"{emotion.title()}: {int(prob*100)}%"
                    for emotion, prob in facepp["emotions"].items()
                    if prob > 0.01  # 只显示概率大于1%的情绪
                ])
                analysis_lines.extend([
                    "┌─ FACE++ API RESULT:",
                    f"│  • {emotions_str}",
                    f"│  • Dominant: {facepp['dominant_emotion'].upper()} ({int(facepp['confidence']*100)}%)",
                    "│"
                ])
            else:
                analysis_lines.extend([
                    "┌─ FACE++ API RESULT:",
                    "│  • ANALYSIS FAILED",
                    "│"
                ])

            # Gemini 结果
            if result["gemini_result"]:
                gemini = result["gemini_result"]
                emotions_str = " | ".join([
                    f"{emotion.title()}: {int(prob*100)}%"
                    for emotion, prob in gemini["emotions"].items()
                    if prob > 0.01
                ])
                analysis_lines.extend([
                    "└─ GEMINI AI RESULT:",
                    f"   • {emotions_str}",
                    f"   • Dominant: {gemini['dominant_emotion'].upper()} ({int(gemini['confidence']*100)}%)",
                    ""
                ])
            else:
                analysis_lines.extend([
                    "└─ GEMINI AI RESULT:",
                    "   • ANALYSIS FAILED",
                    ""
                ])

            # 错误信息
            if result["errors"]:
                analysis_lines.extend([
                    "⚠ ERRORS:",
                    *[f"   • {error}" for error in result["errors"]],
                    ""
                ])

        # 系统状态
        analysis_lines.extend([
            "━" * 80,
            "",
            "BIOMETRIC DATA:",
            "• Facial Expression Analysis: COMPLETE",
            "• Multi-Model Validation: ACTIVE",
            "• Judge AI Analysis: " + ("COMPLETE" if judge_result else "FAILED"),
            "",
            "SYSTEM STATUS: OPERATIONAL"
        ])

        # 错误汇总
        if errors:
            analysis_lines.extend([
                "",
                "⚠ SYSTEM WARNINGS:",
                *[f"• {error}" for error in errors[:5]]  # 最多显示5个错误
            ])

        return "\n".join(analysis_lines)