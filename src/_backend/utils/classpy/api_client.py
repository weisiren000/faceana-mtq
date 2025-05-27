"""
API客户端基类
提供统一的API调用接口和错误处理机制
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json

from ...config import config

# 配置日志
logger = logging.getLogger(__name__)


class APIClientBase(ABC):
    """API客户端基类"""
    
    def __init__(self, name: str, base_url: str, api_key: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.call_history = []
        self.rate_limit_delay = 1.0  # 默认1秒延迟
        self.max_retries = 3
        self.timeout = 30
        
        # 设置默认请求头
        if api_key:
            self.session.headers.update(self._get_auth_headers())
            
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证头信息"""
        pass
        
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        pass
        
    @abstractmethod
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """分析图像"""
        pass
        
    def make_request(self, method: str, endpoint: str, 
                    data: Optional[Dict] = None,
                    files: Optional[Dict] = None,
                    params: Optional[Dict] = None,
                    headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发起API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            files: 文件数据
            params: URL参数
            headers: 额外的请求头
            
        Returns:
            Dict: API响应结果
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # 合并请求头
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
            
        # 记录请求开始时间
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                # 应用速率限制
                if self.call_history:
                    time_since_last = time.time() - self.call_history[-1]['timestamp']
                    if time_since_last < self.rate_limit_delay:
                        time.sleep(self.rate_limit_delay - time_since_last)
                
                # 发起请求
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    files=files,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                # 记录调用历史
                call_record = {
                    'timestamp': time.time(),
                    'method': method,
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'response_time': time.time() - start_time,
                    'attempt': attempt + 1
                }
                self.call_history.append(call_record)
                
                # 检查响应状态
                if response.status_code == 200:
                    try:
                        result = response.json()
                        call_record['success'] = True
                        return result
                    except json.JSONDecodeError:
                        return {'error': 'Invalid JSON response', 'raw_response': response.text}
                        
                elif response.status_code == 429:  # 速率限制
                    logger.warning(f"{self.name} API速率限制，等待重试...")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                    
                else:
                    error_msg = f"API请求失败: {response.status_code} - {response.text}"
                    call_record['error'] = error_msg
                    
                    if attempt == self.max_retries - 1:
                        return {'error': error_msg, 'status_code': response.status_code}
                    else:
                        logger.warning(f"{self.name} API请求失败，重试中... (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(1)
                        
            except requests.exceptions.Timeout:
                error_msg = f"{self.name} API请求超时"
                if attempt == self.max_retries - 1:
                    return {'error': error_msg}
                logger.warning(f"{error_msg}，重试中...")
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"{self.name} API请求异常: {str(e)}"
                if attempt == self.max_retries - 1:
                    return {'error': error_msg}
                logger.warning(f"{error_msg}，重试中...")
                time.sleep(1)
                
        return {'error': f'{self.name} API请求失败，已达到最大重试次数'}
        
    def get_call_statistics(self) -> Dict[str, Any]:
        """获取调用统计信息"""
        if not self.call_history:
            return {'total_calls': 0}
            
        successful_calls = [call for call in self.call_history if call.get('success', False)]
        failed_calls = [call for call in self.call_history if not call.get('success', False)]
        
        response_times = [call['response_time'] for call in self.call_history if 'response_time' in call]
        
        stats = {
            'total_calls': len(self.call_history),
            'successful_calls': len(successful_calls),
            'failed_calls': len(failed_calls),
            'success_rate': len(successful_calls) / len(self.call_history) if self.call_history else 0,
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'last_call_time': self.call_history[-1]['timestamp'] if self.call_history else None
        }
        
        return stats
        
    def clear_history(self):
        """清空调用历史"""
        self.call_history.clear()
        
    def set_rate_limit(self, delay: float):
        """设置速率限制延迟"""
        self.rate_limit_delay = delay
        
    def set_timeout(self, timeout: int):
        """设置请求超时时间"""
        self.timeout = timeout
        
    def set_max_retries(self, max_retries: int):
        """设置最大重试次数"""
        self.max_retries = max_retries


class MockAPIClient(APIClientBase):
    """模拟API客户端，用于测试"""
    
    def __init__(self, name: str = "MockAPI"):
        super().__init__(name, "http://mock.api", "mock_key")
        self.mock_responses = {}
        self.should_fail = False
        self.fail_probability = 0.0
        
    def _get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}
        
    def test_connection(self) -> Dict[str, Any]:
        if self.should_fail:
            return {'error': 'Mock connection failed'}
        return {'status': 'connected', 'mock': True}
        
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        import random
        
        if self.should_fail or random.random() < self.fail_probability:
            return {'error': 'Mock analysis failed'}
            
        # 返回模拟的情绪分析结果
        emotions = ['happiness', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral']
        primary_emotion = random.choice(emotions)
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': random.uniform(0.6, 0.95),
            'polarity_score': random.uniform(-1.0, 1.0),
            'intensity': random.choice(['low', 'medium', 'high']),
            'mock': True,
            'image_path': image_path
        }
        
    def set_mock_response(self, endpoint: str, response: Dict[str, Any]):
        """设置模拟响应"""
        self.mock_responses[endpoint] = response
        
    def set_failure_mode(self, should_fail: bool = True, probability: float = 0.0):
        """设置失败模式"""
        self.should_fail = should_fail
        self.fail_probability = probability


class APIClientManager:
    """API客户端管理器"""
    
    def __init__(self):
        self.clients = {}
        self.default_client = None
        
    def register_client(self, name: str, client: APIClientBase, is_default: bool = False):
        """注册API客户端"""
        self.clients[name] = client
        if is_default or self.default_client is None:
            self.default_client = name
            
    def get_client(self, name: Optional[str] = None) -> Optional[APIClientBase]:
        """获取API客户端"""
        if name is None:
            name = self.default_client
        return self.clients.get(name)
        
    def test_all_clients(self) -> Dict[str, Dict[str, Any]]:
        """测试所有客户端连接"""
        results = {}
        for name, client in self.clients.items():
            try:
                results[name] = client.test_connection()
            except Exception as e:
                results[name] = {'error': str(e)}
        return results
        
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """获取所有客户端统计信息"""
        stats = {}
        for name, client in self.clients.items():
            stats[name] = client.get_call_statistics()
        return stats
        
    def clear_all_history(self):
        """清空所有客户端历史"""
        for client in self.clients.values():
            client.clear_history()


# 全局API客户端管理器实例
api_manager = APIClientManager()
