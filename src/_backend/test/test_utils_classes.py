"""
工具类测试
测试utils/class模块中的各种工具类
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path

from src._backend.utils.classpy.api_client import APIClientBase, MockAPIClient, APIClientManager
from src._backend.utils.classpy.data_models import (
    EmotionResult, ConsistencyAnalysis, FinalJudgment, AnalysisWorkflow,
    DataValidator, DataSerializer
)
from src._backend.utils.classpy.capture import ImageProcessor
from . import create_test_image, mock_emotion_result


class TestAPIClient:
    """API客户端测试"""

    def test_mock_api_client(self):
        """测试模拟API客户端"""
        client = MockAPIClient("TestMock")

        # 测试连接
        result = client.test_connection()
        assert result['status'] == 'connected'
        assert result['mock'] is True

        # 测试图像分析
        analysis_result = client.analyze_image("test_image.jpg")
        assert 'primary_emotion' in analysis_result
        assert 'confidence' in analysis_result
        assert 'polarity_score' in analysis_result
        assert analysis_result['mock'] is True

        # 测试失败模式
        client.set_failure_mode(should_fail=True)
        result = client.test_connection()
        assert 'error' in result

        analysis_result = client.analyze_image("test_image.jpg")
        assert 'error' in analysis_result

    def test_api_client_statistics(self):
        """测试API客户端统计"""
        client = MockAPIClient("StatTest")

        # 进行几次调用
        for i in range(5):
            client.analyze_image(f"test_{i}.jpg")

        stats = client.get_call_statistics()

        assert stats['total_calls'] == 5
        assert stats['successful_calls'] == 5
        assert stats['failed_calls'] == 0
        assert stats['success_rate'] == 1.0

        # 测试失败情况
        client.set_failure_mode(probability=0.5)
        for i in range(10):
            client.analyze_image(f"fail_test_{i}.jpg")

        stats = client.get_call_statistics()
        assert stats['total_calls'] == 15  # 5 + 10
        assert stats['success_rate'] < 1.0

    def test_api_client_manager(self):
        """测试API客户端管理器"""
        manager = APIClientManager()

        # 注册客户端
        client1 = MockAPIClient("Client1")
        client2 = MockAPIClient("Client2")

        manager.register_client("client1", client1, is_default=True)
        manager.register_client("client2", client2)

        # 测试获取客户端
        default_client = manager.get_client()
        assert default_client is client1

        specific_client = manager.get_client("client2")
        assert specific_client is client2

        # 测试所有客户端
        test_results = manager.test_all_clients()
        assert 'client1' in test_results
        assert 'client2' in test_results

        # 测试统计信息
        stats = manager.get_all_statistics()
        assert 'client1' in stats
        assert 'client2' in stats


class TestDataModels:
    """数据模型测试"""

    def test_emotion_result(self):
        """测试情绪结果模型"""
        # 创建情绪结果
        result = EmotionResult(
            agent="TEST",
            timestamp="2024-12-01T10:00:00",
            emotion_category="positive",
            dominant_emotion="happiness",
            polarity_score=0.8,
            confidence=0.9,
            intensity="high",
            reliability="high",
            summary="测试情绪结果"
        )

        # 测试基本属性
        assert result.agent == "TEST"
        assert result.is_positive()
        assert not result.is_negative()
        assert not result.is_neutral()
        assert result.get_intensity_level() == 3

        # 测试字典转换
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict['agent'] == "TEST"

        # 测试从字典创建
        new_result = EmotionResult.from_dict(result_dict)
        assert new_result.agent == result.agent
        assert new_result.polarity_score == result.polarity_score

    def test_emotion_result_validation(self):
        """测试情绪结果验证"""
        # 测试极性分数范围验证
        result = EmotionResult(
            agent="TEST",
            timestamp="2024-12-01T10:00:00",
            emotion_category="positive",
            dominant_emotion="happiness",
            polarity_score=1.5,  # 超出范围
            confidence=1.2,      # 超出范围
            intensity="high",
            reliability="high",
            summary="测试"
        )

        # 验证自动修正
        assert result.polarity_score == 1.0
        assert result.confidence == 1.0

    def test_consistency_analysis(self):
        """测试一致性分析模型"""
        consistency = ConsistencyAnalysis(
            emotion_match=True,
            category_match=True,
            polarity_consistency=0.9,
            confidence_consistency=0.8,
            consistency_score=0.85,
            consistency_level="high",
            consistency_label="高一致性"
        )

        assert consistency.is_high_consistency()
        assert not consistency.is_low_consistency()

        # 测试字典转换
        consistency_dict = consistency.to_dict()
        new_consistency = ConsistencyAnalysis.from_dict(consistency_dict)
        assert new_consistency.consistency_score == consistency.consistency_score

    def test_final_judgment(self):
        """测试最终判定模型"""
        consistency = ConsistencyAnalysis(
            emotion_match=True,
            category_match=True,
            polarity_consistency=0.9,
            confidence_consistency=0.8,
            consistency_score=0.85,
            consistency_level="high",
            consistency_label="高一致性"
        )

        judgment = FinalJudgment(
            emotion_category="positive",
            dominant_emotion="happiness",
            polarity_score=0.8,
            confidence=0.9,
            intensity="high",
            reliability="high",
            summary="最终判定为积极情绪",
            contributing_agents=["DSA", "VSA"],
            consistency_analysis=consistency
        )

        # 测试字典转换
        judgment_dict = judgment.to_dict()
        assert 'consistency_analysis' in judgment_dict

        new_judgment = FinalJudgment.from_dict(judgment_dict)
        assert new_judgment.emotion_category == judgment.emotion_category
        assert new_judgment.consistency_analysis.consistency_score == consistency.consistency_score

    def test_analysis_workflow(self):
        """测试分析工作流模型"""
        workflow = AnalysisWorkflow(
            workflow_id="test_workflow_001",
            workflow_type="complete",
            start_time="2024-12-01T10:00:00",
            end_time=None,
            status="running",
            steps_completed=2,
            total_steps=5,
            agent_results={},
            final_judgment=None,
            error_messages=[]
        )

        # 测试添加智能体结果
        emotion_result = EmotionResult(
            agent="DSA",
            timestamp="2024-12-01T10:01:00",
            emotion_category="positive",
            dominant_emotion="happiness",
            polarity_score=0.8,
            confidence=0.9,
            intensity="high",
            reliability="high",
            summary="DSA分析结果"
        )

        workflow.add_agent_result("DSA", emotion_result)
        assert "DSA" in workflow.agent_results

        # 测试进度计算
        progress = workflow.get_progress()
        assert progress == 0.4  # 2/5

        # 测试标记完成
        workflow.mark_completed()
        assert workflow.status == "completed"
        assert workflow.end_time is not None

        # 测试持续时间
        duration = workflow.get_duration()
        assert duration is not None
        assert duration >= 0

    def test_data_validator(self):
        """测试数据验证器"""
        # 测试有效的情绪结果
        valid_data = {
            'agent': 'TEST',
            'timestamp': '2024-12-01T10:00:00',
            'emotion_category': 'positive',
            'dominant_emotion': 'happiness',
            'polarity_score': 0.8,
            'confidence': 0.9,
            'intensity': 'high',
            'reliability': 'high',
            'summary': '测试结果'
        }

        assert DataValidator.validate_emotion_result(valid_data) is True

        # 测试无效数据
        invalid_data = valid_data.copy()
        invalid_data['polarity_score'] = 2.0  # 超出范围

        assert DataValidator.validate_emotion_result(invalid_data) is False

        # 测试缺少字段
        incomplete_data = valid_data.copy()
        del incomplete_data['agent']

        assert DataValidator.validate_emotion_result(incomplete_data) is False

    def test_data_serializer(self, temp_dirs):
        """测试数据序列化器"""
        # 创建测试数据
        emotion_result = EmotionResult(
            agent="TEST",
            timestamp="2024-12-01T10:00:00",
            emotion_category="positive",
            dominant_emotion="happiness",
            polarity_score=0.8,
            confidence=0.9,
            intensity="high",
            reliability="high",
            summary="测试序列化"
        )

        # 序列化到文件
        filepath = temp_dirs['temp'] / "test_emotion.json"
        success = DataSerializer.serialize_to_json(emotion_result, str(filepath))
        assert success is True
        assert filepath.exists()

        # 反序列化
        loaded_result = DataSerializer.deserialize_from_json(str(filepath), EmotionResult)
        assert loaded_result is not None
        assert loaded_result.agent == emotion_result.agent
        assert loaded_result.polarity_score == emotion_result.polarity_score


class TestImageProcessor:
    """图像处理器测试"""

    def test_image_processor_initialization(self):
        """测试图像处理器初始化"""
        processor = ImageProcessor()

        # 验证级联分类器加载
        assert processor.face_cascade is not None
        assert processor.eye_cascade is not None
        assert processor.smile_cascade is not None

    def test_detect_faces_advanced(self):
        """测试高级人脸检测"""
        processor = ImageProcessor()

        # 创建测试图像（简单的灰度图像）
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128

        # 由于这是单元测试，我们主要测试函数不会崩溃
        # 实际的人脸检测需要真实的人脸图像
        results = processor.detect_faces_advanced(test_image)

        assert isinstance(results, list)
        # 对于纯灰色图像，不应该检测到人脸
        assert len(results) == 0

    def test_enhance_image(self):
        """测试图像增强"""
        processor = ImageProcessor()

        # 创建测试图像
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128

        # 测试亮度调整
        enhanced = processor.enhance_image(test_image, brightness=20)
        assert enhanced.shape == test_image.shape
        assert np.mean(enhanced) > np.mean(test_image)

        # 测试对比度调整
        enhanced = processor.enhance_image(test_image, contrast=1.5)
        assert enhanced.shape == test_image.shape

        # 测试伽马校正
        enhanced = processor.enhance_image(test_image, gamma=0.8)
        assert enhanced.shape == test_image.shape

    def test_add_watermark(self):
        """测试添加水印"""
        processor = ImageProcessor()

        # 创建测试图像
        test_image = np.ones((200, 300, 3), dtype=np.uint8) * 128

        # 添加水印
        watermarked = processor.add_watermark(test_image, "TEST WATERMARK")

        assert watermarked.shape == test_image.shape
        # 水印图像应该与原图像不同
        assert not np.array_equal(watermarked, test_image)

        # 测试不同位置
        positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        for position in positions:
            watermarked = processor.add_watermark(test_image, "TEST", position=position)
            assert watermarked.shape == test_image.shape

    def test_create_collage(self):
        """测试创建拼贴"""
        processor = ImageProcessor()

        # 创建多个测试图像
        images = []
        for i in range(4):
            img = np.ones((100, 100, 3), dtype=np.uint8) * (50 + i * 50)
            images.append(img)

        # 创建拼贴
        collage = processor.create_collage(images)

        assert collage is not None
        assert collage.shape[0] > 100  # 高度应该大于单个图像
        assert collage.shape[1] > 100  # 宽度应该大于单个图像

        # 测试指定网格大小
        collage = processor.create_collage(images, grid_size=(2, 2))
        assert collage is not None

        # 测试空图像列表
        empty_collage = processor.create_collage([])
        assert empty_collage is None


@pytest.mark.integration
class TestUtilsClassesIntegration:
    """工具类集成测试"""

    def test_api_client_with_data_models(self):
        """测试API客户端与数据模型的集成"""
        client = MockAPIClient("IntegrationTest")

        # 获取分析结果
        raw_result = client.analyze_image("test.jpg")

        # 转换为标准化数据模型
        emotion_result = EmotionResult(
            agent="MockAPI",
            timestamp="2024-12-01T10:00:00",
            emotion_category="positive" if raw_result['polarity_score'] > 0 else "negative",
            dominant_emotion=raw_result['primary_emotion'],
            polarity_score=raw_result['polarity_score'],
            confidence=raw_result['confidence'],
            intensity=raw_result['intensity'],
            reliability="high",
            summary=f"Mock分析结果: {raw_result['primary_emotion']}",
            raw_data=raw_result
        )

        # 验证数据模型
        assert emotion_result.agent == "MockAPI"
        assert emotion_result.raw_data == raw_result

    def test_image_processor_with_real_workflow(self, temp_dirs):
        """测试图像处理器在真实工作流中的应用"""
        processor = ImageProcessor()

        # 创建测试图像
        test_images = []
        for i in range(3):
            img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
            test_images.append(img)

        # 增强所有图像
        enhanced_images = []
        for img in test_images:
            enhanced = processor.enhance_image(img, brightness=10, contrast=1.1)
            enhanced_images.append(enhanced)

        # 创建拼贴
        collage = processor.create_collage(enhanced_images)
        assert collage is not None

        # 添加水印
        final_image = processor.add_watermark(collage, "FaceAna-MTQ Test")
        assert final_image is not None
        assert final_image.shape == collage.shape
