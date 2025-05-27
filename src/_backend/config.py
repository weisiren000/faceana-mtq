"""
Backend配置文件
管理所有API密钥、系统配置参数和数据路径
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent

    # 数据目录配置
    DATA_DIR = PROJECT_ROOT / "data"
    CAPTURE_DIR = DATA_DIR / "capture"
    TAGGER_DIR = DATA_DIR / "tagger"
    SPLICER_DIR = DATA_DIR / "splicer"
    CLEANER_DIR = DATA_DIR / "cleaner"
    TEMP_DIR = DATA_DIR / "temp"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Face++ API配置
    FACEPP_API_KEY = "wvv-yzcDhvSx-vIs7tl3DZ2vJnEp-NCr"
    FACEPP_API_SECRET = "Q82rf7NWaheJEQ6Az5_aJoN1MlpfDipT"
    FACEPP_API_URL = "https://api-cn.faceplusplus.com/facepp/v3"

    # OpenRouter API配置
    OPENROUTER_API_KEY = "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"
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODELS = [
        "qwen/qwen3-235b-a22b:free",
        "google/gemma-3-27b-it:free",
        "microsoft/phi-4-reasoning-plus:free",
        "moonshotai/kimi-vl-a3b-thinking:free",
        "qwen/qwen2.5-vl-32b-instruct:free"
    ]

    # Gemini API配置
    GEMINI_API_KEY = "AIzaSyDliXeDpoK1vTj-4wWPHkSP5Akaf-wMYPs"
    GEMINI_MODELS = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-lite-001",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash-preview-05-20",
        "gemma-3-27b-it",
        "gemma-3n-e4b-it"
    ]

    # OpenAI API配置（暂未配置）
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "NONE")

    # Anthropic API配置（暂未配置）
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "NONE")

    # 摄像头配置
    CAMERA_INDEX = 0  # 默认摄像头索引
    CAPTURE_INTERVAL = 0.8  # 4秒5张图，间隔0.8秒
    CAPTURE_COUNT = 5  # 捕获图片数量
    CAPTURE_DURATION = 4  # 捕获持续时间（秒）

    # 图像处理配置
    IMAGE_FORMAT = "jpg"
    IMAGE_QUALITY = 95
    FACE_DETECTION_SCALE_FACTOR = 1.1
    FACE_DETECTION_MIN_NEIGHBORS = 5
    FACE_DETECTION_MIN_SIZE = (30, 30)

    # 智能体配置
    DSA_CONFIDENCE_THRESHOLD = 0.7  # DSA智能体置信度阈值
    VSA_CONFIDENCE_THRESHOLD = 0.6  # VSA智能体置信度阈值
    JSA_WEIGHT_DSA = 0.4  # JSA中DSA权重
    JSA_WEIGHT_VSA = 0.6  # JSA中VSA权重

    # 系统配置
    MAX_RETRY_ATTEMPTS = 3  # API调用最大重试次数
    REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
    LOG_LEVEL = "INFO"  # 日志级别

    @classmethod
    def ensure_directories(cls) -> None:
        """确保所有必要的目录存在"""
        directories = [
            cls.DATA_DIR,
            cls.CAPTURE_DIR,
            cls.TAGGER_DIR,
            cls.SPLICER_DIR,
            cls.CLEANER_DIR,
            cls.TEMP_DIR,
            cls.LOGS_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_api_config(cls, api_name: str) -> Dict[str, Any]:
        """获取指定API的配置信息"""
        api_configs = {
            "facepp": {
                "api_key": cls.FACEPP_API_KEY,
                "api_secret": cls.FACEPP_API_SECRET,
                "api_url": cls.FACEPP_API_URL
            },
            "openrouter": {
                "api_key": cls.OPENROUTER_API_KEY,
                "api_url": cls.OPENROUTER_API_URL,
                "models": cls.OPENROUTER_MODELS
            },
            "gemini": {
                "api_key": cls.GEMINI_API_KEY,
                "models": cls.GEMINI_MODELS
            },
            "openai": {
                "api_key": cls.OPENAI_API_KEY
            },
            "anthropic": {
                "api_key": cls.ANTHROPIC_API_KEY
            }
        }

        return api_configs.get(api_name, {})

    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否有效"""
        required_keys = [
            cls.FACEPP_API_KEY,
            cls.FACEPP_API_SECRET,
            cls.OPENROUTER_API_KEY,
            cls.GEMINI_API_KEY
        ]

        for key in required_keys:
            if not key or key == "NONE":
                return False

        return True

# 创建配置实例
config = Config()

# 确保目录存在
config.ensure_directories()
