# Anthropic Claude API 调用方法

## 基本使用

### 安装依赖

```python
pip install anthropic
```

### 基本调用示例

```python
from anthropic import Anthropic

# 初始化客户端
anthropic = Anthropic(api_key="your-api-key")  # 从环境变量获取: os.environ.get("ANTHROPIC_API_KEY")

# 文本生成调用
message = anthropic.messages.create(
    model="claude-3-opus-20240229",  # 可以选择不同的模型，如 "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
    max_tokens=1000,
    temperature=0.7,
    messages=[
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
)

# 获取回复内容
print(message.content[0].text)
```

## 图像识别与分析

### 调用Vision API

```python
from anthropic import Anthropic
import base64

anthropic = Anthropic(api_key="your-api-key")

# 方法一：通过URL提供图像
message = anthropic.messages.create(
    model="claude-3-opus-20240229",  # Claude 3 系列模型均支持图像输入
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "这张图片中有什么?"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ]
)

# 方法二：通过base64编码提供图像
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

image_path = "path/to/your/image.jpg"
base64_image = encode_image_to_base64(image_path)

message = anthropic.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "这张图片中有什么?"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",  # 指定媒体类型
                        "data": base64_image
                    }
                }
            ]
        }
    ]
)

# 获取回复内容
print(message.content[0].text)
```

## 情感分析应用

### 图像情感分析

```python
from anthropic import Anthropic
import base64

anthropic = Anthropic(api_key="your-api-key")

def analyze_emotion_in_image(image_path):
    # 将图像编码为base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    message = anthropic.messages.create(
        model="claude-3-opus-20240229",  # 使用高精度模型获取更好的情感分析结果
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请分析这张图片中人物的情感状态，包括可能的情绪（如高兴、悲伤、愤怒、惊讶、恐惧、厌恶、中性等），情绪强度，以及你的分析理由。"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    )
    
    return message.content[0].text

# 使用示例
result = analyze_emotion_in_image("path/to/face_image.jpg")
print(result)
```

### 文本情感分析

```python
from anthropic import Anthropic

anthropic = Anthropic(api_key="your-api-key")

def analyze_emotion_in_text(text):
    message = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        system="你是一个专门进行情感分析的AI助手。请详细分析文本中表达的情感。",
        messages=[
            {
                "role": "user",
                "content": f"请分析以下文本中表达的情感状态，包括情绪类型、强度和原因：\n\n{text}"
            }
        ]
    )
    
    return message.content[0].text

# 使用示例
text_sample = "今天是我生命中最美好的一天，一切都那么完美，我感到无比幸福和感激。"
result = analyze_emotion_in_text(text_sample)
print(result)
```

## 流式输出

```python
from anthropic import Anthropic

anthropic = Anthropic(api_key="your-api-key")

# 创建流式响应
with anthropic.messages.stream(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "请给我写一个短篇故事，主题是人工智能与人类友谊。"}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # 实时打印输出
    print()  # 最后打印换行
```

## 多轮对话

```python
from anthropic import Anthropic

anthropic = Anthropic(api_key="your-api-key")

# 创建多轮对话
conversation = [
    {"role": "user", "content": "你好，我想了解一下人工智能。"},
    {"role": "assistant", "content": "你好！人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。它包括机器学习、深度学习、自然语言处理等多个领域。你有什么具体想了解的方面吗？"},
    {"role": "user", "content": "我想了解机器学习的基本原理。"}
]

message = anthropic.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=conversation
)

# 获取回复并添加到对话历史
response = message.content[0].text
conversation.append({"role": "assistant", "content": response})
print(response)

# 继续对话
conversation.append({"role": "user", "content": "谢谢解释，深度学习又是什么？"})

message = anthropic.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=conversation
)

response = message.content[0].text
conversation.append({"role": "assistant", "content": response})
print(response)
```

## 错误处理

```python
from anthropic import Anthropic
from anthropic.types import (
    APIError,
    APIConnectionError,
    APIResponseError,
    APIStatusError,
    APITimeoutError,
    RateLimitError
)

anthropic = Anthropic(api_key="your-api-key")

try:
    message = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": "你好，请回答我的问题。"}
        ]
    )
    print(message.content[0].text)
    
except RateLimitError as e:
    print(f"请求频率超限: {e}")
    # 实现重试逻辑或等待
    
except APIStatusError as e:
    print(f"API状态错误: {e}")
    
except APIConnectionError as e:
    print(f"API连接错误: {e}")
    
except APITimeoutError as e:
    print(f"API超时错误: {e}")
    
except APIResponseError as e:
    print(f"API响应错误: {e}")
    
except APIError as e:
    print(f"API错误: {e}")
    
except Exception as e:
    print(f"发生未知错误: {e}")
```

## 环境变量配置

推荐使用环境变量来存储API密钥，而不是硬编码在代码中：

```python
import os
from anthropic import Anthropic

# 从环境变量获取API密钥
anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 使用客户端...
```

可以使用python-dotenv库从.env文件加载环境变量：

```python
from dotenv import load_dotenv
import os
from anthropic import Anthropic

# 加载.env文件中的环境变量
load_dotenv()

# 使用环境变量
anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
``` 