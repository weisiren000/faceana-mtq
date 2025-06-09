"""
AI模型服务
支持Gemini和OpenRouter API进行情绪分析
"""

import os
import json
import base64
import requests
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
from openai import OpenAI

from ..models.emotion import (
    EmotionResult,
    AI_EMOTION_MAPPING,
    normalize_probabilities,
    get_dominant_emotion,
    json_to_emotions
)

logger = logging.getLogger(__name__)


# 标准化的情绪分析Prompt
EMOTION_ANALYSIS_PROMPT = """
请分析这张图片中人物的情绪，严格按照以下JSON格式返回：

{
  "emotions": {
    "angry": 0.0到1.0之间的数值,
    "disgusted": 0.0到1.0之间的数值,
    "fearful": 0.0到1.0之间的数值,
    "happy": 0.0到1.0之间的数值,
    "neutral": 0.0到1.0之间的数值,
    "sad": 0.0到1.0之间的数值,
    "surprised": 0.0到1.0之间的数值
  },
  "dominant_emotion": "主导情绪名称(英文小写)",
  "confidence": 0.0到1.0之间的置信度
}

要求：
1. 所有情绪概率之和必须等于1.0
2. 只返回JSON格式，不要其他文字
3. 情绪名称必须使用英文小写
4. 仔细观察面部表情、眼神、嘴角等细节
"""

# 裁判员AI的Prompt
JUDGE_AI_PROMPT = """
你是专业的情绪分析裁判员。分析多个AI的情绪识别结果，给出最终判断。

**重要：你必须只返回JSON格式，不要任何解释文字！**

输入数据格式：
- Face++ API结果：每张图片的情绪概率
- Gemini AI结果：每张图片的情绪概率

分析原则：
1. 综合所有结果的一致性
2. 排除明显异常值
3. Face++和Gemini权重相等
4. 结果差异大时降低置信度
5. 情绪概率总和必须为1.0

**输出格式（必须是纯JSON）：**

```json
{
  "final_emotion": "happy",
  "confidence": 0.85,
  "reasoning": "5张图片中4张显示快乐情绪，Face++和Gemini结果高度一致",
  "consistency_analysis": "各API结果差异较小，判断可信度高",
  "emotions": {
    "angry": 0.05,
    "disgusted": 0.02,
    "fearful": 0.03,
    "happy": 0.75,
    "neutral": 0.10,
    "sad": 0.03,
    "surprised": 0.02
  }
}
```

**再次强调：只返回JSON，不要任何其他文字！**
"""
class GeminiService:
    """Gemini API服务类"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDliXeDpoK1vTj-4wWPHkSP5Akaf-wMYPs")
        self.models = [
            "gemma-3-27b-it",
            "gemini-2.0-flash-lite-001",
            "gemini-2.0-flash-lite"
        ]
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def encode_image(self, image_data: bytes) -> str:
        """将图像编码为base64"""
        return base64.b64encode(image_data).decode("utf-8")
    
    async def analyze_emotion(self, image_data: bytes, model: Optional[str] = None) -> EmotionResult:
        """使用Gemini分析情绪"""
        if model is None:
            model = self.models[0]
            
        try:
            image_base64 = self.encode_image(image_data)
            
            url = f"{self.base_url}/{model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}
            
            data = {
                "contents": [{
                    "parts": [
                        {"text": EMOTION_ANALYSIS_PROMPT},
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(url, headers=headers, params=params, 
                                   json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应
            candidates = result.get("candidates", [])
            if not candidates:
                raise Exception("Gemini API未返回有效响应")
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise Exception("Gemini API响应格式错误")
            
            text_response = parts[0].get("text", "")
            
            # 解析JSON响应
            emotions = self.parse_ai_response(text_response)
            dominant_emotion = get_dominant_emotion(emotions)
            confidence = emotions.get(dominant_emotion, 0.0)
            
            return EmotionResult(
                emotions=emotions,
                dominant_emotion=dominant_emotion,
                confidence=confidence,
                source=f"gemini-{model}",
                timestamp=datetime.now(),
                raw_data=result
            )
            
        except Exception as e:
            logger.error(f"Gemini API调用失败 (model: {model}): {e}")
            raise Exception(f"Gemini 情绪分析失败: {str(e)}")

    async def judge_emotions(self, analysis_results: List[Dict]) -> Dict:
        """裁判员AI：综合多个分析结果给出最终判断"""
        try:
            # 构建输入数据
            input_data = {
                "analysis_results": analysis_results
            }

            # 构建prompt
            prompt_text = f"{JUDGE_AI_PROMPT}\n\n输入数据：\n{json.dumps(input_data, ensure_ascii=False, indent=2)}"

            # 使用第一个可用模型
            model = self.models[0]
            url = f"{self.base_url}/{model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}

            data = {
                "contents": [{
                    "parts": [{"text": prompt_text}]
                }]
            }

            response = requests.post(url, headers=headers, params=params,
                                   json=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            # 解析响应
            candidates = result.get("candidates", [])
            if not candidates:
                raise Exception("裁判员AI未返回有效响应")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise Exception("裁判员AI响应格式错误")

            text_response = parts[0].get("text", "")
            logger.info(f"裁判员AI原始响应: {text_response[:500]}...")

            # 解析JSON响应 - 增强版本
            judge_result = self._parse_judge_response(text_response)
            return judge_result

        except Exception as e:
            logger.error(f"裁判员AI调用失败: {e}")
            # 返回默认结果
            return {
                "final_emotion": "neutral",
                "confidence": 0.5,
                "reasoning": f"裁判员AI调用失败: {str(e)}",
                "consistency_analysis": "无法进行一致性分析",
                "emotions": {"neutral": 1.0, "happy": 0.0, "sad": 0.0, "angry": 0.0,
                           "surprised": 0.0, "disgusted": 0.0, "fearful": 0.0}
            }

    def _parse_judge_response(self, text_response: str) -> Dict:
        """解析裁判员AI的响应，支持多种格式"""
        try:
            # 方法1: 直接解析JSON
            if text_response.strip().startswith("{"):
                return json.loads(text_response.strip())

            # 方法2: 提取```json```代码块
            import re
            json_match = re.search(r'```json\s*\n(.*?)\n```', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info(f"从代码块提取JSON: {json_str[:200]}...")
                return json.loads(json_str)

            # 方法3: 提取```代码块（无json标识）
            code_match = re.search(r'```\s*\n(.*?)\n```', text_response, re.DOTALL)
            if code_match:
                json_str = code_match.group(1).strip()
                if json_str.startswith("{"):
                    logger.info(f"从通用代码块提取JSON: {json_str[:200]}...")
                    return json.loads(json_str)

            # 方法4: 查找第一个完整的JSON对象
            brace_count = 0
            start_idx = -1
            for i, char in enumerate(text_response):
                if char == '{':
                    if start_idx == -1:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        json_str = text_response[start_idx:i+1]
                        logger.info(f"提取JSON对象: {json_str[:200]}...")
                        return json.loads(json_str)

            # 如果都失败了，记录详细错误
            logger.error(f"无法解析裁判员AI响应，原始内容: {text_response}")
            raise Exception("裁判员AI未返回有效JSON格式")

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}, 内容: {text_response[:500]}")
            raise Exception(f"JSON格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"解析裁判员AI响应失败: {e}")
            raise
    def parse_ai_response(self, text_response: str) -> Dict[str, float]:
        """解析AI模型的文本响应"""
        try:
            logger.info(f"解析AI响应: {text_response[:200]}...")

            # 方法1: 尝试直接解析JSON
            if text_response.strip().startswith("{"):
                data = json.loads(text_response.strip())
                emotions = data.get("emotions", {})
                logger.info(f"直接JSON解析成功: {emotions}")
                return normalize_probabilities(emotions)

            # 方法2: 提取```json```代码块
            import re
            json_match = re.search(r'```json\s*\n(.*?)\n```', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info(f"从代码块提取JSON: {json_str}")
                data = json.loads(json_str)
                emotions = data.get("emotions", {})
                logger.info(f"代码块JSON解析成功: {emotions}")
                return normalize_probabilities(emotions)

            # 方法3: 提取```代码块（无json标识）
            code_match = re.search(r'```\s*\n(.*?)\n```', text_response, re.DOTALL)
            if code_match:
                json_str = code_match.group(1).strip()
                if json_str.startswith("{"):
                    logger.info(f"从通用代码块提取JSON: {json_str}")
                    data = json.loads(json_str)
                    emotions = data.get("emotions", {})
                    logger.info(f"通用代码块JSON解析成功: {emotions}")
                    return normalize_probabilities(emotions)

            # 方法4: 如果不是JSON，尝试提取情绪关键词
            logger.warning(f"无法解析为JSON，尝试关键词提取: {text_response}")
            text_lower = text_response.lower()
            detected_emotions = {}

            for keyword, emotion in AI_EMOTION_MAPPING.items():
                if keyword in text_lower:
                    detected_emotions[emotion] = detected_emotions.get(emotion, 0) + 1

            if detected_emotions:
                # 转换为概率
                total = sum(detected_emotions.values())
                for emotion in detected_emotions:
                    detected_emotions[emotion] = detected_emotions[emotion] / total
                logger.info(f"关键词提取成功: {detected_emotions}")
                return normalize_probabilities(detected_emotions)

            # 默认返回中性情绪
            logger.warning("所有解析方法都失败，返回默认中性情绪")
            return {"neutral": 1.0}

        except Exception as e:
            logger.error(f"解析AI响应失败: {e}, 原始响应: {text_response}")
            return {"neutral": 1.0}
class OpenRouterService:
    """OpenRouter API服务类"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", 
                                "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")
        self.models = [
            "google/gemma-3-27b-it:free",
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen2.5-vl-32b-instruct:free"
        ]
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
    
    def encode_image(self, image_data: bytes) -> str:
        """将图像编码为base64"""
        return base64.b64encode(image_data).decode("utf-8")
    
    async def analyze_emotion(self, image_data: bytes, model: Optional[str] = None) -> EmotionResult:
        """使用OpenRouter分析情绪"""
        if model is None:
            model = self.models[0]
            
        try:
            image_base64 = self.encode_image(image_data)
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": EMOTION_ANALYSIS_PROMPT},
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                extra_headers={
                    "HTTP-Referer": "https://emoscan-app.com",
                    "X-Title": "EmoScan Emotion Analysis"
                },
                timeout=30
            )
            
            text_response = completion.choices[0].message.content
            if not text_response:
                raise Exception("OpenRouter返回空响应")

            # 解析响应
            emotions = self.parse_ai_response(text_response)
            dominant_emotion = get_dominant_emotion(emotions)
            confidence = emotions.get(dominant_emotion, 0.0)
            
            return EmotionResult(
                emotions=emotions,
                dominant_emotion=dominant_emotion,
                confidence=confidence,
                source=f"openrouter-{model}",
                timestamp=datetime.now(),
                raw_data={"response": text_response}
            )
            
        except Exception as e:
            logger.error(f"OpenRouter API调用失败 (model: {model}): {e}")
            raise Exception(f"OpenRouter 情绪分析失败: {str(e)}")    
    def parse_ai_response(self, text_response: str) -> Dict[str, float]:
        """解析AI模型的文本响应（与GeminiService共用）"""
        try:
            logger.info(f"解析AI响应: {text_response[:200]}...")

            # 方法1: 尝试直接解析JSON
            if text_response.strip().startswith("{"):
                data = json.loads(text_response.strip())
                emotions = data.get("emotions", {})
                logger.info(f"直接JSON解析成功: {emotions}")
                return normalize_probabilities(emotions)

            # 方法2: 提取```json```代码块
            import re
            json_match = re.search(r'```json\s*\n(.*?)\n```', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info(f"从代码块提取JSON: {json_str}")
                data = json.loads(json_str)
                emotions = data.get("emotions", {})
                logger.info(f"代码块JSON解析成功: {emotions}")
                return normalize_probabilities(emotions)

            # 方法3: 提取```代码块（无json标识）
            code_match = re.search(r'```\s*\n(.*?)\n```', text_response, re.DOTALL)
            if code_match:
                json_str = code_match.group(1).strip()
                if json_str.startswith("{"):
                    logger.info(f"从通用代码块提取JSON: {json_str}")
                    data = json.loads(json_str)
                    emotions = data.get("emotions", {})
                    logger.info(f"通用代码块JSON解析成功: {emotions}")
                    return normalize_probabilities(emotions)

            # 方法4: 如果不是JSON，尝试提取情绪关键词
            logger.warning(f"无法解析为JSON，尝试关键词提取: {text_response}")
            text_lower = text_response.lower()
            detected_emotions = {}

            for keyword, emotion in AI_EMOTION_MAPPING.items():
                if keyword in text_lower:
                    detected_emotions[emotion] = detected_emotions.get(emotion, 0) + 1

            if detected_emotions:
                # 转换为概率
                total = sum(detected_emotions.values())
                for emotion in detected_emotions:
                    detected_emotions[emotion] = detected_emotions[emotion] / total
                logger.info(f"关键词提取成功: {detected_emotions}")
                return normalize_probabilities(detected_emotions)

            # 默认返回中性情绪
            logger.warning("所有解析方法都失败，返回默认中性情绪")
            return {"neutral": 1.0}

        except Exception as e:
            logger.error(f"解析AI响应失败: {e}, 原始响应: {text_response}")
            return {"neutral": 1.0}