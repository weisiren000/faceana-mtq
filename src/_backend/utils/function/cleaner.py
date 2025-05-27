"""
文件清理工具函数
提供简化的文件清理接口和批量操作功能
"""

import os
import shutil
import logging
from typing import List, Dict, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta

from ...config import config
from ...core.cleaner import clean_all_files, clean_capture_files, clean_tagger_files

# 配置日志
logger = logging.getLogger(__name__)


def quick_clean(keep_final: bool = True) -> Dict[str, int]:
    """
    快速清理所有临时文件

    Args:
        keep_final: 是否保留最终拼接文件

    Returns:
        Dict[str, int]: 清理统计结果
    """
    try:
        return clean_all_files(keep_splicer_final=keep_final)
    except Exception as e:
        logger.error(f"快速清理失败: {e}")
        return {'total': 0, 'error': str(e)}


def clean_by_age(hours: int = 24, directories: Optional[List[str]] = None) -> Dict[str, int]:
    """
    按文件年龄清理文件

    Args:
        hours: 文件年龄阈值（小时）
        directories: 要清理的目录列表，None表示所有目录

    Returns:
        Dict[str, int]: 清理统计结果
    """
    if directories is None:
        directories = ['capture', 'tagger', 'temp']

    cutoff_time = datetime.now() - timedelta(hours=hours)
    results = {}
    total_cleaned = 0

    dir_mapping = {
        'capture': config.CAPTURE_DIR,
        'tagger': config.TAGGER_DIR,
        'splicer': config.SPLICER_DIR,
        'temp': config.TEMP_DIR
    }

    for dir_name in directories:
        if dir_name not in dir_mapping:
            continue

        directory = dir_mapping[dir_name]
        cleaned_count = 0

        try:
            if directory.exists():
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        # 检查文件修改时间
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"删除过期文件: {file_path}")

        except Exception as e:
            logger.error(f"清理目录 {dir_name} 失败: {e}")

        results[dir_name] = cleaned_count
        total_cleaned += cleaned_count

    results['total'] = total_cleaned
    logger.info(f"按年龄清理完成，删除了 {total_cleaned} 个超过 {hours} 小时的文件")

    return results


def clean_by_pattern(pattern: str, directories: Optional[List[str]] = None) -> Dict[str, int]:
    """
    按文件名模式清理文件

    Args:
        pattern: 文件名模式（支持通配符）
        directories: 要清理的目录列表

    Returns:
        Dict[str, int]: 清理统计结果
    """
    if directories is None:
        directories = ['capture', 'tagger', 'temp']

    results = {}
    total_cleaned = 0

    dir_mapping = {
        'capture': config.CAPTURE_DIR,
        'tagger': config.TAGGER_DIR,
        'splicer': config.SPLICER_DIR,
        'temp': config.TEMP_DIR
    }

    for dir_name in directories:
        if dir_name not in dir_mapping:
            continue

        directory = dir_mapping[dir_name]
        cleaned_count = 0

        try:
            if directory.exists():
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"删除匹配文件: {file_path}")

        except Exception as e:
            logger.error(f"按模式清理目录 {dir_name} 失败: {e}")

        results[dir_name] = cleaned_count
        total_cleaned += cleaned_count

    results['total'] = total_cleaned
    logger.info(f"按模式清理完成，删除了 {total_cleaned} 个匹配 '{pattern}' 的文件")

    return results


def get_directory_size(directory: Union[str, Path]) -> Dict[str, Union[int, str]]:
    """
    获取目录大小信息

    Args:
        directory: 目录路径

    Returns:
        Dict: 包含文件数量和总大小的信息
    """
    directory = Path(directory)

    if not directory.exists():
        return {'files': 0, 'size_bytes': 0, 'size_mb': 0.0, 'error': 'Directory not found'}

    try:
        total_size = 0
        file_count = 0

        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1

        size_mb = total_size / (1024 * 1024)

        return {
            'files': file_count,
            'size_bytes': total_size,
            'size_mb': round(size_mb, 2)
        }

    except Exception as e:
        logger.error(f"获取目录大小失败: {e}")
        return {'files': 0, 'size_bytes': 0, 'size_mb': 0.0, 'error': str(e)}


def get_all_directories_info() -> Dict[str, Dict]:
    """
    获取所有数据目录的信息

    Returns:
        Dict: 所有目录的信息统计
    """
    directories = {
        'capture': config.CAPTURE_DIR,
        'tagger': config.TAGGER_DIR,
        'splicer': config.SPLICER_DIR,
        'temp': config.TEMP_DIR,
        'logs': config.LOGS_DIR
    }

    info = {}

    for name, path in directories.items():
        info[name] = get_directory_size(path)
        info[name]['path'] = str(path)
        info[name]['exists'] = path.exists()

    return info


def backup_directory(source_dir: Union[str, Path], backup_name: Optional[str] = None) -> Optional[str]:
    """
    备份目录

    Args:
        source_dir: 源目录路径
        backup_name: 备份名称，None则使用时间戳

    Returns:
        Optional[str]: 备份文件路径，失败返回None
    """
    source_dir = Path(source_dir)

    if not source_dir.exists():
        logger.error(f"源目录不存在: {source_dir}")
        return None

    try:
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_dir.name}_backup_{timestamp}"

        backup_path = config.TEMP_DIR / f"{backup_name}.zip"

        # 确保备份目录存在
        config.TEMP_DIR.mkdir(parents=True, exist_ok=True)

        # 创建zip备份
        shutil.make_archive(str(backup_path.with_suffix('')), 'zip', source_dir)

        logger.info(f"目录备份完成: {backup_path}")
        return str(backup_path)

    except Exception as e:
        logger.error(f"备份目录失败: {e}")
        return None


def restore_from_backup(backup_path: Union[str, Path], target_dir: Union[str, Path]) -> bool:
    """
    从备份恢复目录

    Args:
        backup_path: 备份文件路径
        target_dir: 目标目录路径

    Returns:
        bool: 恢复是否成功
    """
    backup_path = Path(backup_path)
    target_dir = Path(target_dir)

    if not backup_path.exists():
        logger.error(f"备份文件不存在: {backup_path}")
        return False

    try:
        # 如果目标目录存在，先备份
        if target_dir.exists():
            temp_backup = backup_directory(target_dir, f"temp_backup_{int(datetime.now().timestamp())}")
            if temp_backup:
                logger.info(f"已创建临时备份: {temp_backup}")

        # 清空目标目录
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # 解压备份
        shutil.unpack_archive(backup_path, target_dir)

        logger.info(f"从备份恢复完成: {target_dir}")
        return True

    except Exception as e:
        logger.error(f"从备份恢复失败: {e}")
        return False


def clean_empty_directories() -> int:
    """
    清理空目录

    Returns:
        int: 清理的空目录数量
    """
    directories_to_check = [
        config.CAPTURE_DIR,
        config.TAGGER_DIR,
        config.SPLICER_DIR,
        config.TEMP_DIR
    ]

    cleaned_count = 0

    for directory in directories_to_check:
        try:
            if directory.exists():
                for subdir in directory.rglob('*'):
                    if subdir.is_dir() and not any(subdir.iterdir()):
                        subdir.rmdir()
                        cleaned_count += 1
                        logger.debug(f"删除空目录: {subdir}")

        except Exception as e:
            logger.error(f"清理空目录失败: {e}")

    logger.info(f"清理了 {cleaned_count} 个空目录")
    return cleaned_count