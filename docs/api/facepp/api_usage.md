# Face++ API 调用方法

## 基本使用

### 安装依赖

```python
pip install requests
```

Face++ API不需要专门的SDK，只需使用标准的HTTP请求库即可。

### 基本调用示例

```python
import requests
import json

# API密钥和密钥
api_key = "your_api_key"
api_secret = "your_api_secret"

# 基础URL
base_url = "https://api-cn.faceplusplus.com/facepp/v3"

# 人脸检测API调用
def detect_face(image_path=None, image_url=None):
    endpoint = f"{base_url}/detect"
    
    # 准备请求参数
    params = {
        'api_key': api_key,
        'api_secret': api_secret,
        'return_landmark': 1,  # 返回人脸关键点
        'return_attributes': 'gender,age,smiling,emotion,beauty'  # 返回人脸属性
    }
    
    files = {}
    
    # 通过本地文件或URL发送图像
    if image_path:
        files = {'image_file': open(image_path, 'rb')}
    elif image_url:
        params['image_url'] = image_url
    
    # 发送请求
    response = requests.post(endpoint, params=params, files=files)
    
    # 如果使用了本地文件，记得关闭文件
    if image_path:
        files['image_file'].close()
    
    # 返回结果
    return response.json()

# 使用示例
# 通过本地图片
result = detect_face(image_path="path/to/face.jpg")
print(json.dumps(result, indent=2))

# 通过图片URL
result = detect_face(image_url="https://example.com/face.jpg")
print(json.dumps(result, indent=2))
```

## 人脸分析功能

### 人脸检测与分析

```python
import requests
import json

def face_detect_and_analyze(image_path=None, image_url=None):
    """
    检测图像中的人脸并分析属性
    
    参数:
    - image_path: 本地图像路径
    - image_url: 图像URL
    
    返回:
    - 包含人脸信息和属性的JSON对象
    """
    endpoint = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    
    # 请求参数
    params = {
        'api_key': "your_api_key",
        'api_secret': "your_api_secret",
        'return_landmark': 2,  # 2表示返回106个人脸关键点
        'return_attributes': 'gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus'
    }
    
    files = {}
    
    # 通过本地文件或URL发送图像
    if image_path:
        files = {'image_file': open(image_path, 'rb')}
    elif image_url:
        params['image_url'] = image_url
    
    # 发送请求
    response = requests.post(endpoint, params=params, files=files)
    
    # 如果使用了本地文件，记得关闭文件
    if image_path:
        files['image_file'].close()
    
    # 返回结果
    return response.json()

# 使用示例
result = face_detect_and_analyze(image_path="path/to/face.jpg")

# 访问检测到的人脸信息
if 'faces' in result and result['faces']:
    for i, face in enumerate(result['faces']):
        print(f"人脸 #{i+1}:")
        
        # 获取人脸矩形框位置
        face_rectangle = face['face_rectangle']
        print(f"  位置: 左上角({face_rectangle['left']}, {face_rectangle['top']}), 宽{face_rectangle['width']}, 高{face_rectangle['height']}")
        
        # 获取情绪分析结果
        emotion = face['attributes']['emotion']
        print("  情绪分析:")
        print(f"    - 愤怒: {emotion['anger']}%")
        print(f"    - 厌恶: {emotion['disgust']}%")
        print(f"    - 恐惧: {emotion['fear']}%")
        print(f"    - 高兴: {emotion['happiness']}%")
        print(f"    - 中性: {emotion['neutral']}%")
        print(f"    - 悲伤: {emotion['sadness']}%")
        print(f"    - 惊讶: {emotion['surprise']}%")
        
        # 获取年龄和性别
        print(f"  年龄: {face['attributes']['age']['value']}岁")
        print(f"  性别: {face['attributes']['gender']['value']}, 置信度: {face['attributes']['gender']['confidence']}%")
        
        # 获取微笑程度
        print(f"  微笑程度: {face['attributes']['smile']['value']}, 阈值: {face['attributes']['smile']['threshold']}")
```

### 人脸比对

```python
import requests
import json

def face_compare(face1_path=None, face1_url=None, face2_path=None, face2_url=None):
    """
    比较两张人脸图像的相似度
    
    参数:
    - face1_path/face1_url: 第一张人脸的本地路径或URL
    - face2_path/face2_url: 第二张人脸的本地路径或URL
    
    返回:
    - 包含相似度信息的JSON对象
    """
    endpoint = "https://api-cn.faceplusplus.com/facepp/v3/compare"
    
    # 请求参数
    params = {
        'api_key': "your_api_key",
        'api_secret': "your_api_secret"
    }
    
    files = {}
    
    # 设置第一张人脸
    if face1_path:
        files['image_file1'] = open(face1_path, 'rb')
    elif face1_url:
        params['image_url1'] = face1_url
    
    # 设置第二张人脸
    if face2_path:
        files['image_file2'] = open(face2_path, 'rb')
    elif face2_url:
        params['image_url2'] = face2_url
    
    # 发送请求
    response = requests.post(endpoint, params=params, files=files)
    
    # 关闭已打开的文件
    for key in list(files.keys()):
        files[key].close()
    
    # 返回结果
    return response.json()

# 使用示例
result = face_compare(
    face1_path="path/to/face1.jpg", 
    face2_path="path/to/face2.jpg"
)

# 解析结果
if 'confidence' in result:
    confidence = result['confidence']
    print(f"人脸相似度置信度: {confidence}")
    
    # 置信度阈值建议
    if confidence > 80:
        print("很可能是同一个人")
    elif confidence > 60:
        print("可能是同一个人")
    else:
        print("可能不是同一个人")
```

## 情感分析

### 人脸情绪识别

```python
import requests
import json
import matplotlib.pyplot as plt
import numpy as np

def analyze_emotion(image_path=None, image_url=None):
    """
    分析人脸图像中的情绪表达
    
    参数:
    - image_path: 本地图像路径
    - image_url: 图像URL
    
    返回:
    - 包含情绪分析的JSON对象
    """
    endpoint = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    
    # 请求参数
    params = {
        'api_key': "your_api_key",
        'api_secret': "your_api_secret",
        'return_attributes': 'emotion'  # 只返回情绪属性
    }
    
    files = {}
    
    # 通过本地文件或URL发送图像
    if image_path:
        files = {'image_file': open(image_path, 'rb')}
    elif image_url:
        params['image_url'] = image_url
    
    # 发送请求
    response = requests.post(endpoint, params=params, files=files)
    
    # 如果使用了本地文件，记得关闭文件
    if image_path:
        files['image_file'].close()
    
    # 返回结果
    return response.json()

def visualize_emotion(emotion_data):
    """
    可视化情绪分析结果
    
    参数:
    - emotion_data: 情绪数据字典
    """
    # 提取情绪标签和数值
    emotions = list(emotion_data.keys())
    values = list(emotion_data.values())
    
    # 创建条形图
    plt.figure(figsize=(10, 6))
    bars = plt.bar(emotions, values, color='skyblue')
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height}%', ha='center', va='bottom')
    
    # 设置图表标题和标签
    plt.title('人脸情绪分析结果')
    plt.xlabel('情绪类别')
    plt.ylabel('置信度(%)')
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 显示图表
    plt.show()

# 使用示例
result = analyze_emotion(image_path="path/to/face.jpg")

# 处理和可视化结果
if 'faces' in result and result['faces']:
    # 获取第一个检测到的人脸的情绪数据
    emotion_data = result['faces'][0]['attributes']['emotion']
    print("情绪分析结果:")
    for emotion, score in emotion_data.items():
        print(f"  - {emotion}: {score}%")
    
    # 找出主要情绪
    main_emotion = max(emotion_data, key=emotion_data.get)
    print(f"\n主要情绪: {main_emotion}, 置信度: {emotion_data[main_emotion]}%")
    
    # 可视化情绪分析结果
    visualize_emotion(emotion_data)
else:
    print("未检测到人脸或处理出错")
```

## 错误处理

```python
import requests
import json
import time

def face_api_request_with_retry(endpoint, params, files=None, max_retries=3, retry_delay=2):
    """
    发送Face++ API请求，并支持重试机制
    
    参数:
    - endpoint: API端点URL
    - params: 请求参数
    - files: 文件对象(如果有)
    - max_retries: 最大重试次数
    - retry_delay: 重试延迟(秒)
    
    返回:
    - API响应的JSON对象
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 发送请求
            response = requests.post(endpoint, params=params, files=files)
            
            # 检查响应状态码
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP错误: {response.status_code}, 响应: {response.text}")
                
                # 如果是速率限制(429)，等待更长时间
                if response.status_code == 429:
                    retry_delay = retry_delay * 2
            
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
        
        # 增加重试计数并等待
        retry_count += 1
        if retry_count < max_retries:
            print(f"第{retry_count}次重试, 等待{retry_delay}秒...")
            time.sleep(retry_delay)
    
    return {"error": "超过最大重试次数，请求失败"}

# 使用示例
endpoint = "https://api-cn.faceplusplus.com/facepp/v3/detect"
params = {
    'api_key': "your_api_key",
    'api_secret': "your_api_secret",
    'return_attributes': 'emotion'
}

files = {'image_file': open("path/to/face.jpg", 'rb')}

try:
    result = face_api_request_with_retry(endpoint, params, files)
    print(json.dumps(result, indent=2))
finally:
    # 确保文件被关闭
    files['image_file'].close()
```

## 环境变量配置

推荐使用环境变量来存储API密钥，而不是硬编码在代码中：

```python
import os
import requests
import json
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量获取API密钥
api_key = os.environ.get("FACEPP_API_KEY")
api_secret = os.environ.get("FACEPP_API_SECRET")

# 检查是否成功获取密钥
if not api_key or not api_secret:
    raise ValueError("未找到Face++ API密钥。请检查环境变量是否正确设置。")

# 使用API密钥进行调用
def detect_face(image_path):
    endpoint = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    
    params = {
        'api_key': api_key,
        'api_secret': api_secret,
        'return_attributes': 'emotion'
    }
    
    with open(image_path, 'rb') as image_file:
        files = {'image_file': image_file}
        response = requests.post(endpoint, params=params, files=files)
    
    return response.json()

# 使用示例
result = detect_face("path/to/face.jpg")
print(json.dumps(result, indent=2))
``` 