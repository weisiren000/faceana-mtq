"""
文件清理模块
工作原理：
1. 清理data/capture目录中的临时图像文件
2. 清理data/tagger目录中的标注文件
3. 可选择性清理data/splicer目录中的拼接文件
4. 记录清理操作日志
"""

import os
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from ..config import config

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class FileCleaner:
    """文件清理类"""

    def __init__(self):
        """初始化文件清理器"""
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.errors = []

    def get_files_in_directory(self, directory: Path, pattern: str = "*") -> List[Path]:
        """
        获取目录中的文件列表

        Args:
            directory: 目录路径
            pattern: 文件匹配模式

        Returns:
            List[Path]: 文件路径列表
        """
        if not directory.exists():
            logger.warning(f"目录不存在: {directory}")
            return []

        files = []
        try:
            files = list(directory.glob(pattern))
            logger.info(f"在 {directory} 中找到 {len(files)} 个文件")
        except Exception as e:
            logger.error(f"获取文件列表失败 {directory}: {e}")
            self.errors.append(f"获取文件列表失败 {directory}: {e}")

        return files

    def remove_file(self, file_path: Path) -> bool:
        """
        删除单个文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 删除是否成功
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.cleaned_files.append(str(file_path))
                logger.debug(f"删除文件: {file_path}")
                return True
            else:
                logger.warning(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            error_msg = f"删除文件失败 {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False

    def remove_files(self, file_paths: List[Path]) -> int:
        """
        批量删除文件

        Args:
            file_paths: 文件路径列表

        Returns:
            int: 成功删除的文件数量
        """
        success_count = 0

        for file_path in file_paths:
            if self.remove_file(file_path):
                success_count += 1

        logger.info(f"批量删除完成，成功删除 {success_count}/{len(file_paths)} 个文件")
        return success_count

    def clean_capture_directory(self) -> int:
        """
        清理capture目录

        Returns:
            int: 清理的文件数量
        """
        logger.info("开始清理capture目录...")

        # 获取capture目录中的所有图像文件
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
        all_files = []

        for ext in image_extensions:
            files = self.get_files_in_directory(config.CAPTURE_DIR, ext)
            all_files.extend(files)

        if not all_files:
            logger.info("capture目录中没有文件需要清理")
            return 0

        # 删除文件
        cleaned_count = self.remove_files(all_files)
        logger.info(f"capture目录清理完成，删除了 {cleaned_count} 个文件")

        return cleaned_count

    def clean_tagger_directory(self) -> int:
        """
        清理tagger目录

        Returns:
            int: 清理的文件数量
        """
        logger.info("开始清理tagger目录...")

        # 获取tagger目录中的所有文件（图像和JSON）
        patterns = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.json',
                   '*.JPG', '*.JPEG', '*.PNG', '*.BMP', '*.JSON']
        all_files = []

        for pattern in patterns:
            files = self.get_files_in_directory(config.TAGGER_DIR, pattern)
            all_files.extend(files)

        if not all_files:
            logger.info("tagger目录中没有文件需要清理")
            return 0

        # 删除文件
        cleaned_count = self.remove_files(all_files)
        logger.info(f"tagger目录清理完成，删除了 {cleaned_count} 个文件")

        return cleaned_count

    def clean_splicer_directory(self, keep_final: bool = True) -> int:
        """
        清理splicer目录

        Args:
            keep_final: 是否保留最终拼接文件

        Returns:
            int: 清理的文件数量
        """
        logger.info("开始清理splicer目录...")

        # 获取splicer目录中的所有图像文件
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
        all_files = []

        for ext in image_extensions:
            files = self.get_files_in_directory(config.SPLICER_DIR, ext)
            all_files.extend(files)

        if not all_files:
            logger.info("splicer目录中没有文件需要清理")
            return 0

        # 如果需要保留最终拼接文件，过滤掉final_splice文件
        files_to_clean = []
        if keep_final:
            for file_path in all_files:
                if not file_path.name.startswith('final_splice_'):
                    files_to_clean.append(file_path)
                else:
                    logger.info(f"保留最终拼接文件: {file_path}")
        else:
            files_to_clean = all_files

        if not files_to_clean:
            logger.info("splicer目录中没有需要清理的文件")
            return 0

        # 删除文件
        cleaned_count = self.remove_files(files_to_clean)
        logger.info(f"splicer目录清理完成，删除了 {cleaned_count} 个文件")

        return cleaned_count

    def clean_temp_directory(self) -> int:
        """
        清理temp目录

        Returns:
            int: 清理的文件数量
        """
        logger.info("开始清理temp目录...")

        # 获取temp目录中的所有文件
        all_files = self.get_files_in_directory(config.TEMP_DIR, "*")

        if not all_files:
            logger.info("temp目录中没有文件需要清理")
            return 0

        # 删除文件
        cleaned_count = self.remove_files(all_files)
        logger.info(f"temp目录清理完成，删除了 {cleaned_count} 个文件")

        return cleaned_count

    def clean_all_directories(self, keep_splicer_final: bool = True) -> Dict[str, int]:
        """
        清理所有目录

        Args:
            keep_splicer_final: 是否保留splicer目录中的最终拼接文件

        Returns:
            Dict[str, int]: 各目录清理的文件数量统计
        """
        logger.info("开始全面清理...")

        results = {
            'capture': 0,
            'tagger': 0,
            'splicer': 0,
            'temp': 0,
            'total': 0
        }

        # 清理各个目录
        results['capture'] = self.clean_capture_directory()
        results['tagger'] = self.clean_tagger_directory()
        results['splicer'] = self.clean_splicer_directory(keep_final=keep_splicer_final)
        results['temp'] = self.clean_temp_directory()

        # 计算总数
        results['total'] = sum([results['capture'], results['tagger'],
                               results['splicer'], results['temp']])

        logger.info(f"全面清理完成，总共删除了 {results['total']} 个文件")
        logger.info(f"清理统计: {results}")

        return results

    def get_cleanup_summary(self) -> Dict:
        """
        获取清理操作摘要

        Returns:
            Dict: 清理操作摘要
        """
        return {
            'cleaned_files_count': len(self.cleaned_files),
            'cleaned_files': self.cleaned_files,
            'errors_count': len(self.errors),
            'errors': self.errors,
            'timestamp': datetime.now().isoformat()
        }

    def save_cleanup_log(self, log_file: Optional[str] = None) -> str:
        """
        保存清理日志

        Args:
            log_file: 日志文件路径，默认自动生成

        Returns:
            str: 日志文件路径
        """
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = str(config.LOGS_DIR / f"cleanup_log_{timestamp}.json")

        summary = self.get_cleanup_summary()

        try:
            import json
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            logger.info(f"清理日志已保存: {log_file}")
            return log_file

        except Exception as e:
            logger.error(f"保存清理日志失败: {e}")
            return ""

def clean_all_files(keep_splicer_final: bool = True) -> Dict[str, int]:
    """
    便捷函数：清理所有文件

    Args:
        keep_splicer_final: 是否保留splicer目录中的最终拼接文件

    Returns:
        Dict[str, int]: 清理统计结果
    """
    cleaner = FileCleaner()
    results = cleaner.clean_all_directories(keep_splicer_final)

    # 保存清理日志
    cleaner.save_cleanup_log()

    return results

def clean_capture_files() -> int:
    """
    便捷函数：仅清理capture文件

    Returns:
        int: 清理的文件数量
    """
    cleaner = FileCleaner()
    return cleaner.clean_capture_directory()

def clean_tagger_files() -> int:
    """
    便捷函数：仅清理tagger文件

    Returns:
        int: 清理的文件数量
    """
    cleaner = FileCleaner()
    return cleaner.clean_tagger_directory()

if __name__ == "__main__":
    # 测试代码
    results = clean_all_files()
    print(f"清理结果: {results}")