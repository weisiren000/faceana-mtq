"""
图像捕获模块
工作原理：
1. 打开摄像头
2. 实时检测人脸
3. 检测到人脸后连续截图4秒5张图片
4. 保存到data/capture目录
"""

import cv2
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

from ..config import config

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class FaceCapture:
    """人脸捕获类"""

    def __init__(self, camera_index: int = None):
        """
        初始化人脸捕获器

        Args:
            camera_index: 摄像头索引，默认使用配置中的值
        """
        self.camera_index = camera_index or config.CAMERA_INDEX
        self.cap = None
        self.face_cascade = None
        self.is_capturing = False

        # 初始化人脸检测器
        self._init_face_detector()

    def _init_face_detector(self) -> None:
        """初始化人脸检测器"""
        try:
            # 使用OpenCV的Haar级联分类器
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

            if self.face_cascade.empty():
                raise Exception("无法加载人脸检测器")

            logger.info("人脸检测器初始化成功")

        except Exception as e:
            logger.error(f"人脸检测器初始化失败: {e}")
            raise

    def _init_camera(self) -> bool:
        """
        初始化摄像头

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.camera_index}")
                return False

            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            logger.info(f"摄像头 {self.camera_index} 初始化成功")
            return True

        except Exception as e:
            logger.error(f"摄像头初始化失败: {e}")
            return False

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        检测图像中的人脸

        Args:
            frame: 输入图像帧

        Returns:
            List[Tuple]: 人脸位置列表 [(x, y, w, h), ...]
        """
        try:
            # 转换为灰度图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 检测人脸
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=config.FACE_DETECTION_SCALE_FACTOR,
                minNeighbors=config.FACE_DETECTION_MIN_NEIGHBORS,
                minSize=config.FACE_DETECTION_MIN_SIZE
            )

            return faces.tolist() if len(faces) > 0 else []

        except Exception as e:
            logger.error(f"人脸检测失败: {e}")
            return []

    def save_image(self, frame: np.ndarray, timestamp: str) -> Optional[str]:
        """
        保存图像到capture目录

        Args:
            frame: 图像帧
            timestamp: 时间戳

        Returns:
            Optional[str]: 保存的文件路径，失败返回None
        """
        try:
            filename = f"capture_{timestamp}.{config.IMAGE_FORMAT}"
            filepath = config.CAPTURE_DIR / filename

            # 保存图像
            success = cv2.imwrite(
                str(filepath),
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, config.IMAGE_QUALITY]
            )

            if success:
                logger.info(f"图像保存成功: {filepath}")
                return str(filepath)
            else:
                logger.error(f"图像保存失败: {filepath}")
                return None

        except Exception as e:
            logger.error(f"保存图像时发生错误: {e}")
            return None

    def capture_sequence(self) -> List[str]:
        """
        捕获图像序列（4秒5张图）

        Returns:
            List[str]: 保存的图像文件路径列表
        """
        if not self.cap or not self.cap.isOpened():
            logger.error("摄像头未初始化")
            return []

        captured_files = []
        start_time = time.time()

        logger.info("开始捕获图像序列...")

        try:
            for i in range(config.CAPTURE_COUNT):
                ret, frame = self.cap.read()

                if not ret:
                    logger.error("无法读取摄像头帧")
                    break

                # 生成时间戳
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

                # 保存图像
                filepath = self.save_image(frame, timestamp)
                if filepath:
                    captured_files.append(filepath)

                # 等待间隔时间
                if i < config.CAPTURE_COUNT - 1:
                    time.sleep(config.CAPTURE_INTERVAL)

            end_time = time.time()
            duration = end_time - start_time

            logger.info(f"图像序列捕获完成，耗时: {duration:.2f}秒，成功捕获: {len(captured_files)}张")

        except Exception as e:
            logger.error(f"捕获图像序列时发生错误: {e}")

        return captured_files

    def start_monitoring(self) -> List[str]:
        """
        开始监控并捕获人脸图像

        Returns:
            List[str]: 捕获的图像文件路径列表
        """
        if not self._init_camera():
            return []

        logger.info("开始人脸监控...")
        captured_files = []

        try:
            while True:
                ret, frame = self.cap.read()

                if not ret:
                    logger.error("无法读取摄像头帧")
                    break

                # 检测人脸
                faces = self.detect_faces(frame)

                if faces:
                    logger.info(f"检测到 {len(faces)} 个人脸，开始捕获序列...")

                    # 捕获图像序列
                    captured_files = self.capture_sequence()
                    break

                # 显示预览窗口（可选）
                # cv2.imshow('Face Detection', frame)

                # 按ESC键退出
                if cv2.waitKey(1) & 0xFF == 27:
                    logger.info("用户取消监控")
                    break

        except KeyboardInterrupt:
            logger.info("监控被用户中断")
        except Exception as e:
            logger.error(f"监控过程中发生错误: {e}")
        finally:
            self.release()

        return captured_files

    def release(self) -> None:
        """释放资源"""
        try:
            if self.cap:
                self.cap.release()
                logger.info("摄像头资源已释放")

            cv2.destroyAllWindows()

        except Exception as e:
            logger.error(f"释放资源时发生错误: {e}")

def capture_face_images() -> List[str]:
    """
    便捷函数：捕获人脸图像

    Returns:
        List[str]: 捕获的图像文件路径列表
    """
    capture = FaceCapture()
    return capture.start_monitoring()

if __name__ == "__main__":
    # 测试代码
    captured_files = capture_face_images()
    print(f"捕获的图像文件: {captured_files}")
