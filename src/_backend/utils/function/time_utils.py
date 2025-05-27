"""
时间处理工具函数
提供时间格式化、计算和管理功能
"""

import time
import logging
from typing import Optional, Union, Dict, List
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)


def get_timestamp(format_type: str = 'iso') -> str:
    """
    获取当前时间戳
    
    Args:
        format_type: 格式类型 ('iso', 'filename', 'readable', 'unix')
        
    Returns:
        str: 格式化的时间戳
    """
    now = datetime.now()
    
    formats = {
        'iso': now.isoformat(),
        'filename': now.strftime("%Y%m%d_%H%M%S"),
        'readable': now.strftime("%Y-%m-%d %H:%M:%S"),
        'unix': str(int(now.timestamp())),
        'microsecond': now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    }
    
    return formats.get(format_type, formats['iso'])


def parse_timestamp(timestamp_str: str, input_format: Optional[str] = None) -> Optional[datetime]:
    """
    解析时间戳字符串
    
    Args:
        timestamp_str: 时间戳字符串
        input_format: 输入格式，None则自动检测
        
    Returns:
        Optional[datetime]: 解析后的datetime对象，失败返回None
    """
    try:
        if input_format:
            return datetime.strptime(timestamp_str, input_format)
            
        # 自动检测常见格式
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%dT%H:%M:%S",     # ISO format
            "%Y%m%d_%H%M%S",         # filename format
            "%Y-%m-%d %H:%M:%S",     # readable format
            "%Y%m%d_%H%M%S_%f"       # microsecond format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
                
        # 尝试Unix时间戳
        try:
            return datetime.fromtimestamp(float(timestamp_str))
        except (ValueError, OSError):
            pass
            
        logger.error(f"无法解析时间戳: {timestamp_str}")
        return None
        
    except Exception as e:
        logger.error(f"解析时间戳失败: {e}")
        return None


def format_duration(seconds: float) -> str:
    """
    格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的持续时间字符串
    """
    try:
        if seconds < 60:
            return f"{seconds:.2f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}分{remaining_seconds:.1f}秒"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            remaining_seconds = seconds % 60
            return f"{hours}小时{remaining_minutes}分{remaining_seconds:.1f}秒"
            
    except Exception as e:
        logger.error(f"格式化持续时间失败: {e}")
        return f"{seconds}秒"


def calculate_time_difference(start_time: Union[str, datetime], 
                            end_time: Union[str, datetime]) -> Optional[float]:
    """
    计算时间差（秒）
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        
    Returns:
        Optional[float]: 时间差（秒），失败返回None
    """
    try:
        if isinstance(start_time, str):
            start_time = parse_timestamp(start_time)
        if isinstance(end_time, str):
            end_time = parse_timestamp(end_time)
            
        if start_time is None or end_time is None:
            return None
            
        diff = end_time - start_time
        return diff.total_seconds()
        
    except Exception as e:
        logger.error(f"计算时间差失败: {e}")
        return None


def get_file_age(file_path: Union[str, Path]) -> Optional[float]:
    """
    获取文件年龄（小时）
    
    Args:
        file_path: 文件路径
        
    Returns:
        Optional[float]: 文件年龄（小时），失败返回None
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
            
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        current_time = datetime.now()
        
        age_seconds = (current_time - file_time).total_seconds()
        return age_seconds / 3600  # 转换为小时
        
    except Exception as e:
        logger.error(f"获取文件年龄失败: {e}")
        return None


def is_file_older_than(file_path: Union[str, Path], hours: float) -> bool:
    """
    检查文件是否超过指定年龄
    
    Args:
        file_path: 文件路径
        hours: 年龄阈值（小时）
        
    Returns:
        bool: 是否超过指定年龄
    """
    age = get_file_age(file_path)
    return age is not None and age > hours


def get_time_range_files(directory: Union[str, Path], 
                        start_time: Union[str, datetime],
                        end_time: Union[str, datetime]) -> List[Path]:
    """
    获取指定时间范围内的文件
    
    Args:
        directory: 目录路径
        start_time: 开始时间
        end_time: 结束时间
        
    Returns:
        List[Path]: 符合条件的文件路径列表
    """
    try:
        directory = Path(directory)
        if not directory.exists():
            return []
            
        if isinstance(start_time, str):
            start_time = parse_timestamp(start_time)
        if isinstance(end_time, str):
            end_time = parse_timestamp(end_time)
            
        if start_time is None or end_time is None:
            return []
            
        matching_files = []
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if start_time <= file_time <= end_time:
                    matching_files.append(file_path)
                    
        return sorted(matching_files, key=lambda x: x.stat().st_mtime)
        
    except Exception as e:
        logger.error(f"获取时间范围文件失败: {e}")
        return []


class Timer:
    """简单的计时器类"""
    
    def __init__(self, name: str = "Timer"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        self.end_time = None
        self.elapsed_time = None
        logger.debug(f"{self.name} 开始计时")
        
    def stop(self) -> float:
        """停止计时并返回耗时"""
        if self.start_time is None:
            logger.warning(f"{self.name} 未开始计时")
            return 0.0
            
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        logger.debug(f"{self.name} 计时结束: {format_duration(self.elapsed_time)}")
        return self.elapsed_time
        
    def get_elapsed(self) -> float:
        """获取当前耗时（不停止计时）"""
        if self.start_time is None:
            return 0.0
            
        current_time = time.time()
        return current_time - self.start_time
        
    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        
    def __enter__(self):
        """支持with语句"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.stop()


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.timers = {}
        self.records = []
        
    def start_timer(self, name: str):
        """开始一个命名计时器"""
        if name not in self.timers:
            self.timers[name] = Timer(name)
        self.timers[name].start()
        
    def stop_timer(self, name: str) -> Optional[float]:
        """停止一个命名计时器"""
        if name not in self.timers:
            logger.warning(f"计时器 {name} 不存在")
            return None
            
        elapsed = self.timers[name].stop()
        
        # 记录性能数据
        record = {
            'name': name,
            'elapsed_time': elapsed,
            'timestamp': get_timestamp('iso')
        }
        self.records.append(record)
        
        return elapsed
        
    def get_statistics(self) -> Dict:
        """获取性能统计"""
        if not self.records:
            return {'total_records': 0}
            
        stats = {
            'total_records': len(self.records),
            'operations': {}
        }
        
        # 按操作名称分组统计
        for record in self.records:
            name = record['name']
            if name not in stats['operations']:
                stats['operations'][name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'times': []
                }
                
            op_stats = stats['operations'][name]
            elapsed = record['elapsed_time']
            
            op_stats['count'] += 1
            op_stats['total_time'] += elapsed
            op_stats['min_time'] = min(op_stats['min_time'], elapsed)
            op_stats['max_time'] = max(op_stats['max_time'], elapsed)
            op_stats['times'].append(elapsed)
            
        # 计算平均值
        for name, op_stats in stats['operations'].items():
            op_stats['avg_time'] = op_stats['total_time'] / op_stats['count']
            
        return stats
        
    def clear_records(self):
        """清空记录"""
        self.records.clear()
        
    def save_report(self, filepath: Union[str, Path]) -> bool:
        """保存性能报告"""
        try:
            import json
            
            report = {
                'generated_at': get_timestamp('iso'),
                'statistics': self.get_statistics(),
                'detailed_records': self.records
            }
            
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
            logger.info(f"性能报告已保存: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存性能报告失败: {e}")
            return False


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def monitor_performance(func_name: str):
    """性能监控装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            performance_monitor.start_timer(func_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                performance_monitor.stop_timer(func_name)
        return wrapper
    return decorator
