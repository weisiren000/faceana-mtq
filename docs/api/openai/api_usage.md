# OpenAI API 调用方法

## 基本使用

### 安装依赖

```python
pip install openai
```

### 基本调用示例

```python
from openai import OpenAI

# 初始化客户端
client = OpenAI(api_key="your-api-key")  # 从环境变量获取: os.environ.get("OPENAI_API_KEY")

# 文本生成调用
response = client.chat.completions.create(
    model="gpt-4",  # 或其他模型如 "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
)

# 获取回复内容
print(response.choices[0].message.content)
```

## 图像识别与分析

### 调用Vision API

```python
from openai import OpenAI
import base64

client = OpenAI(api_key="your-api-key")

# 方法一：通过URL提供图像
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图片中有什么?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg",
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

# 方法二：通过base64编码提供图像
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

image_path = "path/to/your/image.jpg"
base64_image = encode_image(image_path)

response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图片中有什么?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

# 获取回复内容
print(response.choices[0].message.content)
```

## 情感分析应用

### 图像情感分析

```python
from openai import OpenAI
import base64

client = OpenAI(api_key="your-api-key")

def analyze_emotion_in_image(image_path):
    # 将图像编码为base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system", 
                "content": "你是一个专门进行情感分析的AI助手。请详细分析图像中人物的情感状态。"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请分析这张图片中人物的情感状态，包括可能的情绪（如高兴、悲伤、愤怒、惊讶、恐惧、厌恶、中性等），情绪强度，以及你的分析理由。"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=500,
    )
    
    return response.choices[0].message.content

# 使用示例
result = analyze_emotion_in_image("path/to/face_image.jpg")
print(result)
```

### 文本情感分析

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def analyze_emotion_in_text(text):
    response = client.chat.completions.create(
        model="gpt-4",  # 或使用 "gpt-3.5-turbo"
        messages=[
            {
                "role": "system", 
                "content": "你是一个专门进行情感分析的AI助手。请详细分析文本中表达的情感。"
            },
            {
                "role": "user",
                "content": f"请分析以下文本中表达的情感状态，包括情绪类型、强度和原因：\n\n{text}"
            }
        ],
        max_tokens=300,
    )
    
    return response.choices[0].message.content

# 使用示例
text_sample = "今天是我生命中最美好的一天，一切都那么完美，我感到无比幸福和感激。"
result = analyze_emotion_in_text(text_sample)
print(result)
```

## 异步调用方法

```python
import asyncio
from openai import AsyncOpenAI

async def generate_text_async():
    client = AsyncOpenAI(api_key="your-api-key")
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "你好，请给我介绍一下Python的异步编程。"}
        ]
    )
    
    return response.choices[0].message.content

# 运行异步函数
async def main():
    result = await generate_text_async()
    print(result)

asyncio.run(main())
```

## 错误处理

```python
from openai import OpenAI
from openai.types.error import APIError, RateLimitError

client = OpenAI(api_key="your-api-key")

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "你好，请回答我的问题。"}
        ]
    )
    print(response.choices[0].message.content)
    
except RateLimitError as e:
    print(f"请求频率超限: {e}")
    # 实现重试逻辑或等待
    
except APIError as e:
    print(f"API错误: {e}")
    
except Exception as e:
    print(f"发生未知错误: {e}")
```

## 环境变量配置

推荐使用环境变量来存储API密钥，而不是硬编码在代码中：

```python
import os
from openai import OpenAI

# 从环境变量获取API密钥
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 使用客户端...
```

可以使用python-dotenv库从.env文件加载环境变量：

```python
from dotenv import load_dotenv
import os
from openai import OpenAI

# 加载.env文件中的环境变量
load_dotenv()

# 使用环境变量
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
``` 