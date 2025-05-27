"""
测试模块初始化
提供测试基础设施和公共工具
"""

import os
import sys
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src._backend.config import config

# 配置测试日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 测试配置
TEST_CONFIG = {
    'use_mock_apis': True,  # 默认使用模拟API
    'create_temp_dirs': True,  # 创建临时目录
    'cleanup_after_test': True,  # 测试后清理
    'mock_camera': True,  # 模拟摄像头
    'test_data_dir': project_root / 'src' / '_backend' / 'test' / 'test_data'
}


class TestEnvironment:
    """测试环境管理器"""
    
    def __init__(self):
        self.temp_dirs = {}
        self.original_config = {}
        self.mock_objects = {}
        
    def setup(self):
        """设置测试环境"""
        # 创建临时目录
        if TEST_CONFIG['create_temp_dirs']:
            self._create_temp_directories()
            
        # 备份原始配置
        self._backup_config()
        
        # 设置测试配置
        self._setup_test_config()
        
    def teardown(self):
        """清理测试环境"""
        # 恢复原始配置
        self._restore_config()
        
        # 清理临时目录
        if TEST_CONFIG['cleanup_after_test']:
            self._cleanup_temp_directories()
            
    def _create_temp_directories(self):
        """创建临时目录"""
        temp_base = tempfile.mkdtemp(prefix='faceana_test_')
        
        self.temp_dirs = {
            'base': Path(temp_base),
            'data': Path(temp_base) / 'data',
            'capture': Path(temp_base) / 'data' / 'capture',
            'tagger': Path(temp_base) / 'data' / 'tagger',
            'splicer': Path(temp_base) / 'data' / 'splicer',
            'temp': Path(temp_base) / 'data' / 'temp',
            'logs': Path(temp_base) / 'logs'
        }
        
        # 创建所有目录
        for dir_path in self.temp_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def _cleanup_temp_directories(self):
        """清理临时目录"""
        if 'base' in self.temp_dirs and self.temp_dirs['base'].exists():
            shutil.rmtree(self.temp_dirs['base'])
            
    def _backup_config(self):
        """备份原始配置"""
        self.original_config = {
            'DATA_DIR': config.DATA_DIR,
            'CAPTURE_DIR': config.CAPTURE_DIR,
            'TAGGER_DIR': config.TAGGER_DIR,
            'SPLICER_DIR': config.SPLICER_DIR,
            'TEMP_DIR': config.TEMP_DIR,
            'LOGS_DIR': config.LOGS_DIR
        }
        
    def _setup_test_config(self):
        """设置测试配置"""
        if TEST_CONFIG['create_temp_dirs']:
            # 使用临时目录
            config.DATA_DIR = self.temp_dirs['data']
            config.CAPTURE_DIR = self.temp_dirs['capture']
            config.TAGGER_DIR = self.temp_dirs['tagger']
            config.SPLICER_DIR = self.temp_dirs['splicer']
            config.TEMP_DIR = self.temp_dirs['temp']
            config.LOGS_DIR = self.temp_dirs['logs']
            
    def _restore_config(self):
        """恢复原始配置"""
        for key, value in self.original_config.items():
            setattr(config, key, value)
            
    def get_temp_dir(self, name: str) -> Optional[Path]:
        """获取临时目录路径"""
        return self.temp_dirs.get(name)


# 全局测试环境实例
test_env = TestEnvironment()


def setup_module():
    """模块级别的设置"""
    test_env.setup()


def teardown_module():
    """模块级别的清理"""
    test_env.teardown()


# pytest fixtures
@pytest.fixture(scope="session")
def test_environment():
    """测试环境fixture"""
    env = TestEnvironment()
    env.setup()
    yield env
    env.teardown()


@pytest.fixture
def temp_dirs(test_environment):
    """临时目录fixture"""
    return test_environment.temp_dirs


@pytest.fixture
def mock_config(test_environment):
    """模拟配置fixture"""
    return {
        'use_mock_apis': TEST_CONFIG['use_mock_apis'],
        'mock_camera': TEST_CONFIG['mock_camera'],
        'test_data_dir': TEST_CONFIG['test_data_dir']
    }


# 测试工具函数
def create_test_image(width: int = 640, height: int = 480, 
                     color: tuple = (128, 128, 128)) -> Path:
    """
    创建测试图像
    
    Args:
        width: 图像宽度
        height: 图像高度
        color: 图像颜色 (R, G, B)
        
    Returns:
        Path: 测试图像路径
    """
    try:
        from PIL import Image
        import numpy as np
        
        # 创建图像数组
        image_array = np.full((height, width, 3), color, dtype=np.uint8)
        
        # 转换为PIL图像
        image = Image.fromarray(image_array)
        
        # 保存到临时目录
        temp_dir = test_env.get_temp_dir('temp')
        if temp_dir is None:
            temp_dir = Path(tempfile.gettempdir())
            
        image_path = temp_dir / f"test_image_{width}x{height}.jpg"
        image.save(image_path)
        
        return image_path
        
    except Exception as e:
        logging.error(f"创建测试图像失败: {e}")
        raise


def create_test_images(count: int = 5) -> list:
    """
    创建多个测试图像
    
    Args:
        count: 图像数量
        
    Returns:
        list: 测试图像路径列表
    """
    images = []
    colors = [
        (255, 0, 0),    # 红色
        (0, 255, 0),    # 绿色
        (0, 0, 255),    # 蓝色
        (255, 255, 0),  # 黄色
        (255, 0, 255),  # 紫色
    ]
    
    for i in range(count):
        color = colors[i % len(colors)]
        image_path = create_test_image(color=color)
        images.append(str(image_path))
        
    return images


def mock_emotion_result(agent: str = "TEST", 
                       emotion: str = "happiness",
                       polarity: float = 0.5,
                       confidence: float = 0.8) -> Dict[str, Any]:
    """
    创建模拟情绪分析结果
    
    Args:
        agent: 智能体名称
        emotion: 主导情绪
        polarity: 极性分数
        confidence: 置信度
        
    Returns:
        Dict: 模拟结果
    """
    from datetime import datetime
    
    return {
        'agent': agent,
        'timestamp': datetime.now().isoformat(),
        'emotion_category': 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral',
        'dominant_emotion': emotion,
        'polarity_score': polarity,
        'confidence': confidence,
        'intensity': 'high' if abs(polarity) > 0.7 else 'medium' if abs(polarity) > 0.3 else 'low',
        'reliability': 'high' if confidence > 0.8 else 'medium' if confidence > 0.5 else 'low',
        'summary': f"检测到{emotion}情绪，极性分数{polarity:.3f}，置信度{confidence:.3f}"
    }


def assert_emotion_result_valid(result: Dict[str, Any]):
    """
    验证情绪分析结果的有效性
    
    Args:
        result: 情绪分析结果
    """
    required_fields = [
        'agent', 'timestamp', 'emotion_category', 'dominant_emotion',
        'polarity_score', 'confidence', 'intensity', 'reliability', 'summary'
    ]
    
    # 检查必需字段
    for field in required_fields:
        assert field in result, f"缺少必需字段: {field}"
        
    # 检查数值范围
    assert -1.0 <= result['polarity_score'] <= 1.0, f"极性分数超出范围: {result['polarity_score']}"
    assert 0.0 <= result['confidence'] <= 1.0, f"置信度超出范围: {result['confidence']}"
    
    # 检查枚举值
    valid_categories = ['positive', 'negative', 'neutral']
    assert result['emotion_category'] in valid_categories, f"无效的情绪类别: {result['emotion_category']}"
    
    valid_intensities = ['low', 'medium', 'high']
    assert result['intensity'] in valid_intensities, f"无效的情绪强度: {result['intensity']}"


def skip_if_no_camera():
    """如果没有摄像头则跳过测试"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if TEST_CONFIG['mock_camera']:
                pytest.skip("使用模拟摄像头，跳过真实摄像头测试")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def skip_if_no_api_keys():
    """如果没有API密钥则跳过测试"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if TEST_CONFIG['use_mock_apis']:
                pytest.skip("使用模拟API，跳过真实API测试")
            return func(*args, **kwargs)
        return wrapper
    return decorator
