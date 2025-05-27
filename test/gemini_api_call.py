import os
import requests
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取 API 密钥和模型名称
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("MODEL")

# 确保 API 密钥和模型名称已设置
if not GEMINI_API_KEY or not MODEL:
    print("请设置 GEMINI_API_KEY 和 MODEL 环境变量")
    exit()

# Gemini API 的基本 URL
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL + ":generateContent"

# 请求头
headers = {
    "Content-Type": "application/json"
}

# 请求参数
params = {
    "key": GEMINI_API_KEY
}

import base64

# 图像文件路径
IMAGE_PATH = "test/image/test_img.png"

# 读取图像文件并进行 Base64 编码
with open(IMAGE_PATH, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

# 请求体
data = {
    "contents": [{
        "parts": [
            {
                "text": "这张图片是什么？情绪是什么？简答，比如：开心"
            },
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": image_data
                }
            }
        ]
    }]
}

try:
    # 发送 POST 请求
    response = requests.post(BASE_URL, headers=headers, params=params, json=data)

    # 检查响应状态码
    response.raise_for_status()

    # 打印响应
    print(response.json())

except requests.exceptions.RequestException as e:
    print(f"发生错误：{e}")