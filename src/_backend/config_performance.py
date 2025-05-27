#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化配置模块
包含性能相关的配置参数和优化选项
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PerformanceConfig:
    """性能配置类"""
    
    # 图像处理优化
    USE_GPU_ACCELERATION: bool = False  # 是否使用GPU加速
    OPENCV_NUM_THREADS: int = 4  # OpenCV线程数
    IMAGE_PROCESSING_BATCH_SIZE: int = 5  # 批处理大小
    IMAGE_RESIZE_QUALITY: str = "medium"  # 图像缩放质量: low, medium, high
    ENABLE_IMAGE_CACHE: bool = True  # 是否启用图像缓存
    
    # 并发处理优化
    MAX_WORKER_THREADS: int = 4  # 最大工作线程数
    ENABLE_ASYNC_PROCESSING: bool = True  # 是否启用异步处理
    THREAD_POOL_SIZE: int = 8  # 线程池大小
    PROCESS_POOL_SIZE: int = 2  # 进程池大小
    
    # API调用优化
    API_CONNECTION_POOL_SIZE: int = 10  # 连接池大小
    API_REQUEST_TIMEOUT: int = 30  # 请求超时时间(秒)
    API_MAX_RETRIES: int = 3  # 最大重试次数
    API_RETRY_DELAY: float = 1.0  # 重试延迟(秒)
    ENABLE_API_CACHE: bool = True  # 是否启用API缓存
    API_CACHE_TTL: int = 3600  # API缓存过期时间(秒)
    
    # 内存管理优化
    MAX_MEMORY_USAGE_MB: int = 1024  # 最大内存使用(MB)
    ENABLE_MEMORY_MONITORING: bool = True  # 是否启用内存监控
    MEMORY_CLEANUP_THRESHOLD: float = 0.8  # 内存清理阈值
    GARBAGE_COLLECTION_INTERVAL: int = 60  # 垃圾回收间隔(秒)
    
    # 缓存配置
    CACHE_TYPE: str = "memory"  # 缓存类型: memory, redis, file
    CACHE_MAX_SIZE: int = 100  # 缓存最大条目数
    CACHE_DEFAULT_TTL: int = 1800  # 默认缓存过期时间(秒)
    
    # 日志和监控
    ENABLE_PERFORMANCE_LOGGING: bool = True  # 是否启用性能日志
    PERFORMANCE_LOG_LEVEL: str = "INFO"  # 性能日志级别
    ENABLE_METRICS_COLLECTION: bool = True  # 是否启用指标收集
    METRICS_COLLECTION_INTERVAL: int = 10  # 指标收集间隔(秒)
    
    # GPU加速配置
    CUDA_DEVICE_ID: int = 0  # CUDA设备ID
    ENABLE_CUDA_MEMORY_POOL: bool = True  # 是否启用CUDA内存池
    CUDA_MEMORY_FRACTION: float = 0.7  # CUDA内存使用比例
    
    # 文件I/O优化
    FILE_BUFFER_SIZE: int = 8192  # 文件缓冲区大小
    ENABLE_ASYNC_FILE_IO: bool = True  # 是否启用异步文件I/O
    TEMP_FILE_CLEANUP_INTERVAL: int = 300  # 临时文件清理间隔(秒)
    
    @classmethod
    def from_env(cls) -> 'PerformanceConfig':
        """从环境变量创建配置"""
        return cls(
            USE_GPU_ACCELERATION=os.getenv('USE_GPU_ACCELERATION', 'false').lower() == 'true',
            OPENCV_NUM_THREADS=int(os.getenv('OPENCV_NUM_THREADS', '4')),
            IMAGE_PROCESSING_BATCH_SIZE=int(os.getenv('IMAGE_PROCESSING_BATCH_SIZE', '5')),
            IMAGE_RESIZE_QUALITY=os.getenv('IMAGE_RESIZE_QUALITY', 'medium'),
            ENABLE_IMAGE_CACHE=os.getenv('ENABLE_IMAGE_CACHE', 'true').lower() == 'true',
            
            MAX_WORKER_THREADS=int(os.getenv('MAX_WORKER_THREADS', '4')),
            ENABLE_ASYNC_PROCESSING=os.getenv('ENABLE_ASYNC_PROCESSING', 'true').lower() == 'true',
            THREAD_POOL_SIZE=int(os.getenv('THREAD_POOL_SIZE', '8')),
            PROCESS_POOL_SIZE=int(os.getenv('PROCESS_POOL_SIZE', '2')),
            
            API_CONNECTION_POOL_SIZE=int(os.getenv('API_CONNECTION_POOL_SIZE', '10')),
            API_REQUEST_TIMEOUT=int(os.getenv('API_REQUEST_TIMEOUT', '30')),
            API_MAX_RETRIES=int(os.getenv('API_MAX_RETRIES', '3')),
            API_RETRY_DELAY=float(os.getenv('API_RETRY_DELAY', '1.0')),
            ENABLE_API_CACHE=os.getenv('ENABLE_API_CACHE', 'true').lower() == 'true',
            API_CACHE_TTL=int(os.getenv('API_CACHE_TTL', '3600')),
            
            MAX_MEMORY_USAGE_MB=int(os.getenv('MAX_MEMORY_USAGE_MB', '1024')),
            ENABLE_MEMORY_MONITORING=os.getenv('ENABLE_MEMORY_MONITORING', 'true').lower() == 'true',
            MEMORY_CLEANUP_THRESHOLD=float(os.getenv('MEMORY_CLEANUP_THRESHOLD', '0.8')),
            GARBAGE_COLLECTION_INTERVAL=int(os.getenv('GARBAGE_COLLECTION_INTERVAL', '60')),
            
            CACHE_TYPE=os.getenv('CACHE_TYPE', 'memory'),
            CACHE_MAX_SIZE=int(os.getenv('CACHE_MAX_SIZE', '100')),
            CACHE_DEFAULT_TTL=int(os.getenv('CACHE_DEFAULT_TTL', '1800')),
            
            ENABLE_PERFORMANCE_LOGGING=os.getenv('ENABLE_PERFORMANCE_LOGGING', 'true').lower() == 'true',
            PERFORMANCE_LOG_LEVEL=os.getenv('PERFORMANCE_LOG_LEVEL', 'INFO'),
            ENABLE_METRICS_COLLECTION=os.getenv('ENABLE_METRICS_COLLECTION', 'true').lower() == 'true',
            METRICS_COLLECTION_INTERVAL=int(os.getenv('METRICS_COLLECTION_INTERVAL', '10')),
            
            CUDA_DEVICE_ID=int(os.getenv('CUDA_DEVICE_ID', '0')),
            ENABLE_CUDA_MEMORY_POOL=os.getenv('ENABLE_CUDA_MEMORY_POOL', 'true').lower() == 'true',
            CUDA_MEMORY_FRACTION=float(os.getenv('CUDA_MEMORY_FRACTION', '0.7')),
            
            FILE_BUFFER_SIZE=int(os.getenv('FILE_BUFFER_SIZE', '8192')),
            ENABLE_ASYNC_FILE_IO=os.getenv('ENABLE_ASYNC_FILE_IO', 'true').lower() == 'true',
            TEMP_FILE_CLEANUP_INTERVAL=int(os.getenv('TEMP_FILE_CLEANUP_INTERVAL', '300')),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    def save_to_file(self, file_path: Path):
        """保存配置到文件"""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'PerformanceConfig':
        """从文件加载配置"""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig.from_env()
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """设置优化选项"""
        # OpenCV优化
        import cv2
        cv2.setNumThreads(self.config.OPENCV_NUM_THREADS)
        cv2.setUseOptimized(True)
        
        # 设置环境变量
        if self.config.USE_GPU_ACCELERATION:
            os.environ['OPENCV_DNN_BACKEND'] = 'CUDA'
            os.environ['OPENCV_DNN_TARGET'] = 'CUDA'
        
        # 内存优化
        if self.config.ENABLE_MEMORY_MONITORING:
            self._setup_memory_monitoring()
    
    def _setup_memory_monitoring(self):
        """设置内存监控"""
        import gc
        import threading
        
        def memory_monitor():
            import psutil
            while True:
                memory_percent = psutil.virtual_memory().percent / 100
                if memory_percent > self.config.MEMORY_CLEANUP_THRESHOLD:
                    gc.collect()
                
                import time
                time.sleep(self.config.GARBAGE_COLLECTION_INTERVAL)
        
        monitor_thread = threading.Thread(target=memory_monitor, daemon=True)
        monitor_thread.start()
    
    def get_optimal_thread_count(self) -> int:
        """获取最优线程数"""
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        return min(self.config.MAX_WORKER_THREADS, cpu_count)
    
    def get_optimal_batch_size(self, available_memory_mb: float) -> int:
        """根据可用内存计算最优批处理大小"""
        # 估算每张图片需要的内存（假设640x480 RGB图片）
        estimated_memory_per_image = (640 * 480 * 3 * 4) / 1024 / 1024  # 约3.7MB
        
        max_batch_size = int(available_memory_mb * 0.5 / estimated_memory_per_image)
        return min(max_batch_size, self.config.IMAGE_PROCESSING_BATCH_SIZE)
    
    def optimize_opencv_for_performance(self):
        """优化OpenCV性能设置"""
        import cv2
        
        # 启用优化
        cv2.setUseOptimized(True)
        
        # 设置线程数
        cv2.setNumThreads(self.config.OPENCV_NUM_THREADS)
        
        # 如果支持GPU，启用GPU加速
        if self.config.USE_GPU_ACCELERATION:
            try:
                # 检查CUDA支持
                if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                    cv2.cuda.setDevice(self.config.CUDA_DEVICE_ID)
                    return True
            except:
                pass
        
        return False
    
    def create_optimized_session_config(self) -> Dict[str, Any]:
        """创建优化的会话配置"""
        return {
            'thread_pool_size': self.get_optimal_thread_count(),
            'batch_size': self.config.IMAGE_PROCESSING_BATCH_SIZE,
            'use_gpu': self.config.USE_GPU_ACCELERATION,
            'memory_limit_mb': self.config.MAX_MEMORY_USAGE_MB,
            'enable_cache': self.config.ENABLE_IMAGE_CACHE,
            'cache_ttl': self.config.CACHE_DEFAULT_TTL
        }


# 全局性能配置实例
PERFORMANCE_CONFIG = PerformanceConfig.from_env()
PERFORMANCE_OPTIMIZER = PerformanceOptimizer(PERFORMANCE_CONFIG)


def get_performance_config() -> PerformanceConfig:
    """获取性能配置"""
    return PERFORMANCE_CONFIG


def get_performance_optimizer() -> PerformanceOptimizer:
    """获取性能优化器"""
    return PERFORMANCE_OPTIMIZER


def apply_performance_optimizations():
    """应用性能优化"""
    optimizer = get_performance_optimizer()
    gpu_enabled = optimizer.optimize_opencv_for_performance()
    
    print(f"🚀 性能优化已应用:")
    print(f"   - OpenCV线程数: {optimizer.config.OPENCV_NUM_THREADS}")
    print(f"   - GPU加速: {'✅' if gpu_enabled else '❌'}")
    print(f"   - 最大工作线程: {optimizer.get_optimal_thread_count()}")
    print(f"   - 批处理大小: {optimizer.config.IMAGE_PROCESSING_BATCH_SIZE}")
    print(f"   - 内存监控: {'✅' if optimizer.config.ENABLE_MEMORY_MONITORING else '❌'}")
    
    return optimizer.create_optimized_session_config()


if __name__ == "__main__":
    # 测试性能配置
    config = get_performance_config()
    print("性能配置:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    
    print("\n应用性能优化...")
    session_config = apply_performance_optimizations()
    print(f"\n会话配置: {session_config}")
