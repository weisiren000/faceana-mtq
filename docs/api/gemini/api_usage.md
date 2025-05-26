# Google Gemini API 调用方法

## 基本使用

### 安装依赖

```python
pip install google-generativeai
```

### 基本调用示例

```python
import google.generativeai as genai

# 配置API密钥
genai.configure(api_key="your-api-key")  # 从环境变量获取: os.environ.get("GEMINI_API_KEY")

# 获取可用模型列表
models = genai.list_models()
for model in models:
    if "generateContent" in model.supported_generation_methods:
        print(model.name)

# 选择模型
model = genai.GenerativeModel('gemini-1.5-pro')  # 或其他模型如 'gemini-1.5-flash', 'gemini-pro'

# 文本生成调用
response = model.generate_content("你好，请介绍一下自己。")

# 获取回复内容
print(response.text)
```

## 图像识别与分析

### 调用Vision API

```python
import google.generativeai as genai
import PIL.Image

# 配置API密钥
genai.configure(api_key="your-api-key")

# 选择支持多模态的模型
model = genai.GenerativeModel('gemini-1.5-pro')  # 或 'gemini-pro-vision'

# 方法一：通过URL提供图像（需要使用requests库获取图像）
import requests
from io import BytesIO

url = "https://example.com/image.jpg"
response = requests.get(url)
image = PIL.Image.open(BytesIO(response.content))

result = model.generate_content(["这张图片中有什么?", image])
print(result.text)

# 方法二：从本地文件加载图像
image_path = "path/to/your/image.jpg"
image = PIL.Image.open(image_path)

result = model.generate_content(["这张图片中有什么?", image])
print(result.text)
```

## 情感分析应用

### 图像情感分析

```python
import google.generativeai as genai
import PIL.Image

# 配置API密钥
genai.configure(api_key="your-api-key")

# 选择支持多模态的模型
model = genai.GenerativeModel('gemini-1.5-pro')  # 使用高精度模型获取更好的情感分析结果

def analyze_emotion_in_image(image_path):
    # 加载图像
    image = PIL.Image.open(image_path)
    
    # 构建提示
    prompt = "请分析这张图片中人物的情感状态，包括可能的情绪（如高兴、悲伤、愤怒、惊讶、恐惧、厌恶、中性等），情绪强度，以及你的分析理由。"
    
    # 生成内容
    response = model.generate_content([prompt, image])
    
    return response.text

# 使用示例
result = analyze_emotion_in_image("path/to/face_image.jpg")
print(result)
```

### 文本情感分析

```python
import google.generativeai as genai

# 配置API密钥
genai.configure(api_key="your-api-key")

# 选择文本模型
model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_emotion_in_text(text):
    # 构建提示
    prompt = f"""
    请分析以下文本中表达的情感状态，包括情绪类型、强度和原因：

    {text}
    
    分析要点：
    1. 主要情绪类型
    2. 情绪强度（低、中、高）
    3. 引起这种情绪的可能原因
    4. 其他次要情绪（如果有）
    """
    
    # 生成内容
    response = model.generate_content(prompt)
    
    return response.text

# 使用示例
text_sample = "今天是我生命中最美好的一天，一切都那么完美，我感到无比幸福和感激。"
result = analyze_emotion_in_text(text_sample)
print(result)
```

## 流式输出

```python
import google.generativeai as genai

# 配置API密钥
genai.configure(api_key="your-api-key")

# 选择模型
model = genai.GenerativeModel('gemini-1.5-pro')

# 创建流式响应
response = model.generate_content(
    "请给我写一个短篇故事，主题是人工智能与人类友谊。",
    stream=True
)

# 处理流式响应
for chunk in response:
    print(chunk.text, end="", flush=True)
print()  # 最后打印换行
```

## 多轮对话

```python
import google.generativeai as genai

# 配置API密钥
genai.configure(api_key="your-api-key")

# 创建聊天会话
chat = genai.GenerativeModel('gemini-1.5-pro').start_chat(
    history=[]
)

# 发送第一条消息
response = chat.send_message("你好，我想了解一下人工智能。")
print("AI: " + response.text)

# 发送第二条消息
response = chat.send_message("我想了解机器学习的基本原理。")
print("AI: " + response.text)

# 发送第三条消息
response = chat.send_message("深度学习和机器学习有什么区别？")
print("AI: " + response.text)

# 查看聊天历史
print("\n聊天历史:")
for message in chat.history:
    author = "用户" if message.role == "user" else "AI"
    print(f"{author}: {message.parts[0].text}")
```

## 设置生成参数

```python
import google.generativeai as genai

# 配置API密钥
genai.configure(api_key="your-api-key")

# 选择模型
model = genai.GenerativeModel(
    'gemini-1.5-pro',
    # 设置生成参数
    generation_config={
        'temperature': 0.7,  # 控制创造性 (0.0-1.0)
        'top_p': 0.95,       # 控制输出多样性
        'top_k': 40,         # 从前k个可能的词中选择
        'max_output_tokens': 2048,  # 最大输出长度
        'response_mime_type': 'text/plain',  # 响应MIME类型
    }
)

# 使用设置好参数的模型生成内容
response = model.generate_content("请写一首关于人工智能的诗。")
print(response.text)
```

## 安全设置

```python
import google.generativeai as genai

# 配置API密钥
genai.configure(api_key="your-api-key")

# 自定义安全设置
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# 选择模型并应用安全设置
model = genai.GenerativeModel(
    'gemini-1.5-pro',
    safety_settings=safety_settings
)

# 使用设置好安全参数的模型生成内容
response = model.generate_content("请介绍一下AI的伦理问题。")
print(response.text)
```

## 错误处理

```python
import google.generativeai as genai
from google.api_core import exceptions

# 配置API密钥
genai.configure(api_key="your-api-key")

# 选择模型
model = genai.GenerativeModel('gemini-1.5-pro')

try:
    response = model.generate_content("你好，请回答我的问题。")
    print(response.text)
    
except exceptions.InvalidArgument as e:
    print(f"参数错误: {e}")
    
except exceptions.ResourceExhausted as e:
    print(f"资源耗尽或配额超限: {e}")
    
except exceptions.PermissionDenied as e:
    print(f"权限被拒绝: {e}")
    
except exceptions.ServiceUnavailable as e:
    print(f"服务不可用: {e}")
    
except exceptions.DeadlineExceeded as e:
    print(f"请求超时: {e}")
    
except Exception as e:
    print(f"发生未知错误: {e}")
```

## 环境变量配置

推荐使用环境变量来存储API密钥，而不是硬编码在代码中：

```python
import os
import google.generativeai as genai

# 从环境变量获取API密钥
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 使用客户端...
```

可以使用python-dotenv库从.env文件加载环境变量：

```python
from dotenv import load_dotenv
import os
import google.generativeai as genai

# 加载.env文件中的环境变量
load_dotenv()

# 使用环境变量
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
``` 