"""
工具函数测试
测试utils/function模块中的各种工具函数
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

from src._backend.utils.function.data_converter import (
    image_to_base64, base64_to_image, standardize_emotion_result,
    merge_emotion_results, save_json_result, load_json_result
)
from src._backend.utils.function.time_utils import (
    get_timestamp, parse_timestamp, format_duration, Timer, PerformanceMonitor
)
from src._backend.utils.function.cleaner import (
    quick_clean, clean_by_age, get_directory_size, get_all_directories_info
)
from . import create_test_image, mock_emotion_result, assert_emotion_result_valid


class TestDataConverter:
    """数据转换工具函数测试"""
    
    def test_image_to_base64(self, temp_dirs):
        """测试图像转base64"""
        # 创建测试图像
        image_path = create_test_image()
        
        # 转换为base64
        base64_str = image_to_base64(image_path)
        
        assert base64_str is not None
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0
        
        # 测试不存在的文件
        invalid_path = temp_dirs['temp'] / "nonexistent.jpg"
        result = image_to_base64(invalid_path)
        assert result is None
        
    def test_base64_to_image(self, temp_dirs):
        """测试base64转图像"""
        # 创建测试图像并转换为base64
        original_path = create_test_image()
        base64_str = image_to_base64(original_path)
        
        # 转换回图像
        output_path = temp_dirs['temp'] / "converted.jpg"
        success = base64_to_image(base64_str, output_path)
        
        assert success is True
        assert output_path.exists()
        
        # 测试无效的base64
        invalid_base64 = "invalid_base64_string"
        result = base64_to_image(invalid_base64, temp_dirs['temp'] / "invalid.jpg")
        assert result is False
        
    def test_standardize_emotion_result(self):
        """测试情绪结果标准化"""
        # 测试Face++结果标准化
        facepp_result = {
            'faces': [{
                'attributes': {
                    'emotion': {
                        'happiness': 80.5,
                        'sadness': 10.2,
                        'anger': 5.1,
                        'fear': 2.1,
                        'surprise': 1.8,
                        'disgust': 0.2,
                        'neutral': 0.1
                    }
                }
            }]
        }
        
        standardized = standardize_emotion_result(facepp_result, 'facepp')
        
        assert standardized['source'] == 'facepp'
        assert standardized['dominant_emotion'] == 'happiness'
        assert standardized['emotion_category'] == 'positive'
        assert 0.0 <= standardized['confidence'] <= 1.0
        assert -1.0 <= standardized['polarity_score'] <= 1.0
        
        # 测试AI模型结果标准化
        ai_result = {
            'primary_emotion': 'sadness',
            'confidence': 0.85,
            'polarity_score': -0.6
        }
        
        standardized = standardize_emotion_result(ai_result, 'openrouter')
        
        assert standardized['source'] == 'openrouter'
        assert standardized['dominant_emotion'] == 'sadness'
        assert standardized['emotion_category'] == 'negative'
        
    def test_merge_emotion_results(self):
        """测试情绪结果合并"""
        # 创建多个测试结果
        results = [
            mock_emotion_result('DSA', 'happiness', 0.7, 0.9),
            mock_emotion_result('VSA', 'happiness', 0.6, 0.8),
            mock_emotion_result('JSA', 'happiness', 0.8, 0.85)
        ]
        
        merged = merge_emotion_results(results)
        
        assert merged['results_count'] == 3
        assert 'average_polarity' in merged
        assert 'average_confidence' in merged
        assert 'emotion_consensus' in merged
        assert 'final_category' in merged
        
        # 测试空结果列表
        empty_merged = merge_emotion_results([])
        assert 'error' in empty_merged
        
    def test_save_and_load_json_result(self, temp_dirs):
        """测试JSON保存和加载"""
        test_data = {
            'test_key': 'test_value',
            'number': 42,
            'list': [1, 2, 3],
            'nested': {'inner': 'value'}
        }
        
        # 保存JSON
        filename = "test_result.json"
        success = save_json_result(test_data, filename, temp_dirs['temp'])
        assert success is True
        
        # 加载JSON
        filepath = temp_dirs['temp'] / filename
        loaded_data = load_json_result(filepath)
        
        assert loaded_data is not None
        assert loaded_data == test_data
        
        # 测试加载不存在的文件
        invalid_path = temp_dirs['temp'] / "nonexistent.json"
        result = load_json_result(invalid_path)
        assert result is None


class TestTimeUtils:
    """时间工具函数测试"""
    
    def test_get_timestamp(self):
        """测试时间戳生成"""
        # 测试不同格式
        iso_timestamp = get_timestamp('iso')
        filename_timestamp = get_timestamp('filename')
        readable_timestamp = get_timestamp('readable')
        unix_timestamp = get_timestamp('unix')
        
        assert isinstance(iso_timestamp, str)
        assert isinstance(filename_timestamp, str)
        assert isinstance(readable_timestamp, str)
        assert isinstance(unix_timestamp, str)
        
        # 验证格式
        assert 'T' in iso_timestamp  # ISO格式包含T
        assert '_' in filename_timestamp  # 文件名格式包含下划线
        assert '-' in readable_timestamp  # 可读格式包含连字符
        assert unix_timestamp.isdigit()  # Unix时间戳是数字
        
    def test_parse_timestamp(self):
        """测试时间戳解析"""
        # 测试ISO格式
        iso_str = "2024-12-01T10:30:45.123456"
        parsed = parse_timestamp(iso_str)
        assert parsed is not None
        assert parsed.year == 2024
        assert parsed.month == 12
        assert parsed.day == 1
        
        # 测试文件名格式
        filename_str = "20241201_103045"
        parsed = parse_timestamp(filename_str)
        assert parsed is not None
        
        # 测试无效格式
        invalid_str = "invalid_timestamp"
        parsed = parse_timestamp(invalid_str)
        assert parsed is None
        
    def test_format_duration(self):
        """测试持续时间格式化"""
        # 测试秒
        duration_str = format_duration(30.5)
        assert "30.50秒" in duration_str
        
        # 测试分钟
        duration_str = format_duration(125.0)
        assert "分" in duration_str
        assert "秒" in duration_str
        
        # 测试小时
        duration_str = format_duration(3665.0)
        assert "小时" in duration_str
        assert "分" in duration_str
        
    def test_timer(self):
        """测试计时器"""
        timer = Timer("test_timer")
        
        # 测试基本计时
        timer.start()
        time.sleep(0.1)
        elapsed = timer.stop()
        
        assert elapsed >= 0.1
        assert timer.elapsed_time is not None
        
        # 测试with语句
        with Timer("context_timer") as ctx_timer:
            time.sleep(0.05)
            
        assert ctx_timer.elapsed_time >= 0.05
        
    def test_performance_monitor(self):
        """测试性能监控器"""
        monitor = PerformanceMonitor()
        
        # 测试计时器操作
        monitor.start_timer("test_operation")
        time.sleep(0.1)
        elapsed = monitor.stop_timer("test_operation")
        
        assert elapsed >= 0.1
        
        # 测试统计信息
        stats = monitor.get_statistics()
        assert stats['total_records'] == 1
        assert 'test_operation' in stats['operations']
        
        # 测试清空记录
        monitor.clear_records()
        stats = monitor.get_statistics()
        assert stats['total_records'] == 0


class TestCleanerFunctions:
    """清理工具函数测试"""
    
    def test_get_directory_size(self, temp_dirs):
        """测试目录大小获取"""
        # 创建测试文件
        test_file = temp_dirs['temp'] / "test_file.txt"
        test_content = "test content" * 100
        test_file.write_text(test_content)
        
        # 获取目录大小
        size_info = get_directory_size(temp_dirs['temp'])
        
        assert size_info['files'] >= 1
        assert size_info['size_bytes'] > 0
        assert size_info['size_mb'] >= 0
        
        # 测试不存在的目录
        invalid_dir = temp_dirs['temp'] / "nonexistent"
        size_info = get_directory_size(invalid_dir)
        assert 'error' in size_info
        
    def test_get_all_directories_info(self, temp_dirs):
        """测试所有目录信息获取"""
        # 创建一些测试文件
        for i in range(3):
            test_file = temp_dirs['capture'] / f"test_{i}.txt"
            test_file.write_text(f"test content {i}")
            
        info = get_all_directories_info()
        
        assert isinstance(info, dict)
        assert 'capture' in info
        assert 'tagger' in info
        assert 'splicer' in info
        
        # 验证信息结构
        for dir_name, dir_info in info.items():
            assert 'files' in dir_info
            assert 'size_bytes' in dir_info
            assert 'path' in dir_info
            assert 'exists' in dir_info
            
    def test_clean_by_age(self, temp_dirs):
        """测试按年龄清理文件"""
        # 创建测试文件
        old_file = temp_dirs['capture'] / "old_file.txt"
        old_file.write_text("old content")
        
        # 修改文件时间（模拟旧文件）
        import os
        old_time = time.time() - 25 * 3600  # 25小时前
        os.utime(old_file, (old_time, old_time))
        
        # 创建新文件
        new_file = temp_dirs['capture'] / "new_file.txt"
        new_file.write_text("new content")
        
        # 按年龄清理（24小时）
        results = clean_by_age(24, ['capture'])
        
        assert results['total'] >= 1
        assert not old_file.exists()  # 旧文件应该被删除
        assert new_file.exists()     # 新文件应该保留
        
    @patch('src._backend.core.cleaner.clean_all_files')
    def test_quick_clean(self, mock_clean_all):
        """测试快速清理"""
        # 模拟清理结果
        mock_clean_all.return_value = {'total': 5, 'capture': 2, 'tagger': 3}
        
        result = quick_clean(keep_final=True)
        
        assert result['total'] == 5
        mock_clean_all.assert_called_once_with(keep_splicer_final=True)
        
        # 测试异常情况
        mock_clean_all.side_effect = Exception("Clean failed")
        result = quick_clean()
        
        assert 'error' in result


@pytest.mark.integration
class TestUtilsIntegration:
    """工具函数集成测试"""
    
    def test_image_processing_pipeline(self, temp_dirs):
        """测试图像处理流水线"""
        # 创建测试图像
        image_path = create_test_image()
        
        # 转换为base64
        base64_str = image_to_base64(image_path)
        assert base64_str is not None
        
        # 转换回图像
        output_path = temp_dirs['temp'] / "pipeline_output.jpg"
        success = base64_to_image(base64_str, output_path)
        assert success is True
        
        # 验证文件存在
        assert output_path.exists()
        
    def test_emotion_analysis_pipeline(self):
        """测试情绪分析流水线"""
        # 创建模拟结果
        dsa_result = mock_emotion_result('DSA', 'happiness', 0.7, 0.9)
        vsa_result = mock_emotion_result('VSA', 'happiness', 0.6, 0.8)
        
        # 验证结果有效性
        assert_emotion_result_valid(dsa_result)
        assert_emotion_result_valid(vsa_result)
        
        # 合并结果
        merged = merge_emotion_results([dsa_result, vsa_result])
        assert merged['results_count'] == 2
        assert merged['final_category'] == 'positive'
        
    def test_performance_monitoring_pipeline(self):
        """测试性能监控流水线"""
        monitor = PerformanceMonitor()
        
        # 模拟多个操作
        operations = ['capture', 'tagger', 'splicer', 'analysis']
        
        for op in operations:
            monitor.start_timer(op)
            time.sleep(0.01)  # 模拟操作时间
            monitor.stop_timer(op)
            
        # 获取统计信息
        stats = monitor.get_statistics()
        
        assert stats['total_records'] == len(operations)
        for op in operations:
            assert op in stats['operations']
            assert stats['operations'][op]['count'] == 1
