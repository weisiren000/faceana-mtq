# EmoScan Backend API 🧠

> 基于FastAPI的情感分析后端服务

EmoScan后端提供强大的多API融合情绪分析能力，整合Face++、Gemini和OpenRouter等服务，为前端提供准确可靠的情绪识别结果。

## ✨ 核心特性

- 🔄 **多API融合** - 整合Face++、Gemini、OpenRouter多个API
- 🛡️ **智能容错** - 自动切换备用API，确保服务可用性
- 📊 **标准化输出** - 统一的7种情绪类别，兼容前端显示格式
- ⚡ **异步处理** - 并发调用多个API，提升响应速度
- 🎯 **高精度分析** - 加权融合多个结果，提高识别准确性

## 🚀 快速启动

### 环境要求
- Python 3.8+
- uv包管理器

### 安装依赖
```powershell
# 进入后端目录
Set-Location "D:\codee\faceana-mtq\src\_backend"

# 使用uv安装依赖
uv pip install -r requirements.txt
```

### 配置环境变量
```powershell
# 复制环境变量模板
Copy-Item .env.example .env

# 编辑.env文件，确认API密钥配置
```

### 启动服务器
```powershell
# 方法1: 使用启动脚本
python start_server.py

# 方法2: 直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 API文档

### 基础端点

#### 健康检查
```http
GET /
GET /health
```

#### 情绪分析
```http
POST /api/v1/analyze/image
Content-Type: multipart/form-data

file: [图像文件]
```

**响应格式**:
```json
{
  "success": true,
  "emotion_data": [
    {
      "emotion": "Happy",
      "percentage": 65.4,
      "color": "#00ff88"
    }
  ],
  "analysis_text": ">>> NEURAL NETWORK ANALYSIS COMPLETE <<<\n...",
  "error_message": null
}
```