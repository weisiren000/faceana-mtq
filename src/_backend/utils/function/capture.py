"""
图像捕获工具函数
提供简化的图像捕获接口和便捷函数
"""

import cv2
import logging
from typing import List, Optional, Tuple, Dict
from pathlib import Path
from datetime import datetime

from ...config import config
from ...core.capture import capture_face_images, FaceCapture

# 配置日志
logger = logging.getLogger(__name__)


def quick_capture(num_images: int = 5, interval: float = 0.8) -> List[str]:
    """
    快速图像捕获

    Args:
        num_images: 捕获图像数量，默认5张
        interval: 捕获间隔，默认0.8秒

    Returns:
        List[str]: 捕获的图像文件路径列表
    """
    try:
        return capture_face_images(num_images=num_images, interval=interval)
    except Exception as e:
        logger.error(f"快速捕获失败: {e}")
        return []


def capture_single_image(save_path: Optional[str] = None) -> Optional[str]:
    """
    捕获单张图像

    Args:
        save_path: 保存路径，如果为None则使用默认路径

    Returns:
        Optional[str]: 图像文件路径，失败返回None
    """
    try:
        capturer = FaceCapture()

        # 初始化摄像头
        if not capturer.initialize_camera():
            return None

        # 检测人脸并捕获
        frame = capturer.capture_frame()
        if frame is None:
            return None

        faces = capturer.detect_faces(frame)
        if not faces:
            logger.warning("未检测到人脸")
            return None

        # 保存图像
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = str(config.CAPTURE_DIR / f"single_{timestamp}.jpg")

        cv2.imwrite(save_path, frame)
        logger.info(f"单张图像已保存: {save_path}")

        return save_path

    except Exception as e:
        logger.error(f"单张图像捕获失败: {e}")
        return None
    finally:
        if 'capturer' in locals():
            capturer.cleanup()


def test_camera() -> bool:
    """
    测试摄像头是否可用

    Returns:
        bool: 摄像头是否可用
    """
    try:
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        if not cap.isOpened():
            return False

        ret, frame = cap.read()
        success = ret and frame is not None

        cap.release()
        cv2.destroyAllWindows()

        return success

    except Exception as e:
        logger.error(f"摄像头测试失败: {e}")
        return False


def get_camera_info() -> Dict:
    """
    获取摄像头信息

    Returns:
        Dict: 摄像头信息字典
    """
    info = {
        'available': False,
        'index': config.CAMERA_INDEX,
        'width': None,
        'height': None,
        'fps': None
    }

    try:
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        if cap.isOpened():
            info['available'] = True
            info['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            info['fps'] = cap.get(cv2.CAP_PROP_FPS)

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        logger.error(f"获取摄像头信息失败: {e}")

    return info


def batch_capture_with_delay(batches: int = 3, images_per_batch: int = 5,
                           batch_delay: float = 2.0) -> List[List[str]]:
    """
    分批次捕获图像

    Args:
        batches: 批次数量
        images_per_batch: 每批次图像数量
        batch_delay: 批次间延迟时间（秒）

    Returns:
        List[List[str]]: 每批次的图像文件路径列表
    """
    results = []

    for batch_idx in range(batches):
        logger.info(f"开始第 {batch_idx + 1}/{batches} 批次捕获")

        batch_images = quick_capture(images_per_batch)
        results.append(batch_images)

        if batch_idx < batches - 1:  # 不是最后一批
            logger.info(f"等待 {batch_delay} 秒后开始下一批次")
            import time
            time.sleep(batch_delay)

    return results


def capture_with_face_validation(min_face_size: int = 50,
                               max_attempts: int = 10) -> List[str]:
    """
    带人脸验证的图像捕获

    Args:
        min_face_size: 最小人脸尺寸
        max_attempts: 最大尝试次数

    Returns:
        List[str]: 有效的图像文件路径列表
    """
    valid_images = []
    attempts = 0

    capturer = FaceCapture()

    try:
        if not capturer.initialize_camera():
            return []

        while len(valid_images) < 5 and attempts < max_attempts:
            attempts += 1

            frame = capturer.capture_frame()
            if frame is None:
                continue

            faces = capturer.detect_faces(frame)

            # 验证人脸大小
            valid_faces = [face for face in faces
                          if face[2] >= min_face_size and face[3] >= min_face_size]

            if valid_faces:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"validated_{timestamp}.jpg"
                filepath = str(config.CAPTURE_DIR / filename)

                cv2.imwrite(filepath, frame)
                valid_images.append(filepath)
                logger.info(f"捕获有效图像 {len(valid_images)}/5: {filename}")

            import time
            time.sleep(0.5)  # 短暂延迟

    except Exception as e:
        logger.error(f"带验证的捕获失败: {e}")
    finally:
        capturer.cleanup()

    return valid_images