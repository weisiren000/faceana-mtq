import os
from openai import OpenAI
from dotenv import load_dotenv
import base64
from PIL import Image
from io import BytesIO

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemma-3-27b-it:free"  # 支持图像识别的模型

def compress_image(input_path, max_size_kb=700, max_width=1024):
    img = Image.open(input_path)
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    quality = 90
    while True:
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality < 30:
            buffer.seek(0)
            return buffer
        quality -= 10

def vision_with_openrouter(image_path, prompt="用简短的自然语言描述这张图片"):
    if not API_KEY:
        raise ValueError("请在.env文件中设置OPENROUTER_API_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )
    img_buffer = compress_image(image_path)
    img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
            }
        ],
        extra_headers={
            "HTTP-Referer": "https://your-app-url.com",
            "X-Title": "OpenRouter Vision Example"
        }
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    try:
        vision_result = vision_with_openrouter("test/image/test_img.png")
        print("图片识别返回：", vision_result)
    except Exception as e:
        print("图片识别调用失败：", e)