"""
ComfyUI服务模块
负责与ComfyUI API交互，生成情绪相关的图像
"""

import json
import time
import uuid
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any

import aiohttp
import aiofiles

from ..models.comfyui import (
    GenerationRequest, GenerationResponse, ComfyUIStatus, WorkflowInfo,
    COMFYUI_CONFIG, get_workflow_filename,
    parse_comfyui_outputs, json_to_workflow, EMOTION_WORKFLOW_MAPPING, DEFAULT_WORKFLOW
)
from datetime import datetime

logger = logging.getLogger(__name__)


class ComfyUIService:
    """ComfyUI服务类"""
    
    def __init__(self, base_url: Optional[str] = None, workflows_dir: Optional[str] = None):
        self.base_url = base_url or COMFYUI_CONFIG["base_url"]
        self.workflows_dir = Path(workflows_dir) if workflows_dir else Path(__file__).parent.parent.parent / "workflows"
        self.client_id = f"emoscan_{uuid.uuid4()}"
        self.timeout = COMFYUI_CONFIG["timeout"]
        self.max_wait_time = COMFYUI_CONFIG["max_wait_time"]
        self.check_interval = COMFYUI_CONFIG["check_interval"]
        
        logger.info(f"ComfyUI服务初始化: {self.base_url}, 工作流目录: {self.workflows_dir}")
    
    async def check_status(self) -> ComfyUIStatus:
        """检查ComfyUI服务状态"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                # 检查系统状态
                async with session.get(f"{self.base_url}/system_stats") as response:
                    if response.status == 200:
                        system_stats = await response.json()
                        
                        # 检查队列状态
                        async with session.get(f"{self.base_url}/queue") as queue_response:
                            if queue_response.status == 200:
                                queue_data = await queue_response.json()
                                return ComfyUIStatus(
                                    available=True,
                                    queue_running=len(queue_data.get("queue_running", [])),
                                    queue_pending=len(queue_data.get("queue_pending", [])),
                                    system_stats=system_stats
                                )
                            
                        return ComfyUIStatus(available=True, system_stats=system_stats)
                    else:
                        return ComfyUIStatus(
                            available=False,
                            error_message=f"HTTP {response.status}"
                        )
                        
        except Exception as e:
            logger.error(f"检查ComfyUI状态失败: {e}")
            return ComfyUIStatus(
                available=False,
                error_message=str(e)
            )
    
    async def load_workflow(self, emotion: str, custom_workflow: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """加载工作流文件"""
        try:
            # 确定工作流文件名
            workflow_filename = custom_workflow or get_workflow_filename(emotion)
            workflow_path = self.workflows_dir / workflow_filename
            
            # 检查文件是否存在
            if not workflow_path.exists():
                logger.warning(f"工作流文件不存在: {workflow_path}")
                return None
            
            # 异步读取文件
            async with aiofiles.open(workflow_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                workflow = json_to_workflow(content)
                
            logger.info(f"成功加载工作流: {workflow_path}")
            return workflow
            
        except Exception as e:
            logger.error(f"加载工作流失败: {e}")
            return None
    
    def modify_workflow(self, workflow: Dict[str, Any], emotion: str, seed: Optional[int] = None,
                       custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """修改工作流参数 - 确保每次生成唯一的文件名和随机seed"""
        modified_workflow = workflow.copy()

        # 生成唯一的文件名前缀，确保每次都不同
        timestamp = int(time.time() * 1000)  # 使用毫秒级时间戳
        unique_id = str(uuid.uuid4())[:8]    # 使用UUID的前8位
        filename_prefix = f"emoscan_{emotion}_{timestamp}_{unique_id}"

        # 生成随机seed（如果没有指定的话）
        if seed is None:
            import random
            seed = random.randint(1, 2147483647)  # 32位正整数范围

        # 查找并修改所有SaveImage节点的filename_prefix
        modified_count = 0
        for node_id, node_data in modified_workflow.items():
            if isinstance(node_data, dict) and node_data.get("class_type") == "SaveImage":
                if "inputs" in node_data:
                    node_data["inputs"]["filename_prefix"] = filename_prefix
                    modified_count += 1
                    logger.info(f"修改节点 {node_id} 的filename_prefix为: {filename_prefix}")

        # 查找并修改所有包含seed的节点（JimengImageGenerator, KSampler等）
        seed_modified_count = 0
        for node_id, node_data in modified_workflow.items():
            if isinstance(node_data, dict) and "inputs" in node_data:
                inputs = node_data["inputs"]
                if "seed" in inputs:
                    inputs["seed"] = seed
                    seed_modified_count += 1
                    logger.info(f"修改节点 {node_id} ({node_data.get('class_type', 'Unknown')}) 的seed为: {seed}")

        logger.info(f"工作流修改完成 (情绪: {emotion}, 修改了 {modified_count} 个SaveImage节点, {seed_modified_count} 个seed参数)")
        return modified_workflow
    
    async def send_prompt(self, workflow: Dict[str, Any]) -> Optional[str]:
        """发送工作流到ComfyUI"""
        try:
            data = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/prompt", json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        logger.info(f"成功发送工作流，提示ID: {prompt_id}")
                        return prompt_id
                    else:
                        error_text = await response.text()
                        logger.error(f"发送工作流失败，状态码: {response.status}, 错误: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"发送工作流异常: {e}")
            return None

    async def wait_for_completion(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """等待图像生成完成"""
        logger.info(f"等待图像生成完成，提示ID: {prompt_id}")
        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < self.max_wait_time:
                try:
                    # 首先检查完整历史记录
                    async with session.get(f"{self.base_url}/history") as response:
                        if response.status == 200:
                            all_history = await response.json()
                            if prompt_id in all_history:
                                result = all_history[prompt_id]
                                # 检查状态
                                if "status" in result:
                                    status = result["status"]
                                    if status.get("completed", False) and status.get("status_str") == "success":
                                        logger.info(f"图像生成完成！提示ID: {prompt_id}")
                                        return result.get("outputs", {})
                                    elif status.get("status_str") == "error":
                                        logger.error(f"图像生成失败: {status}")
                                        return None

                                # 如果有outputs，也认为是成功的
                                if "outputs" in result:
                                    logger.info(f"图像生成完成（通过outputs检测）！提示ID: {prompt_id}")
                                    return result["outputs"]

                    # 检查队列状态，看是否还在处理中
                    async with session.get(f"{self.base_url}/queue") as response:
                        if response.status == 200:
                            queue_data = await response.json()
                            running = queue_data.get("queue_running", [])
                            pending = queue_data.get("queue_pending", [])

                            # 检查是否还在队列中
                            in_queue = False
                            for item in running + pending:
                                if len(item) >= 2 and isinstance(item[1], str):
                                    if item[1] == prompt_id:
                                        in_queue = True
                                        break
                                elif len(item) >= 2 and isinstance(item[1], dict):
                                    # 有些格式可能不同，也检查一下
                                    if str(item[1]).find(prompt_id) != -1:
                                        in_queue = True
                                        break

                            if not in_queue:
                                # 不在队列中，最后再检查一次历史记录
                                async with session.get(f"{self.base_url}/history") as hist_response:
                                    if hist_response.status == 200:
                                        final_history = await hist_response.json()
                                        if prompt_id in final_history:
                                            result = final_history[prompt_id]
                                            logger.info(f"在最终检查中找到结果: {prompt_id}")
                                            return result.get("outputs", {})
                                        else:
                                            logger.warning(f"任务不在队列中，但历史记录中也找不到: {prompt_id}")
                                            return None

                    # 等待一段时间后重试
                    await asyncio.sleep(self.check_interval)

                except Exception as e:
                    logger.error(f"检查生成状态时出错: {e}")
                    await asyncio.sleep(1)  # 出错时短暂等待
                    continue

        logger.warning(f"等待图像生成超时: {prompt_id}")
        return None

    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """生成图像的主要方法"""
        start_time = time.time()

        try:
            # 1. 检查服务状态
            status = await self.check_status()
            if not status.available:
                return GenerationResponse(
                    success=False,
                    error_message=f"ComfyUI服务不可用: {status.error_message}"
                )

            # 2. 加载工作流
            workflow = await self.load_workflow(request.emotion, request.workflow_name)
            if not workflow:
                return GenerationResponse(
                    success=False,
                    error_message=f"无法加载工作流: {request.emotion}"
                )

            # 3. 修改工作流参数
            modified_workflow = self.modify_workflow(
                workflow,
                request.emotion,
                request.seed,
                request.custom_params
            )

            # 4. 发送工作流
            prompt_id = await self.send_prompt(modified_workflow)
            if not prompt_id:
                return GenerationResponse(
                    success=False,
                    error_message="发送工作流失败"
                )

            # 5. 等待完成
            outputs = await self.wait_for_completion(prompt_id)
            if not outputs:
                return GenerationResponse(
                    success=False,
                    prompt_id=prompt_id,
                    error_message="图像生成超时或失败"
                )

            # 6. 解析结果
            images = parse_comfyui_outputs(outputs, self.base_url)
            generation_time = time.time() - start_time

            logger.info(f"图像生成成功: {len(images)}张图像，耗时: {generation_time:.2f}秒")

            return GenerationResponse(
                success=True,
                prompt_id=prompt_id,
                images=images,
                generation_time=generation_time
            )

        except Exception as e:
            logger.error(f"图像生成异常: {e}")
            return GenerationResponse(
                success=False,
                error_message=f"生成异常: {str(e)}",
                generation_time=time.time() - start_time
            )

    async def list_workflows(self) -> List[WorkflowInfo]:
        """列出所有可用的工作流"""
        workflows = []

        try:
            for emotion, filename in EMOTION_WORKFLOW_MAPPING.items():
                workflow_path = self.workflows_dir / filename
                workflows.append(WorkflowInfo(
                    name=filename,
                    emotion=emotion,
                    path=str(workflow_path),
                    exists=workflow_path.exists(),
                    last_modified=datetime.fromtimestamp(workflow_path.stat().st_mtime) if workflow_path.exists() else None
                ))

            # 添加默认工作流
            default_path = self.workflows_dir / DEFAULT_WORKFLOW
            workflows.append(WorkflowInfo(
                name=DEFAULT_WORKFLOW,
                emotion="default",
                path=str(default_path),
                exists=default_path.exists(),
                last_modified=datetime.fromtimestamp(default_path.stat().st_mtime) if default_path.exists() else None
            ))

        except Exception as e:
            logger.error(f"列出工作流失败: {e}")

        return workflows
