"""
ComfyUI服务类 - 负责与ComfyUI API通信
提供发送提示词、获取生成结果等功能
"""

import json
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger(__name__)

class ComfyUIService:
    """ComfyUI API通信服务"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化ComfyUI服务
        
        Args:
            base_url: ComfyUI API基础URL，默认为http://localhost:8000
        """
        self.base_url = base_url
        self.client_id = f"emoscan_{id(self)}"
        self.ws = None
        self.connected = False
        self.callbacks = {}
    
    async def check_connection(self) -> bool:
        """
        检查与ComfyUI的连接状态
        
        Returns:
            bool: 是否连接成功
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/system_stats") as response:
                    if response.status == 200:
                        logger.info(f"成功连接到ComfyUI服务器: {self.base_url}")
                        return True
                    else:
                        logger.error(f"连接ComfyUI失败: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"连接ComfyUI时发生错误: {e}")
            return False
    
    async def send_prompt(self, workflow: Dict) -> Dict[str, Any]:
        """
        发送工作流到ComfyUI
        
        Args:
            workflow: ComfyUI工作流数据
            
        Returns:
            Dict: 响应结果，包含prompt_id等信息
        """
        try:
            # 准备发送的数据
            data = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/prompt",
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        logger.info(f"成功发送提示词，提示ID: {prompt_id}")
                        
                        return {
                            "success": True,
                            "prompt_id": prompt_id,
                            "message": "已开始生成"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"发送到ComfyUI API失败: {response.status}, {error_text}")
                        return {"success": False, "error": f"API错误: {response.status}"}
                        
        except Exception as e:
            logger.error(f"发送提示词时发生错误: {e}")
            return {"success": False, "error": str(e)}
    
    def create_workflow_from_emotion(self, emotion: str, intensity: float = 0.8,
                                  custom_prompt: Optional[str] = None) -> Dict:
        """
        根据情绪创建ComfyUI工作流
        
        Args:
            emotion: 情绪类型，如happy、sad等
            intensity: 情绪强度，0-1之间
            custom_prompt: 自定义提示词
            
        Returns:
            Dict: ComfyUI工作流数据
        """
        # 情绪到提示词的映射
        emotion_prompts = {
            "happy": "a joyful scene with bright colors, sunshine, smiling people",
            "sad": "a melancholic scene with rain, dark colors, lonely figure",
            "angry": "a dramatic scene with intense red colors, stormy weather",
            "surprised": "a scene with unexpected elements, bright contrasts",
            "neutral": "a balanced scene with natural colors, calm atmosphere",
            "disgusted": "a scene with unsettling elements, sickly green tones",
            "fearful": "a dark scene with shadows, fog, mysterious elements"
        }
        
        # 情绪参数映射
        emotion_params = {
            "happy": {"cfg": 6.5, "sampler": "euler_a", "steps": 20},
            "sad": {"cfg": 7.5, "sampler": "ddim", "steps": 25},
            "angry": {"cfg": 8.0, "sampler": "dpm++_2m", "steps": 30},
            "surprised": {"cfg": 7.0, "sampler": "euler", "steps": 20},
            "neutral": {"cfg": 7.0, "sampler": "ddpm", "steps": 20},
            "disgusted": {"cfg": 7.5, "sampler": "dpm2", "steps": 25},
            "fearful": {"cfg": 8.0, "sampler": "dpm_sde", "steps": 30}
        }
        
        # 获取情绪对应的提示词和参数
        base_prompt = emotion_prompts.get(emotion.lower(), "a scene")
        params = emotion_params.get(emotion.lower(), {"cfg": 7.0, "sampler": "euler_ancestral", "steps": 20})
        
        # 添加自定义提示词
        if custom_prompt:
            prompt = f"{base_prompt}, {custom_prompt}"
        else:
            prompt = base_prompt
            
        # 根据强度调整提示词
        intensity_word = "extremely" if intensity > 0.9 else "very" if intensity > 0.7 else ""
        if intensity_word:
            prompt = f"{prompt}, {intensity_word} {emotion}"
            
        # 创建工作流
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(intensity * 1000000),  # 使用强度生成种子
                    "steps": params["steps"],
                    "cfg": params["cfg"],
                    "sampler_name": params["sampler"],
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "dreamshaper_8.safetensors"  # 默认模型
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "ugly, deformed, bad anatomy, blurry, low quality",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "filename_prefix": f"emoscan_{emotion}",
                    "fps": 8
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow
    
    async def get_image_url(self, filename: str) -> Optional[str]:
        """
        获取生成图像的URL
        
        Args:
            filename: 图像文件名
            
        Returns:
            Optional[str]: 图像URL，如果失败则返回None
        """
        try:
            # ComfyUI的图像URL格式
            return f"{self.base_url}/view?filename={filename}"
        except Exception as e:
            logger.error(f"获取图像URL时出错: {e}")
            return None
    
    async def get_history(self) -> List[Dict]:
        """
        获取ComfyUI历史记录
        
        Returns:
            List[Dict]: 历史记录列表
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/history") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"获取历史记录失败: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"获取历史记录时出错: {e}")
            return [] 