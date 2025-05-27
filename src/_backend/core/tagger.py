"""
人脸标注模块
工作原理：
1. 读取data/capture中的图片
2. 进行人脸关键点检测和标注
3. 将标注结果保存到data/tagger目录
"""

import cv2
import logging
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import json
from datetime import datetime

from ..config import config

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class FaceTagger:
    """人脸标注类"""

    def __init__(self):
        """初始化人脸标注器"""
        self.face_cascade = None
        self.eye_cascade = None
        self.smile_cascade = None

        # 初始化检测器
        self._init_detectors()

    def _init_detectors(self) -> None:
        """初始化各种检测器"""
        try:
            # 人脸检测器
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)

            # 眼部检测器
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

            # 微笑检测器
            smile_cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
            self.smile_cascade = cv2.CascadeClassifier(smile_cascade_path)

            # 验证检测器是否加载成功
            if (self.face_cascade.empty() or
                self.eye_cascade.empty() or
                self.smile_cascade.empty()):
                raise Exception("检测器加载失败")

            logger.info("人脸检测器初始化成功")

        except Exception as e:
            logger.error(f"检测器初始化失败: {e}")
            raise

    def detect_face_features(self, image: np.ndarray) -> Dict:
        """
        检测人脸特征

        Args:
            image: 输入图像

        Returns:
            Dict: 检测结果字典
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=config.FACE_DETECTION_SCALE_FACTOR,
            minNeighbors=config.FACE_DETECTION_MIN_NEIGHBORS,
            minSize=config.FACE_DETECTION_MIN_SIZE
        )

        results = {
            'faces': [],
            'total_faces': len(faces),
            'image_shape': image.shape
        }

        for (x, y, w, h) in faces:
            face_roi_gray = gray[y:y+h, x:x+w]
            face_roi_color = image[y:y+h, x:x+w]

            # 在人脸区域检测眼部
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray)

            # 在人脸区域检测微笑
            smiles = self.smile_cascade.detectMultiScale(
                face_roi_gray,
                scaleFactor=1.8,
                minNeighbors=20
            )

            face_data = {
                'face_rect': [int(x), int(y), int(w), int(h)],
                'eyes': [[int(ex), int(ey), int(ew), int(eh)] for (ex, ey, ew, eh) in eyes],
                'smiles': [[int(sx), int(sy), int(sw), int(sh)] for (sx, sy, sw, sh) in smiles],
                'eye_count': len(eyes),
                'smile_count': len(smiles)
            }

            results['faces'].append(face_data)

        return results

    def draw_annotations(self, image: np.ndarray, detection_results: Dict) -> np.ndarray:
        """
        在图像上绘制标注

        Args:
            image: 原始图像
            detection_results: 检测结果

        Returns:
            np.ndarray: 标注后的图像
        """
        annotated_image = image.copy()

        for face_data in detection_results['faces']:
            x, y, w, h = face_data['face_rect']

            # 绘制人脸框（绿色）
            cv2.rectangle(annotated_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # 添加人脸标签
            cv2.putText(annotated_image, 'Face', (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # 绘制眼部（蓝色）
            for ex, ey, ew, eh in face_data['eyes']:
                cv2.rectangle(annotated_image, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 2)
                cv2.putText(annotated_image, 'Eye', (x+ex, y+ey-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # 绘制微笑（红色）
            for sx, sy, sw, sh in face_data['smiles']:
                cv2.rectangle(annotated_image, (x+sx, y+sy), (x+sx+sw, y+sy+sh), (0, 0, 255), 2)
                cv2.putText(annotated_image, 'Smile', (x+sx, y+sy-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # 添加统计信息
        info_text = f"Faces: {detection_results['total_faces']}"
        cv2.putText(annotated_image, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return annotated_image

    def process_image(self, image_path: str) -> Optional[Tuple[str, str]]:
        """
        处理单张图像

        Args:
            image_path: 图像文件路径

        Returns:
            Optional[Tuple[str, str]]: (标注图像路径, 检测结果JSON路径)
        """
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"无法读取图像: {image_path}")
                return None

            # 检测人脸特征
            detection_results = self.detect_face_features(image)

            # 绘制标注
            annotated_image = self.draw_annotations(image, detection_results)

            # 生成输出文件名
            input_filename = Path(image_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 保存标注图像
            annotated_filename = f"tagged_{input_filename}_{timestamp}.{config.IMAGE_FORMAT}"
            annotated_path = config.TAGGER_DIR / annotated_filename

            success = cv2.imwrite(
                str(annotated_path),
                annotated_image,
                [cv2.IMWRITE_JPEG_QUALITY, config.IMAGE_QUALITY]
            )

            if not success:
                logger.error(f"保存标注图像失败: {annotated_path}")
                return None

            # 保存检测结果JSON
            json_filename = f"detection_{input_filename}_{timestamp}.json"
            json_path = config.TAGGER_DIR / json_filename

            detection_results['source_image'] = image_path
            detection_results['annotated_image'] = str(annotated_path)
            detection_results['timestamp'] = timestamp

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(detection_results, f, ensure_ascii=False, indent=2)

            logger.info(f"图像处理完成: {annotated_path}")
            return str(annotated_path), str(json_path)

        except Exception as e:
            logger.error(f"处理图像时发生错误: {e}")
            return None

    def process_capture_directory(self) -> List[Tuple[str, str]]:
        """
        处理capture目录中的所有图像

        Returns:
            List[Tuple[str, str]]: [(标注图像路径, JSON路径), ...]
        """
        results = []

        # 获取capture目录中的所有图像文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(config.CAPTURE_DIR.glob(f"*{ext}"))
            image_files.extend(config.CAPTURE_DIR.glob(f"*{ext.upper()}"))

        if not image_files:
            logger.warning("capture目录中没有找到图像文件")
            return results

        logger.info(f"找到 {len(image_files)} 个图像文件，开始处理...")

        for image_file in sorted(image_files):
            result = self.process_image(str(image_file))
            if result:
                results.append(result)

        logger.info(f"图像处理完成，成功处理: {len(results)} 个文件")
        return results

def tag_face_images() -> List[Tuple[str, str]]:
    """
    便捷函数：标注人脸图像

    Returns:
        List[Tuple[str, str]]: [(标注图像路径, JSON路径), ...]
    """
    tagger = FaceTagger()
    return tagger.process_capture_directory()

if __name__ == "__main__":
    # 测试代码
    results = tag_face_images()
    print(f"标注结果: {results}")