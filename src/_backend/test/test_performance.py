#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试模块
用于测试系统各组件的性能指标，建立性能基线
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import cv2
import numpy as np
from datetime import datetime

from ..config import Config
from ..core.capture import capture_images
from ..core.tagger import tag_faces_in_images
from ..core.splicer import splice_images
from ..api.facepp import FacePPClient
from ..api.openrouter import OpenRouterClient
from ..api.gemini import GeminiClient
from ..robot.dsa import DSAAgent
from ..robot.vsa import VSAAgent
from ..robot.jsa import JSAAgent


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    operation: str
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
        self.monitor_thread = None
        self.peak_memory = 0
        self.cpu_samples = []
    
    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self.peak_memory = 0
        self.cpu_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            memory = psutil.virtual_memory().used / 1024 / 1024  # MB
            cpu = psutil.cpu_percent()
            
            self.peak_memory = max(self.peak_memory, memory)
            self.cpu_samples.append(cpu)
            
            time.sleep(0.1)  # 100ms采样间隔
    
    def get_average_cpu(self) -> float:
        """获取平均CPU使用率"""
        return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        self.config = Config()
        self.monitor = PerformanceMonitor()
        self.results: List[PerformanceMetrics] = []
    
    def measure_operation(self, operation_name: str, operation_func, *args, **kwargs) -> PerformanceMetrics:
        """测量单个操作的性能"""
        # 获取初始内存
        memory_before = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # 开始监控
        self.monitor.start_monitoring()
        
        # 执行操作
        start_time = time.time()
        success = True
        error_message = None
        result = None
        
        try:
            result = operation_func(*args, **kwargs)
        except Exception as e:
            success = False
            error_message = str(e)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 获取结束内存
        memory_after = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # 创建性能指标
        metrics = PerformanceMetrics(
            operation=operation_name,
            duration=duration,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=self.monitor.peak_memory,
            cpu_percent=self.monitor.get_average_cpu(),
            success=success,
            error_message=error_message,
            additional_data={'result': result}
        )
        
        self.results.append(metrics)
        return metrics
    
    def test_image_capture(self) -> PerformanceMetrics:
        """测试图像捕获性能"""
        def capture_operation():
            return capture_images(
                camera_index=0,
                num_images=5,
                interval=0.8,
                output_dir=self.config.CAPTURE_DIR
            )
        
        return self.measure_operation("image_capture", capture_operation)
    
    def test_face_detection(self) -> PerformanceMetrics:
        """测试人脸检测性能"""
        def detection_operation():
            # 创建测试图像
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            test_path = self.config.TEMP_DIR / "test_image.jpg"
            cv2.imwrite(str(test_path), test_image)
            
            return tag_faces_in_images(
                input_dir=self.config.TEMP_DIR,
                output_dir=self.config.TAGGER_DIR
            )
        
        return self.measure_operation("face_detection", detection_operation)
    
    def test_image_splicing(self) -> PerformanceMetrics:
        """测试图像拼接性能"""
        def splicing_operation():
            return splice_images(
                capture_dir=self.config.CAPTURE_DIR,
                tagger_dir=self.config.TAGGER_DIR,
                output_dir=self.config.SPLICER_DIR
            )
        
        return self.measure_operation("image_splicing", splicing_operation)
    
    def test_api_calls(self) -> Dict[str, PerformanceMetrics]:
        """测试API调用性能"""
        results = {}
        
        # 创建测试图像
        test_image_path = self.config.TEMP_DIR / "test_api.jpg"
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(str(test_image_path), test_image)
        
        # 测试Face++
        def facepp_operation():
            client = FacePPClient()
            return client.analyze_emotion(str(test_image_path))
        
        results['facepp'] = self.measure_operation("facepp_api", facepp_operation)
        
        # 测试OpenRouter
        def openrouter_operation():
            client = OpenRouterClient()
            return client.analyze_image_emotion(str(test_image_path))
        
        results['openrouter'] = self.measure_operation("openrouter_api", openrouter_operation)
        
        # 测试Gemini
        def gemini_operation():
            client = GeminiClient()
            return client.analyze_image_emotion(str(test_image_path))
        
        results['gemini'] = self.measure_operation("gemini_api", gemini_operation)
        
        return results
    
    def test_agent_analysis(self) -> Dict[str, PerformanceMetrics]:
        """测试智能体分析性能"""
        results = {}
        
        # 模拟数据
        mock_facepp_data = {
            "faces": [
                {
                    "attributes": {
                        "emotion": {
                            "happiness": 85.5,
                            "sadness": 5.2,
                            "anger": 3.1,
                            "fear": 2.8,
                            "surprise": 2.4,
                            "disgust": 1.0,
                            "neutral": 0.0
                        }
                    }
                }
            ]
        }
        
        mock_vsa_data = [
            {
                "primary_emotion": "happiness",
                "intensity": "high",
                "confidence": 0.85
            }
        ]
        
        # 测试DSA
        def dsa_operation():
            agent = DSAAgent()
            return agent.analyze_emotion_data(mock_facepp_data)
        
        results['dsa'] = self.measure_operation("dsa_analysis", dsa_operation)
        
        # 测试VSA
        def vsa_operation():
            agent = VSAAgent()
            return agent.analyze_visual_data(mock_vsa_data)
        
        results['vsa'] = self.measure_operation("vsa_analysis", vsa_operation)
        
        # 测试JSA
        def jsa_operation():
            agent = JSAAgent()
            dsa_result = {"emotion_category": "positive", "polarity_score": 0.8, "confidence": 0.85}
            vsa_result = {"emotion_category": "positive", "polarity_score": 0.75, "confidence": 0.80}
            return agent.make_final_judgment(dsa_result, vsa_result)
        
        results['jsa'] = self.measure_operation("jsa_analysis", jsa_operation)
        
        return results
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """运行完整的性能基准测试"""
        print("🚀 开始性能基准测试...")
        
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}"
            },
            "tests": {}
        }
        
        # 图像处理测试
        print("📸 测试图像捕获...")
        benchmark_results["tests"]["image_capture"] = self.test_image_capture().__dict__
        
        print("👤 测试人脸检测...")
        benchmark_results["tests"]["face_detection"] = self.test_face_detection().__dict__
        
        print("🔗 测试图像拼接...")
        benchmark_results["tests"]["image_splicing"] = self.test_image_splicing().__dict__
        
        # API测试
        print("🌐 测试API调用...")
        api_results = self.test_api_calls()
        benchmark_results["tests"]["api_calls"] = {k: v.__dict__ for k, v in api_results.items()}
        
        # 智能体测试
        print("🤖 测试智能体分析...")
        agent_results = self.test_agent_analysis()
        benchmark_results["tests"]["agent_analysis"] = {k: v.__dict__ for k, v in agent_results.items()}
        
        # 保存结果
        results_file = Path("performance_benchmark.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 性能基准测试完成，结果保存到: {results_file}")
        return benchmark_results
    
    def print_summary(self, results: Dict[str, Any]):
        """打印性能测试摘要"""
        print("\n📊 性能测试摘要")
        print("=" * 50)
        
        for category, tests in results["tests"].items():
            print(f"\n{category.upper()}:")
            
            if isinstance(tests, dict) and "duration" in tests:
                # 单个测试
                self._print_test_result(tests)
            else:
                # 多个测试
                for test_name, test_data in tests.items():
                    print(f"  {test_name}:")
                    self._print_test_result(test_data, indent="    ")
    
    def _print_test_result(self, test_data: Dict[str, Any], indent: str = "  "):
        """打印单个测试结果"""
        status = "✅" if test_data["success"] else "❌"
        print(f"{indent}{status} 耗时: {test_data['duration']:.2f}s")
        print(f"{indent}   内存: {test_data['memory_after'] - test_data['memory_before']:+.1f}MB")
        print(f"{indent}   CPU: {test_data['cpu_percent']:.1f}%")
        
        if not test_data["success"]:
            print(f"{indent}   错误: {test_data['error_message']}")


def main():
    """主函数"""
    tester = PerformanceTester()
    results = tester.run_full_benchmark()
    tester.print_summary(results)


if __name__ == "__main__":
    main()
