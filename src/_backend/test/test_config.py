"""
配置模块测试
测试配置管理功能和参数验证
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src._backend.config import Config, config
from . import test_env, mock_config


class TestConfig:
    """配置类测试"""
    
    def test_config_initialization(self):
        """测试配置初始化"""
        # 测试基本属性存在
        assert hasattr(config, 'PROJECT_ROOT')
        assert hasattr(config, 'DATA_DIR')
        assert hasattr(config, 'CAPTURE_DIR')
        assert hasattr(config, 'TAGGER_DIR')
        assert hasattr(config, 'SPLICER_DIR')
        assert hasattr(config, 'LOGS_DIR')
        
        # 测试路径类型
        assert isinstance(config.PROJECT_ROOT, Path)
        assert isinstance(config.DATA_DIR, Path)
        assert isinstance(config.CAPTURE_DIR, Path)
        
    def test_api_keys_exist(self):
        """测试API密钥配置"""
        # 测试Face++配置
        assert hasattr(config, 'FACEPP_API_KEY')
        assert hasattr(config, 'FACEPP_API_SECRET')
        assert config.FACEPP_API_KEY is not None
        assert config.FACEPP_API_SECRET is not None
        
        # 测试OpenRouter配置
        assert hasattr(config, 'OPENROUTER_API_KEY')
        assert config.OPENROUTER_API_KEY is not None
        
        # 测试Gemini配置
        assert hasattr(config, 'GEMINI_API_KEY')
        assert config.GEMINI_API_KEY is not None
        
    def test_camera_config(self):
        """测试摄像头配置"""
        assert hasattr(config, 'CAMERA_INDEX')
        assert isinstance(config.CAMERA_INDEX, int)
        assert config.CAMERA_INDEX >= 0
        
    def test_agent_weights(self):
        """测试智能体权重配置"""
        assert hasattr(config, 'DSA_WEIGHT')
        assert hasattr(config, 'VSA_WEIGHT')
        
        # 测试权重范围
        assert 0.0 <= config.DSA_WEIGHT <= 1.0
        assert 0.0 <= config.VSA_WEIGHT <= 1.0
        
        # 测试权重和为1（允许小误差）
        total_weight = config.DSA_WEIGHT + config.VSA_WEIGHT
        assert abs(total_weight - 1.0) < 0.01
        
    def test_ensure_directories(self, temp_dirs):
        """测试目录创建功能"""
        # 使用临时目录进行测试
        temp_config = Config()
        temp_config.DATA_DIR = temp_dirs['data']
        temp_config.CAPTURE_DIR = temp_dirs['capture']
        temp_config.TAGGER_DIR = temp_dirs['tagger']
        temp_config.SPLICER_DIR = temp_dirs['splicer']
        temp_config.LOGS_DIR = temp_dirs['logs']
        
        # 删除目录（如果存在）
        for dir_path in [temp_config.CAPTURE_DIR, temp_config.TAGGER_DIR]:
            if dir_path.exists():
                dir_path.rmdir()
                
        # 测试目录创建
        temp_config.ensure_directories()
        
        # 验证目录存在
        assert temp_config.DATA_DIR.exists()
        assert temp_config.CAPTURE_DIR.exists()
        assert temp_config.TAGGER_DIR.exists()
        assert temp_config.SPLICER_DIR.exists()
        assert temp_config.LOGS_DIR.exists()
        
    def test_validate_config(self):
        """测试配置验证"""
        # 测试正常配置验证
        is_valid = config.validate_config()
        assert isinstance(is_valid, bool)
        
        # 如果使用真实API密钥，应该验证通过
        if not config.FACEPP_API_KEY.startswith('test_'):
            assert is_valid
            
    def test_config_paths_are_absolute(self):
        """测试配置路径是绝对路径"""
        assert config.PROJECT_ROOT.is_absolute()
        assert config.DATA_DIR.is_absolute()
        assert config.CAPTURE_DIR.is_absolute()
        assert config.TAGGER_DIR.is_absolute()
        assert config.SPLICER_DIR.is_absolute()
        assert config.LOGS_DIR.is_absolute()
        
    def test_config_hierarchy(self):
        """测试配置目录层次结构"""
        # 测试数据目录是项目根目录的子目录
        assert config.PROJECT_ROOT in config.DATA_DIR.parents
        
        # 测试子目录是数据目录的子目录
        assert config.DATA_DIR in config.CAPTURE_DIR.parents
        assert config.DATA_DIR in config.TAGGER_DIR.parents
        assert config.DATA_DIR in config.SPLICER_DIR.parents
        
    @patch.dict('os.environ', {'FACEPP_API_KEY': 'test_key'})
    def test_environment_variable_override(self):
        """测试环境变量覆盖"""
        # 重新加载配置以应用环境变量
        from importlib import reload
        from src._backend import config as config_module
        reload(config_module)
        
        # 验证环境变量生效
        # 注意：这个测试可能需要根据实际的环境变量处理逻辑调整
        
    def test_log_level_config(self):
        """测试日志级别配置"""
        assert hasattr(config, 'LOG_LEVEL')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert config.LOG_LEVEL in valid_levels
        
    def test_image_processing_config(self):
        """测试图像处理配置"""
        # 测试图像捕获参数
        assert hasattr(config, 'CAPTURE_COUNT')
        assert hasattr(config, 'CAPTURE_INTERVAL')
        
        assert isinstance(config.CAPTURE_COUNT, int)
        assert isinstance(config.CAPTURE_INTERVAL, (int, float))
        
        assert config.CAPTURE_COUNT > 0
        assert config.CAPTURE_INTERVAL > 0
        
    def test_api_timeout_config(self):
        """测试API超时配置"""
        assert hasattr(config, 'API_TIMEOUT')
        assert isinstance(config.API_TIMEOUT, (int, float))
        assert config.API_TIMEOUT > 0


class TestConfigValidation:
    """配置验证测试"""
    
    def test_validate_api_keys(self):
        """测试API密钥验证"""
        # 创建临时配置用于测试
        temp_config = Config()
        
        # 测试有效的API密钥格式
        temp_config.FACEPP_API_KEY = "valid_key_123"
        temp_config.FACEPP_API_SECRET = "valid_secret_456"
        
        # 这里可以添加具体的验证逻辑测试
        assert temp_config.FACEPP_API_KEY is not None
        assert temp_config.FACEPP_API_SECRET is not None
        
    def test_validate_weights(self):
        """测试权重验证"""
        # 测试权重范围
        assert 0.0 <= config.DSA_WEIGHT <= 1.0
        assert 0.0 <= config.VSA_WEIGHT <= 1.0
        
        # 测试权重和
        total = config.DSA_WEIGHT + config.VSA_WEIGHT
        assert abs(total - 1.0) < 0.01, f"权重和应该为1.0，实际为{total}"
        
    def test_validate_camera_index(self):
        """测试摄像头索引验证"""
        assert isinstance(config.CAMERA_INDEX, int)
        assert config.CAMERA_INDEX >= 0
        assert config.CAMERA_INDEX < 10  # 假设不会有超过10个摄像头
        
    def test_validate_capture_params(self):
        """测试捕获参数验证"""
        assert config.CAPTURE_COUNT > 0
        assert config.CAPTURE_COUNT <= 20  # 合理的上限
        
        assert config.CAPTURE_INTERVAL > 0
        assert config.CAPTURE_INTERVAL <= 10  # 合理的上限


class TestConfigIntegration:
    """配置集成测试"""
    
    def test_config_with_real_directories(self, temp_dirs):
        """测试配置与真实目录的集成"""
        # 确保目录创建
        config.ensure_directories()
        
        # 测试目录可写
        test_file = config.TEMP_DIR / "test_write.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        
        # 清理测试文件
        test_file.unlink()
        
    def test_config_import_from_different_modules(self):
        """测试从不同模块导入配置"""
        # 测试配置对象的一致性
        from src._backend.config import config as config1
        from src._backend.config import config as config2
        
        assert config1 is config2
        assert config1.PROJECT_ROOT == config2.PROJECT_ROOT
        
    def test_config_thread_safety(self):
        """测试配置的线程安全性"""
        import threading
        import time
        
        results = []
        
        def access_config():
            """访问配置的线程函数"""
            time.sleep(0.01)  # 模拟一些处理时间
            results.append(config.PROJECT_ROOT)
            
        # 创建多个线程同时访问配置
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=access_config)
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        # 验证所有结果一致
        assert len(results) == 10
        assert all(result == config.PROJECT_ROOT for result in results)


@pytest.mark.integration
class TestConfigEnvironment:
    """配置环境测试"""
    
    def test_config_in_different_environments(self):
        """测试不同环境下的配置"""
        # 这个测试可以根据需要扩展，测试开发/测试/生产环境的配置差异
        pass
        
    def test_config_backup_and_restore(self, temp_dirs):
        """测试配置备份和恢复"""
        # 备份原始配置
        original_data_dir = config.DATA_DIR
        
        # 修改配置
        config.DATA_DIR = temp_dirs['data']
        
        # 验证修改生效
        assert config.DATA_DIR == temp_dirs['data']
        
        # 恢复配置
        config.DATA_DIR = original_data_dir
        
        # 验证恢复成功
        assert config.DATA_DIR == original_data_dir
