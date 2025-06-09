# ComfyUI集成使用说明

## 概述

本项目已集成ComfyUI，可以根据情绪分析结果自动生成对应的艺术图像。系统会根据检测到的主导情绪选择相应的工作流文件进行图像生成。

## 功能特性

- 🎨 **情绪驱动生成**: 根据7种标准情绪自动选择工作流
- 🔄 **异步处理**: 非阻塞的图像生成流程
- 📊 **状态监控**: 实时监控ComfyUI服务状态和队列
- 🛡️ **容错机制**: ComfyUI不可用时不影响核心功能
- ⚙️ **灵活配置**: 支持自定义工作流和参数

## 环境要求

### ComfyUI服务
- ComfyUI需要单独安装和运行
- 默认端口：8188
- 确保ComfyUI的API服务已启用

### 工作流文件
在 `src/_backend/workflows/` 目录下放置以下工作流文件：
- `happy.json` - 快乐情绪工作流
- `sad.json` - 悲伤情绪工作流
- `angry.json` - 愤怒情绪工作流
- `surprised.json` - 惊讶情绪工作流
- `neutral.json` - 中性情绪工作流
- `disgusted.json` - 厌恶情绪工作流
- `fearful.json` - 恐惧情绪工作流
- `test.json` - 默认工作流（必需）

## API使用

### 1. 检查ComfyUI状态
```bash
GET /api/v1/generation/status
```

响应示例：
```json
{
  "available": true,
  "queue_running": 0,
  "queue_pending": 1,
  "system_stats": {...}
}
```

### 2. 列出可用工作流
```bash
GET /api/v1/generation/workflows
```

### 3. 根据情绪生成图像
```bash
POST /api/v1/generation/generate
Content-Type: application/json

{
  "emotion": "happy",
  "seed": 12345,
  "workflow_name": "custom_happy.json"
}
```

### 4. 基于情绪分析结果生成图像
```bash
POST /api/v1/generation/generate-from-analysis
Content-Type: application/json

{
  "emotion_data": [
    {"emotion": "Happy", "percentage": 75.5, "color": "#00ff88"},
    {"emotion": "Sad", "percentage": 15.2, "color": "#0099ff"}
  ],
  "seed": 12345
}
```

### 5. 一键分析和生成
```bash
POST /api/v1/analyze-and-generate
Content-Type: multipart/form-data

file: [图像文件]
generate_image: true
```

## 工作流配置

### 工作流文件格式
工作流文件是标准的ComfyUI JSON格式，系统会自动修改以下参数：

1. **随机种子**: 在KSampler节点中设置
2. **文件名前缀**: 在SaveImage节点中设置为 `emoscan_{emotion}_{timestamp}`

### 示例工作流结构
```json
{
  "3": {
    "inputs": {
      "seed": 422542716721075,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler"
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": ["8", 0]
    },
    "class_type": "SaveImage"
  }
}
```

## 测试和调试

### 运行集成测试
```bash
cd src/_backend
python test_comfyui_integration.py
```

测试内容包括：
- ComfyUI服务连接状态
- 工作流文件加载
- 情绪映射功能
- 图像生成流程

### 常见问题

#### 1. ComfyUI连接失败
- 确保ComfyUI正在运行（默认端口8188）
- 检查防火墙设置
- 验证ComfyUI API是否启用

#### 2. 工作流加载失败
- 检查工作流文件是否存在
- 验证JSON格式是否正确
- 确保文件编码为UTF-8

#### 3. 图像生成超时
- 检查ComfyUI队列状态
- 增加超时时间配置
- 验证工作流的复杂度

## 配置选项

在 `app/models/comfyui.py` 中可以修改以下配置：

```python
COMFYUI_CONFIG = {
    "base_url": "http://localhost:8188",  # ComfyUI服务地址
    "timeout": 10,                        # 请求超时时间
    "max_wait_time": 300,                 # 最大等待时间
    "check_interval": 3,                  # 状态检查间隔
}
```

## 性能优化建议

1. **工作流优化**: 使用较少步数和较小分辨率的工作流以提高生成速度
2. **队列管理**: 监控ComfyUI队列状态，避免过多并发请求
3. **缓存策略**: 考虑对相同参数的生成结果进行缓存
4. **异步处理**: 利用异步特性避免阻塞主线程

## 扩展功能

### 自定义参数支持
可以通过 `custom_params` 参数传递自定义的工作流参数：

```json
{
  "emotion": "happy",
  "custom_params": {
    "6.inputs.text": "beautiful landscape, happy mood",
    "3.inputs.steps": 25
  }
}
```

参数路径格式：`节点ID.inputs.参数名`

### 多模型支持
通过不同的工作流文件可以支持多种AI模型和风格：
- 写实风格工作流
- 动漫风格工作流
- 抽象艺术工作流
- 等等

## 注意事项

1. **资源消耗**: 图像生成会消耗大量GPU资源，请合理安排使用
2. **存储空间**: 生成的图像会保存在ComfyUI的输出目录中
3. **版本兼容**: 确保ComfyUI版本与工作流文件兼容
4. **安全考虑**: 在生产环境中请配置适当的访问控制
