"""
主控程序 (Caller)
工作原理：
1. 协调各模块的工作流程
2. 管理数据流和状态监控
3. 提供统一的调用接口
4. 处理异常和错误恢复
"""

import logging
import json
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import config
from .capture import capture_face_images
from .tagger import tag_face_images
from .splicer import splice_images
from .cleaner import clean_all_files
from ..robot.jsa import run_jsa_analysis, run_complete_emotion_analysis

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class WorkflowStatus:
    """工作流状态管理"""

    def __init__(self):
        self.current_step = ""
        self.total_steps = 0
        self.completed_steps = 0
        self.start_time = None
        self.errors = []
        self.warnings = []
        self.results = {}

    def start(self, total_steps: int):
        """开始工作流"""
        self.total_steps = total_steps
        self.completed_steps = 0
        self.start_time = time.time()
        self.errors = []
        self.warnings = []
        self.results = {}
        logger.info(f"工作流开始，总共 {total_steps} 个步骤")

    def update_step(self, step_name: str):
        """更新当前步骤"""
        self.current_step = step_name
        logger.info(f"执行步骤: {step_name} ({self.completed_steps + 1}/{self.total_steps})")

    def complete_step(self, result: Any = None):
        """完成当前步骤"""
        self.completed_steps += 1
        if result is not None:
            self.results[self.current_step] = result

        progress = (self.completed_steps / self.total_steps) * 100
        logger.info(f"步骤完成: {self.current_step} (进度: {progress:.1f}%)")

    def add_error(self, error: str):
        """添加错误"""
        self.errors.append({
            'step': self.current_step,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        logger.error(f"步骤错误 [{self.current_step}]: {error}")

    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append({
            'step': self.current_step,
            'warning': warning,
            'timestamp': datetime.now().isoformat()
        })
        logger.warning(f"步骤警告 [{self.current_step}]: {warning}")

    def get_summary(self) -> Dict:
        """获取工作流摘要"""
        duration = time.time() - self.start_time if self.start_time else 0

        return {
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'current_step': self.current_step,
            'duration_seconds': duration,
            'success_rate': (self.completed_steps / self.total_steps) * 100 if self.total_steps > 0 else 0,
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'results': self.results
        }

class EmotionAnalysisCaller:
    """情绪分析主控程序"""

    def __init__(self):
        """初始化主控程序"""
        self.status = WorkflowStatus()
        self.progress_callback: Optional[Callable] = None

        logger.info("情绪分析主控程序初始化成功")

    def set_progress_callback(self, callback: Callable[[Dict], None]):
        """设置进度回调函数"""
        self.progress_callback = callback

    def _notify_progress(self):
        """通知进度更新"""
        if self.progress_callback:
            try:
                self.progress_callback(self.status.get_summary())
            except Exception as e:
                logger.error(f"进度回调失败: {e}")

    def run_step(self, step_name: str, step_func: Callable, *args, **kwargs) -> Any:
        """执行单个步骤"""
        self.status.update_step(step_name)
        self._notify_progress()

        try:
            result = step_func(*args, **kwargs)

            # 检查结果是否包含错误
            if isinstance(result, dict) and 'error' in result:
                self.status.add_error(result['error'])
                return None

            self.status.complete_step(result)
            self._notify_progress()
            return result

        except Exception as e:
            error_msg = f"步骤执行失败: {e}"
            self.status.add_error(error_msg)
            self._notify_progress()
            return None

    def _create_error_result(self, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            'success': False,
            'error': error_msg,
            'workflow_summary': self.status.get_summary(),
            'timestamp': datetime.now().isoformat()
        }

    def _create_success_result(self, workflow_type: str, results: Dict) -> Dict:
        """创建成功结果"""
        summary = self.status.get_summary()

        return {
            'success': True,
            'workflow_type': workflow_type,
            'results': results,
            'workflow_summary': summary,
            'timestamp': datetime.now().isoformat(),
            'final_result': results.get('analysis_result', {}).get('final_judgment', {}),
            'summary_text': self._generate_summary_text(results)
        }

    def _generate_summary_text(self, results: Dict) -> str:
        """生成摘要文本"""
        try:
            analysis_result = results.get('analysis_result', {})
            final_judgment = analysis_result.get('final_judgment', {})

            if final_judgment and 'summary' in final_judgment:
                return final_judgment['summary']
            elif 'error' in analysis_result:
                return f"分析失败: {analysis_result['error']}"
            else:
                return "图像处理完成，但情绪分析未成功"

        except Exception as e:
            return f"摘要生成失败: {e}"

    def run_basic_workflow(self) -> Dict:
        """运行基础工作流程（不包含分析）"""
        logger.info("开始基础工作流程...")

        self.status.start(4)  # 4个基础步骤

        # 步骤1: 图像捕获
        captured_files = self.run_step("图像捕获", capture_face_images)
        if not captured_files:
            return self._create_error_result("图像捕获失败")

        # 步骤2: 人脸标注
        tagged_results = self.run_step("人脸标注", tag_face_images)
        if not tagged_results:
            return self._create_error_result("人脸标注失败")

        # 步骤3: 图像拼接
        spliced_result = self.run_step("图像拼接", splice_images)
        if not spliced_result:
            return self._create_error_result("图像拼接失败")

        # 步骤4: 文件清理
        cleanup_result = self.run_step("文件清理", clean_all_files, True)  # 保留最终拼接文件

        return self._create_success_result("basic_workflow", {
            'captured_files': captured_files,
            'tagged_results': tagged_results,
            'spliced_result': spliced_result,
            'cleanup_result': cleanup_result
        })

    def run_analysis_workflow(self) -> Dict:
        """运行分析工作流程（仅分析）"""
        logger.info("开始分析工作流程...")

        self.status.start(1)  # 1个分析步骤

        # 步骤1: JSA综合分析
        analysis_result = self.run_step("JSA综合分析", run_jsa_analysis)
        if not analysis_result or 'error' in analysis_result:
            return self._create_error_result("JSA分析失败")

        return self._create_success_result("analysis_workflow", {
            'analysis_result': analysis_result
        })

    def run_complete_workflow(self, progress_callback: Optional[Callable] = None) -> Dict:
        """运行完整工作流程"""
        logger.info("开始完整工作流程...")

        # 如果提供了进度回调，设置它
        if progress_callback:
            self.set_progress_callback(progress_callback)

        self.status.start(5)  # 5个完整步骤

        # 步骤1: 图像捕获
        captured_files = self.run_step("图像捕获", capture_face_images)
        if not captured_files:
            return self._create_error_result("图像捕获失败")

        # 步骤2: 人脸标注
        tagged_results = self.run_step("人脸标注", tag_face_images)
        if not tagged_results:
            return self._create_error_result("人脸标注失败")

        # 步骤3: 图像拼接
        spliced_result = self.run_step("图像拼接", splice_images)
        if not spliced_result:
            return self._create_error_result("图像拼接失败")

        # 步骤4: JSA综合分析
        analysis_result = self.run_step("JSA综合分析", run_jsa_analysis)
        if not analysis_result or 'error' in analysis_result:
            self.status.add_warning("JSA分析失败，但基础流程已完成")

        # 步骤5: 文件清理
        cleanup_result = self.run_step("文件清理", clean_all_files, True)

        return self._create_success_result("complete_workflow", {
            'captured_files': captured_files,
            'tagged_results': tagged_results,
            'spliced_result': spliced_result,
            'analysis_result': analysis_result,
            'cleanup_result': cleanup_result
        })

    def run_batch_analysis(self, image_paths: List[str]) -> Dict:
        """运行批量图像分析"""
        logger.info(f"开始批量分析 {len(image_paths)} 张图像...")

        self.status.start(2)  # 2个批量步骤

        # 步骤1: 批量图像处理
        def batch_process():
            # 这里可以添加批量图像预处理逻辑
            return {'processed_images': image_paths}

        processed_result = self.run_step("批量图像处理", batch_process)
        if not processed_result:
            return self._create_error_result("批量图像处理失败")

        # 步骤2: 批量分析
        analysis_result = self.run_step("批量分析", run_jsa_analysis)
        if not analysis_result or 'error' in analysis_result:
            return self._create_error_result("批量分析失败")

        return self._create_success_result("batch_analysis", {
            'processed_result': processed_result,
            'analysis_result': analysis_result
        })

    def get_status(self) -> Dict:
        """获取当前状态"""
        return self.status.get_summary()

    def reset(self):
        """重置状态"""
        self.status = WorkflowStatus()
        logger.info("主控程序状态已重置")

# 便捷函数
def run_emotion_analysis(workflow_type: str = "complete", progress_callback: Optional[Callable] = None) -> Dict:
    """
    便捷函数：运行情绪分析

    Args:
        workflow_type: 工作流类型 ("complete", "basic", "analysis")
        progress_callback: 进度回调函数

    Returns:
        Dict: 分析结果
    """
    caller = EmotionAnalysisCaller()

    if progress_callback:
        caller.set_progress_callback(progress_callback)

    if workflow_type == "complete":
        return caller.run_complete_workflow()
    elif workflow_type == "basic":
        return caller.run_basic_workflow()
    elif workflow_type == "analysis":
        return caller.run_analysis_workflow()
    else:
        return {
            'success': False,
            'error': f"不支持的工作流类型: {workflow_type}",
            'timestamp': datetime.now().isoformat()
        }

def run_batch_emotion_analysis(image_paths: List[str], progress_callback: Optional[Callable] = None) -> Dict:
    """
    便捷函数：运行批量情绪分析

    Args:
        image_paths: 图像文件路径列表
        progress_callback: 进度回调函数

    Returns:
        Dict: 批量分析结果
    """
    caller = EmotionAnalysisCaller()

    if progress_callback:
        caller.set_progress_callback(progress_callback)

    return caller.run_batch_analysis(image_paths)

def get_workflow_status() -> Dict:
    """
    便捷函数：获取工作流状态

    Returns:
        Dict: 状态信息
    """
    caller = EmotionAnalysisCaller()
    return caller.get_status()

class AsyncEmotionAnalysisCaller:
    """异步情绪分析主控程序"""

    def __init__(self):
        """初始化异步主控程序"""
        self.caller = EmotionAnalysisCaller()

    async def run_async_workflow(self, workflow_type: str = "complete") -> Dict:
        """
        异步运行工作流程

        Args:
            workflow_type: 工作流类型

        Returns:
            Dict: 分析结果
        """
        loop = asyncio.get_event_loop()

        if workflow_type == "complete":
            return await loop.run_in_executor(None, self.caller.run_complete_workflow)
        elif workflow_type == "basic":
            return await loop.run_in_executor(None, self.caller.run_basic_workflow)
        elif workflow_type == "analysis":
            return await loop.run_in_executor(None, self.caller.run_analysis_workflow)
        else:
            return {
                'success': False,
                'error': f"不支持的工作流类型: {workflow_type}",
                'timestamp': datetime.now().isoformat()
            }

    async def run_async_batch_analysis(self, image_paths: List[str]) -> Dict:
        """
        异步运行批量分析

        Args:
            image_paths: 图像文件路径列表

        Returns:
            Dict: 批量分析结果
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.caller.run_batch_analysis, image_paths)

# 异步便捷函数
async def run_async_emotion_analysis(workflow_type: str = "complete") -> Dict:
    """
    异步便捷函数：运行情绪分析

    Args:
        workflow_type: 工作流类型

    Returns:
        Dict: 分析结果
    """
    async_caller = AsyncEmotionAnalysisCaller()
    return await async_caller.run_async_workflow(workflow_type)

async def run_async_batch_emotion_analysis(image_paths: List[str]) -> Dict:
    """
    异步便捷函数：运行批量情绪分析

    Args:
        image_paths: 图像文件路径列表

    Returns:
        Dict: 批量分析结果
    """
    async_caller = AsyncEmotionAnalysisCaller()
    return await async_caller.run_async_batch_analysis(image_paths)

# 为了向后兼容，创建别名
WorkflowCaller = EmotionAnalysisCaller

if __name__ == "__main__":
    # 测试代码
    def progress_callback(status):
        print(f"进度更新: {status['current_step']} - {status['success_rate']:.1f}%")

    # 测试完整工作流程
    result = run_emotion_analysis("complete", progress_callback)
    print(f"分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")