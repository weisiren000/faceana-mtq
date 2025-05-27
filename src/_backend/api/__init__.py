"""
API统一接口模块
提供统一的API调用接口、负载均衡和故障转移功能
"""

import logging
import time
import random
from typing import Dict, List, Optional, Union, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from ..config import config
from .facepp import FacePPClient, analyze_capture_directory as facepp_analyze
from .openrouter import OpenRouterClient, analyze_capture_with_openrouter
from .gemini import GeminiClient, analyze_capture_with_gemini

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class APIManager:
    """API管理器 - 统一的API调用接口"""

    def __init__(self):
        """初始化API管理器"""
        self.clients = {}
        self.api_status = {}
        self.call_history = []

        # 初始化各API客户端
        self._init_clients()

        logger.info("API管理器初始化成功")

    def _init_clients(self):
        """初始化API客户端"""
        try:
            # Face++ 客户端
            self.clients['facepp'] = FacePPClient()
            self.api_status['facepp'] = {'available': True, 'last_error': None, 'call_count': 0}

            # OpenRouter 客户端
            self.clients['openrouter'] = OpenRouterClient()
            self.api_status['openrouter'] = {'available': True, 'last_error': None, 'call_count': 0}

            # Gemini 客户端
            self.clients['gemini'] = GeminiClient()
            self.api_status['gemini'] = {'available': True, 'last_error': None, 'call_count': 0}

            logger.info("所有API客户端初始化完成")

        except Exception as e:
            logger.error(f"API客户端初始化失败: {e}")
            raise

    def _record_api_call(self, api_name: str, success: bool, duration: float, error: str = None):
        """记录API调用"""
        call_record = {
            'api_name': api_name,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'duration': duration,
            'error': error
        }

        self.call_history.append(call_record)
        self.api_status[api_name]['call_count'] += 1

        if not success:
            self.api_status[api_name]['last_error'] = error
            logger.warning(f"API调用失败 [{api_name}]: {error}")

        # 保持历史记录在合理范围内
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-500:]

    def _call_with_retry(self, api_name: str, func: Callable, *args, **kwargs) -> Dict:
        """带重试的API调用"""
        max_retries = config.MAX_RETRY_ATTEMPTS

        for attempt in range(max_retries):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # 检查结果是否包含错误
                if isinstance(result, dict) and 'error' in result:
                    self._record_api_call(api_name, False, duration, result['error'])

                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)  # 指数退避
                        logger.info(f"API调用失败，{wait_time:.1f}秒后重试 ({attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        return result
                else:
                    self._record_api_call(api_name, True, duration)
                    return result

            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                self._record_api_call(api_name, False, duration, error_msg)

                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"API调用异常，{wait_time:.1f}秒后重试 ({attempt + 1}/{max_retries}): {error_msg}")
                    time.sleep(wait_time)
                    continue
                else:
                    return {'error': error_msg}

        return {'error': f'API调用失败，已重试{max_retries}次'}

    def call_facepp_analysis(self, image_paths: List[str] = None) -> Dict:
        """调用Face++分析"""
        logger.info("调用Face++进行情绪分析")

        if image_paths:
            # 批量分析指定图像
            client = self.clients['facepp']
            return self._call_with_retry('facepp', client.batch_analyze_emotions, image_paths)
        else:
            # 分析capture目录
            return self._call_with_retry('facepp', facepp_analyze)

    def call_openrouter_analysis(self, image_paths: List[str] = None, model: str = None) -> Dict:
        """调用OpenRouter分析"""
        logger.info("调用OpenRouter进行视觉分析")

        if image_paths:
            # 批量分析指定图像
            client = self.clients['openrouter']
            return self._call_with_retry('openrouter', client.batch_analyze_emotions, image_paths, model)
        else:
            # 分析capture目录
            return self._call_with_retry('openrouter', analyze_capture_with_openrouter, model)

    def call_gemini_analysis(self, image_paths: List[str] = None, model: str = None) -> Dict:
        """调用Gemini分析"""
        logger.info("调用Gemini进行视觉分析")

        if image_paths:
            # 批量分析指定图像
            client = self.clients['gemini']
            return self._call_with_retry('gemini', client.batch_analyze_emotions, image_paths, model)
        else:
            # 分析capture目录
            return self._call_with_retry('gemini', analyze_capture_with_gemini, model)

    def call_parallel_visual_analysis(self, image_paths: List[str] = None) -> Dict:
        """并行调用多个视觉分析API"""
        logger.info("并行调用OpenRouter和Gemini进行视觉分析")

        results = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            # 提交任务
            future_openrouter = executor.submit(self.call_openrouter_analysis, image_paths)
            future_gemini = executor.submit(self.call_gemini_analysis, image_paths)

            # 收集结果
            try:
                results['openrouter'] = future_openrouter.result(timeout=config.REQUEST_TIMEOUT)
            except Exception as e:
                results['openrouter'] = {'error': f'OpenRouter调用超时或失败: {e}'}

            try:
                results['gemini'] = future_gemini.result(timeout=config.REQUEST_TIMEOUT)
            except Exception as e:
                results['gemini'] = {'error': f'Gemini调用超时或失败: {e}'}

        return {
            'parallel_analysis': True,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'success_count': sum(1 for r in results.values() if 'error' not in r),
            'total_apis': len(results)
        }

    def get_api_status(self) -> Dict:
        """获取API状态"""
        status_summary = {
            'timestamp': datetime.now().isoformat(),
            'apis': {},
            'total_calls': len(self.call_history),
            'recent_calls': len([c for c in self.call_history if
                               (datetime.now() - datetime.fromisoformat(c['timestamp'])).seconds < 3600])
        }

        for api_name, status in self.api_status.items():
            recent_calls = [c for c in self.call_history if c['api_name'] == api_name and
                           (datetime.now() - datetime.fromisoformat(c['timestamp'])).seconds < 3600]

            success_rate = 0
            if recent_calls:
                success_count = sum(1 for c in recent_calls if c['success'])
                success_rate = (success_count / len(recent_calls)) * 100

            status_summary['apis'][api_name] = {
                'available': status['available'],
                'total_calls': status['call_count'],
                'recent_calls': len(recent_calls),
                'success_rate': success_rate,
                'last_error': status['last_error']
            }

        return status_summary

    def test_all_apis(self) -> Dict:
        """测试所有API的可用性"""
        logger.info("测试所有API可用性")

        test_results = {}

        for api_name, client in self.clients.items():
            try:
                if hasattr(client, 'test_model'):
                    # 对于有test_model方法的客户端
                    if api_name == 'openrouter':
                        result = client.test_model(client.models[0] if client.models else None)
                    elif api_name == 'gemini':
                        result = client.test_model(client.default_model)
                    else:
                        result = {'available': True, 'test': 'no_test_method'}
                else:
                    # 对于Face++等没有test方法的客户端，简单检查初始化
                    result = {'available': True, 'test': 'initialization_check'}

                test_results[api_name] = result

            except Exception as e:
                test_results[api_name] = {'available': False, 'error': str(e)}

        return {
            'test_timestamp': datetime.now().isoformat(),
            'results': test_results,
            'available_count': sum(1 for r in test_results.values() if r.get('available', False)),
            'total_apis': len(test_results)
        }

# 全局API管理器实例
api_manager = APIManager()

# 便捷函数
def get_api_manager() -> APIManager:
    """获取API管理器实例"""
    return api_manager

def call_facepp_api(image_paths: List[str] = None) -> Dict:
    """便捷函数：调用Face++API"""
    return api_manager.call_facepp_analysis(image_paths)

def call_openrouter_api(image_paths: List[str] = None, model: str = None) -> Dict:
    """便捷函数：调用OpenRouter API"""
    return api_manager.call_openrouter_analysis(image_paths, model)

def call_gemini_api(image_paths: List[str] = None, model: str = None) -> Dict:
    """便捷函数：调用Gemini API"""
    return api_manager.call_gemini_analysis(image_paths, model)

def call_parallel_visual_apis(image_paths: List[str] = None) -> Dict:
    """便捷函数：并行调用视觉分析API"""
    return api_manager.call_parallel_visual_analysis(image_paths)

def get_all_api_status() -> Dict:
    """便捷函数：获取所有API状态"""
    return api_manager.get_api_status()

def test_all_api_availability() -> Dict:
    """便捷函数：测试所有API可用性"""
    return api_manager.test_all_apis()

if __name__ == "__main__":
    # 测试代码
    try:
        manager = APIManager()
        print("API管理器初始化成功")

        # 测试API状态
        status = manager.get_api_status()
        print(f"API状态: {status}")

        # 测试API可用性
        test_results = manager.test_all_apis()
        print(f"API测试结果: {test_results}")

    except Exception as e:
        print(f"API管理器测试失败: {e}")