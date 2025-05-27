"""
图像拼接模块
工作原理：
1. 将data/capture中的图片按照时间顺序进行横向拼接
2. 将data/tagger中的图片按照时间顺序进行横向拼接
3. 将上述两个拼接的图像进行纵向拼接存放到data/splicer
"""

import cv2
import logging
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
import re

from ..config import config

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class ImageSplicer:
    """图像拼接类"""

    def __init__(self):
        """初始化图像拼接器"""
        pass

    def get_sorted_images(self, directory: Path, pattern: str = "*") -> List[Path]:
        """
        获取目录中按时间排序的图像文件

        Args:
            directory: 目录路径
            pattern: 文件匹配模式

        Returns:
            List[Path]: 排序后的图像文件路径列表
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(directory.glob(f"{pattern}{ext}"))
            image_files.extend(directory.glob(f"{pattern}{ext.upper()}"))

        # 按文件名中的时间戳排序
        def extract_timestamp(filepath: Path) -> str:
            """从文件名中提取时间戳"""
            filename = filepath.stem
            # 查找时间戳模式 YYYYMMDD_HHMMSS_mmm
            timestamp_match = re.search(r'\d{8}_\d{6}_\d{3}', filename)
            if timestamp_match:
                return timestamp_match.group()
            # 如果没有找到时间戳，使用文件修改时间
            return str(filepath.stat().st_mtime)

        sorted_files = sorted(image_files, key=extract_timestamp)
        logger.info(f"在 {directory} 中找到 {len(sorted_files)} 个图像文件")

        return sorted_files

    def resize_images_to_same_height(self, images: List[np.ndarray]) -> List[np.ndarray]:
        """
        将图像调整为相同高度

        Args:
            images: 图像列表

        Returns:
            List[np.ndarray]: 调整后的图像列表
        """
        if not images:
            return []

        # 找到最小高度
        min_height = min(img.shape[0] for img in images)

        resized_images = []
        for img in images:
            if img.shape[0] != min_height:
                # 计算新的宽度以保持宽高比
                aspect_ratio = img.shape[1] / img.shape[0]
                new_width = int(min_height * aspect_ratio)

                # 调整图像大小
                resized_img = cv2.resize(img, (new_width, min_height))
                resized_images.append(resized_img)
            else:
                resized_images.append(img)

        return resized_images

    def resize_images_to_same_width(self, images: List[np.ndarray]) -> List[np.ndarray]:
        """
        将图像调整为相同宽度

        Args:
            images: 图像列表

        Returns:
            List[np.ndarray]: 调整后的图像列表
        """
        if not images:
            return []

        # 找到最小宽度
        min_width = min(img.shape[1] for img in images)

        resized_images = []
        for img in images:
            if img.shape[1] != min_width:
                # 计算新的高度以保持宽高比
                aspect_ratio = img.shape[0] / img.shape[1]
                new_height = int(min_width * aspect_ratio)

                # 调整图像大小
                resized_img = cv2.resize(img, (min_width, new_height))
                resized_images.append(resized_img)
            else:
                resized_images.append(img)

        return resized_images

    def horizontal_concatenate(self, images: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        水平拼接图像

        Args:
            images: 图像列表

        Returns:
            Optional[np.ndarray]: 拼接后的图像，失败返回None
        """
        if not images:
            logger.warning("没有图像可以拼接")
            return None

        if len(images) == 1:
            return images[0]

        try:
            # 调整图像为相同高度
            resized_images = self.resize_images_to_same_height(images)

            # 水平拼接
            concatenated = np.hstack(resized_images)
            logger.info(f"成功水平拼接 {len(images)} 张图像")

            return concatenated

        except Exception as e:
            logger.error(f"水平拼接失败: {e}")
            return None

    def vertical_concatenate(self, images: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        垂直拼接图像

        Args:
            images: 图像列表

        Returns:
            Optional[np.ndarray]: 拼接后的图像，失败返回None
        """
        if not images:
            logger.warning("没有图像可以拼接")
            return None

        if len(images) == 1:
            return images[0]

        try:
            # 调整图像为相同宽度
            resized_images = self.resize_images_to_same_width(images)

            # 垂直拼接
            concatenated = np.vstack(resized_images)
            logger.info(f"成功垂直拼接 {len(images)} 张图像")

            return concatenated

        except Exception as e:
            logger.error(f"垂直拼接失败: {e}")
            return None

    def load_images_from_paths(self, image_paths: List[Path]) -> List[np.ndarray]:
        """
        从路径列表加载图像

        Args:
            image_paths: 图像路径列表

        Returns:
            List[np.ndarray]: 加载的图像列表
        """
        images = []

        for path in image_paths:
            try:
                image = cv2.imread(str(path))
                if image is not None:
                    images.append(image)
                    logger.debug(f"成功加载图像: {path}")
                else:
                    logger.warning(f"无法加载图像: {path}")
            except Exception as e:
                logger.error(f"加载图像失败 {path}: {e}")

        return images

    def splice_capture_images(self) -> Optional[str]:
        """
        拼接capture目录中的图像

        Returns:
            Optional[str]: 拼接后的图像文件路径，失败返回None
        """
        try:
            # 获取capture目录中的图像文件
            capture_files = self.get_sorted_images(config.CAPTURE_DIR, "capture_*")

            if not capture_files:
                logger.warning("capture目录中没有找到图像文件")
                return None

            # 加载图像
            capture_images = self.load_images_from_paths(capture_files)

            if not capture_images:
                logger.error("无法加载capture图像")
                return None

            # 水平拼接
            spliced_image = self.horizontal_concatenate(capture_images)

            if spliced_image is None:
                logger.error("capture图像拼接失败")
                return None

            # 保存拼接结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spliced_capture_{timestamp}.{config.IMAGE_FORMAT}"
            filepath = config.SPLICER_DIR / filename

            success = cv2.imwrite(
                str(filepath),
                spliced_image,
                [cv2.IMWRITE_JPEG_QUALITY, config.IMAGE_QUALITY]
            )

            if success:
                logger.info(f"capture图像拼接完成: {filepath}")
                return str(filepath)
            else:
                logger.error(f"保存拼接图像失败: {filepath}")
                return None

        except Exception as e:
            logger.error(f"拼接capture图像时发生错误: {e}")
            return None

    def splice_tagger_images(self) -> Optional[str]:
        """
        拼接tagger目录中的图像

        Returns:
            Optional[str]: 拼接后的图像文件路径，失败返回None
        """
        try:
            # 获取tagger目录中的图像文件
            tagger_files = self.get_sorted_images(config.TAGGER_DIR, "tagged_*")

            if not tagger_files:
                logger.warning("tagger目录中没有找到图像文件")
                return None

            # 加载图像
            tagger_images = self.load_images_from_paths(tagger_files)

            if not tagger_images:
                logger.error("无法加载tagger图像")
                return None

            # 水平拼接
            spliced_image = self.horizontal_concatenate(tagger_images)

            if spliced_image is None:
                logger.error("tagger图像拼接失败")
                return None

            # 保存拼接结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spliced_tagger_{timestamp}.{config.IMAGE_FORMAT}"
            filepath = config.SPLICER_DIR / filename

            success = cv2.imwrite(
                str(filepath),
                spliced_image,
                [cv2.IMWRITE_JPEG_QUALITY, config.IMAGE_QUALITY]
            )

            if success:
                logger.info(f"tagger图像拼接完成: {filepath}")
                return str(filepath)
            else:
                logger.error(f"保存拼接图像失败: {filepath}")
                return None

        except Exception as e:
            logger.error(f"拼接tagger图像时发生错误: {e}")
            return None

    def create_final_splice(self, capture_splice_path: str, tagger_splice_path: str) -> Optional[str]:
        """
        创建最终的拼接图像（垂直拼接capture和tagger的拼接结果）

        Args:
            capture_splice_path: capture拼接图像路径
            tagger_splice_path: tagger拼接图像路径

        Returns:
            Optional[str]: 最终拼接图像路径，失败返回None
        """
        try:
            # 加载两个拼接图像
            capture_image = cv2.imread(capture_splice_path)
            tagger_image = cv2.imread(tagger_splice_path)

            if capture_image is None or tagger_image is None:
                logger.error("无法加载拼接图像")
                return None

            # 垂直拼接
            final_image = self.vertical_concatenate([capture_image, tagger_image])

            if final_image is None:
                logger.error("最终拼接失败")
                return None

            # 保存最终拼接结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"final_splice_{timestamp}.{config.IMAGE_FORMAT}"
            filepath = config.SPLICER_DIR / filename

            success = cv2.imwrite(
                str(filepath),
                final_image,
                [cv2.IMWRITE_JPEG_QUALITY, config.IMAGE_QUALITY]
            )

            if success:
                logger.info(f"最终拼接完成: {filepath}")
                return str(filepath)
            else:
                logger.error(f"保存最终拼接图像失败: {filepath}")
                return None

        except Exception as e:
            logger.error(f"创建最终拼接时发生错误: {e}")
            return None

    def process_all_images(self) -> Optional[str]:
        """
        处理所有图像拼接流程

        Returns:
            Optional[str]: 最终拼接图像路径，失败返回None
        """
        logger.info("开始图像拼接流程...")

        # 1. 拼接capture图像
        capture_splice_path = self.splice_capture_images()
        if not capture_splice_path:
            logger.error("capture图像拼接失败，终止流程")
            return None

        # 2. 拼接tagger图像
        tagger_splice_path = self.splice_tagger_images()
        if not tagger_splice_path:
            logger.error("tagger图像拼接失败，终止流程")
            return None

        # 3. 创建最终拼接
        final_splice_path = self.create_final_splice(capture_splice_path, tagger_splice_path)
        if not final_splice_path:
            logger.error("最终拼接失败")
            return None

        logger.info("图像拼接流程完成")
        return final_splice_path

def splice_images() -> Optional[str]:
    """
    便捷函数：执行图像拼接

    Returns:
        Optional[str]: 最终拼接图像路径，失败返回None
    """
    splicer = ImageSplicer()
    return splicer.process_all_images()

if __name__ == "__main__":
    # 测试代码
    result = splice_images()
    print(f"拼接结果: {result}")