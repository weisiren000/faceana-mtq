"""
ComfyUI配置文件
包含ComfyUI相关的配置参数
"""

# ComfyUI连接配置
COMFYUI_API_URL = "http://localhost:8000"
COMFYUI_WS_URL = "ws://localhost:8000/ws"

# 默认生成参数
DEFAULT_MODEL = "dreamshaper_8.safetensors"
DEFAULT_SAMPLER = "euler_ancestral"
DEFAULT_STEPS = 20
DEFAULT_CFG = 7.0
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512

# 情绪参数映射
EMOTION_PARAMS = {
    "happy": {
        "cfg": 6.5,
        "sampler": "euler_a",
        "steps": 20
    },
    "sad": {
        "cfg": 7.5,
        "sampler": "ddim",
        "steps": 25
    },
    "angry": {
        "cfg": 8.0,
        "sampler": "dpm++_2m",
        "steps": 30
    },
    "surprised": {
        "cfg": 7.0,
        "sampler": "euler",
        "steps": 20
    },
    "neutral": {
        "cfg": 7.0,
        "sampler": "ddpm",
        "steps": 20
    },
    "disgusted": {
        "cfg": 7.5,
        "sampler": "dpm2",
        "steps": 25
    },
    "fearful": {
        "cfg": 8.0,
        "sampler": "dpm_sde",
        "steps": 30
    }
}

# 情绪提示词模板
EMOTION_TEMPLATES = {
    "happy": [
        "a joyful scene with bright colors and sunshine",
        "people celebrating with smiles and laughter",
        "vibrant landscape with flowers and blue sky"
    ],
    "sad": [
        "a melancholic scene with rain and gray colors",
        "lonely figure walking in empty streets",
        "abandoned place with somber atmosphere"
    ],
    "angry": [
        "a dramatic scene with intense red colors",
        "stormy weather with lightning and dark clouds",
        "powerful waves crashing against rocks"
    ],
    "surprised": [
        "a scene with unexpected elements and bright contrasts",
        "person with wide eyes looking at something amazing",
        "magical moment with sparkling lights"
    ],
    "neutral": [
        "a balanced scene with natural colors",
        "calm atmosphere with gentle lighting",
        "everyday scene with normal activities"
    ],
    "disgusted": [
        "a scene with unsettling elements",
        "sickly green tones and strange textures",
        "distorted shapes and uncomfortable atmosphere"
    ],
    "fearful": [
        "a dark scene with shadows and fog",
        "mysterious elements lurking in darkness",
        "abandoned haunted building at night"
    ]
} 