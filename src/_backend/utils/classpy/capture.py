"""
图像处理工具类
提供高级图像处理和分析功能
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Union
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from ...config import config

# 配置日志
logger = logging.getLogger(__name__)


class ImageProcessor:
    """图像处理工具类"""

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

    def detect_faces_advanced(self, image: np.ndarray,
                            min_size: Tuple[int, int] = (30, 30),
                            scale_factor: float = 1.1,
                            min_neighbors: int = 5) -> List[Dict]:
        """
        高级人脸检测

        Args:
            image: 输入图像
            min_size: 最小人脸尺寸
            scale_factor: 缩放因子
            min_neighbors: 最小邻居数

        Returns:
            List[Dict]: 检测结果列表，包含位置和置信度信息
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            results = []
            for i, (x, y, w, h) in enumerate(faces):
                # 计算人脸区域
                face_roi = gray[y:y+h, x:x+w]

                # 检测眼部
                eyes = self.eye_cascade.detectMultiScale(face_roi)

                # 检测微笑
                smiles = self.smile_cascade.detectMultiScale(face_roi)

                # 计算质量分数
                quality_score = self._calculate_face_quality(face_roi)

                result = {
                    'id': i,
                    'bbox': (x, y, w, h),
                    'center': (x + w//2, y + h//2),
                    'area': w * h,
                    'aspect_ratio': w / h,
                    'eyes_count': len(eyes),
                    'smiles_count': len(smiles),
                    'quality_score': quality_score,
                    'eyes': eyes.tolist() if len(eyes) > 0 else [],
                    'smiles': smiles.tolist() if len(smiles) > 0 else []
                }
                results.append(result)

            # 按质量分数排序
            results.sort(key=lambda x: x['quality_score'], reverse=True)

            return results

        except Exception as e:
            logger.error(f"高级人脸检测失败: {e}")
            return []

    def _calculate_face_quality(self, face_roi: np.ndarray) -> float:
        """
        计算人脸质量分数

        Args:
            face_roi: 人脸区域图像

        Returns:
            float: 质量分数 (0-1)
        """
        try:
            # 计算清晰度（拉普拉斯方差）
            laplacian_var = cv2.Laplacian(face_roi, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000.0, 1.0)

            # 计算亮度均匀性
            mean_brightness = np.mean(face_roi)
            brightness_score = 1.0 - abs(mean_brightness - 128) / 128.0

            # 计算对比度
            contrast = np.std(face_roi)
            contrast_score = min(contrast / 64.0, 1.0)

            # 综合质量分数
            quality_score = (sharpness_score * 0.5 +
                           brightness_score * 0.3 +
                           contrast_score * 0.2)

            return max(0.0, min(1.0, quality_score))

        except Exception as e:
            logger.error(f"计算人脸质量失败: {e}")
            return 0.0

    def enhance_image(self, image: np.ndarray,
                     brightness: float = 0.0,
                     contrast: float = 1.0,
                     gamma: float = 1.0) -> np.ndarray:
        """
        图像增强

        Args:
            image: 输入图像
            brightness: 亮度调整 (-100 到 100)
            contrast: 对比度调整 (0.5 到 3.0)
            gamma: 伽马校正 (0.5 到 2.0)

        Returns:
            np.ndarray: 增强后的图像
        """
        try:
            enhanced = image.astype(np.float32)

            # 亮度调整
            enhanced = enhanced + brightness

            # 对比度调整
            enhanced = enhanced * contrast

            # 伽马校正
            if gamma != 1.0:
                enhanced = enhanced / 255.0
                enhanced = np.power(enhanced, gamma)
                enhanced = enhanced * 255.0

            # 限制像素值范围
            enhanced = np.clip(enhanced, 0, 255)

            return enhanced.astype(np.uint8)

        except Exception as e:
            logger.error(f"图像增强失败: {e}")
            return image

    def add_watermark(self, image: np.ndarray,
                     text: str = "FaceAna-MTQ",
                     position: str = "bottom-right",
                     font_scale: float = 0.7,
                     color: Tuple[int, int, int] = (255, 255, 255),
                     thickness: int = 2) -> np.ndarray:
        """
        添加水印

        Args:
            image: 输入图像
            text: 水印文本
            position: 位置 ("top-left", "top-right", "bottom-left", "bottom-right")
            font_scale: 字体大小
            color: 文字颜色 (B, G, R)
            thickness: 线条粗细

        Returns:
            np.ndarray: 添加水印后的图像
        """
        try:
            result = image.copy()
            height, width = image.shape[:2]

            # 获取文字尺寸
            font = cv2.FONT_HERSHEY_SIMPLEX
            (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

            # 计算位置
            margin = 10
            positions = {
                "top-left": (margin, text_height + margin),
                "top-right": (width - text_width - margin, text_height + margin),
                "bottom-left": (margin, height - margin),
                "bottom-right": (width - text_width - margin, height - margin)
            }

            pos = positions.get(position, positions["bottom-right"])

            # 添加半透明背景
            overlay = result.copy()
            cv2.rectangle(overlay,
                         (pos[0] - 5, pos[1] - text_height - 5),
                         (pos[0] + text_width + 5, pos[1] + 5),
                         (0, 0, 0), -1)
            result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)

            # 添加文字
            cv2.putText(result, text, pos, font, font_scale, color, thickness)

            return result

        except Exception as e:
            logger.error(f"添加水印失败: {e}")
            return image

    def create_collage(self, images: List[np.ndarray],
                      grid_size: Optional[Tuple[int, int]] = None,
                      spacing: int = 10,
                      background_color: Tuple[int, int, int] = (255, 255, 255)) -> Optional[np.ndarray]:
        """
        创建图像拼贴

        Args:
            images: 图像列表
            grid_size: 网格大小 (rows, cols)，None则自动计算
            spacing: 图像间距
            background_color: 背景颜色

        Returns:
            Optional[np.ndarray]: 拼贴图像，失败返回None
        """
        try:
            if not images:
                return None

            # 自动计算网格大小
            if grid_size is None:
                num_images = len(images)
                cols = int(np.ceil(np.sqrt(num_images)))
                rows = int(np.ceil(num_images / cols))
                grid_size = (rows, cols)

            rows, cols = grid_size

            # 统一图像尺寸
            target_height = max(img.shape[0] for img in images)
            target_width = max(img.shape[1] for img in images)

            resized_images = []
            for img in images:
                resized = cv2.resize(img, (target_width, target_height))
                resized_images.append(resized)

            # 计算拼贴图像尺寸
            collage_width = cols * target_width + (cols - 1) * spacing
            collage_height = rows * target_height + (rows - 1) * spacing

            # 创建背景
            collage = np.full((collage_height, collage_width, 3),
                            background_color, dtype=np.uint8)

            # 放置图像
            for i, img in enumerate(resized_images):
                if i >= rows * cols:
                    break

                row = i // cols
                col = i % cols

                y_start = row * (target_height + spacing)
                x_start = col * (target_width + spacing)
                y_end = y_start + target_height
                x_end = x_start + target_width

                collage[y_start:y_end, x_start:x_end] = img

            return collage

        except Exception as e:
            logger.error(f"创建拼贴失败: {e}")
            return None