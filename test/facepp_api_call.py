import os
import requests
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

API_KEY = os.getenv("FACEPP_API_KEY", "wvv-yzcDhvSx-vIs7tl3DZ2vJnEp-NCr")
API_SECRET = os.getenv("FACEPP_API_SECRET", "Q82rf7NWaheJEQ6Az5_aJoN1MlpfDipT")
IMAGE_PATH = "test/image/test_img.png"

from PIL import Image
from io import BytesIO

def compress_image(input_path, max_size_kb=700, max_width=1024):
    img = Image.open(input_path)
    # 限制宽度
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    # 如果是RGBA或P模式，需转为RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # 循环压缩直到小于max_size_kb
    quality = 90
    while True:
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality < 30:
            buffer.seek(0)
            return buffer
        quality -= 10

url = "https://api-cn.faceplusplus.com/facepp/v3/detect"
img_buffer = compress_image(IMAGE_PATH)
files = {"image_file": ("image.jpg", img_buffer, "image/jpeg")}
data = {
    "api_key": API_KEY,
    "api_secret": API_SECRET,
    "return_attributes": "age,gender,smiling,emotion,ethnicity,beauty"
}

try:
    response = requests.post(url, data=data, files=files)
    response.raise_for_status()
    print(response.json())
except Exception as e:
    print("调用Face++失败：", e)