# 项目架构

## 项目概述

这是一个情感分析系统（Emotion Analysis System），主要用于分析人脸图像和相关数据中的情感表达。系统采用Python作为主要开发语言，前端使用Python Flet框架。

## 技术栈

1. 后端: Python
2. 前端: Python Flet
3. 包管理工具: 
   - uv: 用于替代pip管理Python依赖
   - ~~bun: 用于替代npm~~（已弃用）

## 目录结构

```
faceana-mtq/
│
├── .obsidian/                    # Obsidian配置和插件目录
│   └── plugins/                  # Obsidian插件
│       ├── 3d-graph/             # 3D图表插件
│       ├── advanced-canvas/      # 高级画布插件
│       ├── excel/                # Excel插件
│       ├── obsidian-chartsview-plugin/  # 图表视图插件
│       ├── obsidian-excalidraw-plugin/  # Excalidraw绘图插件
│       ├── obsidian-image-toolkit/      # 图像工具包插件
│       ├── obsidian-latex-suite/        # LaTeX套件插件
│       ├── obsidian-mind-map/           # 思维导图插件
│       └── obsidian-tasks-plugin/       # 任务管理插件
│
├── docs/                         # 项目文档
│   ├── arc.md                    # 项目架构文档
│   ├── api-documents.md          # API文档
│   ├── idea.md                   # 项目想法
│   ├── agent.md                  # 智能体文档
├── obsidian/                     # Obsidian笔记和知识库
│
├── src/                          # 源代码目录
│   ├── config.py                 # 全局配置文件
│   ├── main.py                   # 主控程序，用于启动前后端
│   │
│   ├── _backend/                 # 后端代码
│   │   ├── agent/                # 智能体模块
│   │   │   ├── __init__.py       # 智能体初始化
│   │   │   ├── dsa.py            # 数据情感分析智能体
│   │   │   ├── jsa.py            # 视觉情感分析智能体
│   │   │   ├── pea.py            # 心理情感分析智能体
│   │   │   └── vsa.py            # 视觉情感分析智能体
│   │   │
│   │   ├── api/                  # API接口
│   │   │   ├── __init__.py       # API初始化
│   │   │   ├── anthropic.py      # Anthropic API集成
│   │   │   ├── facepp.py         # Face++ API集成
│   │   │   ├── gemini.py         # Gemini API集成
│   │   │   ├── openai.py         # OpenAI API集成
│   │   │   └── openrouter.py     # OpenRouter API集成
│   │   │
│   │   ├── app/                  # 应用层
│   │   │   ├── main.py           # 应用主入口
│   │   │   └── assets/           # 资源文件
│   │   │       ├── fonts/        # 字体资源
│   │   │       ├── images/       # 图像资源
│   │   │       ├── utils/        # 工具函数
│   │   │       └── views/        # 视图组件
│   │   │
│   │   ├── core/                 # 核心功能模块
│   │   │   ├── __init__.py       # 核心模块初始化
│   │   │   ├── capture.py        # 截图器：检测人脸并截取摄像头图像
│   │   │   ├── cleaner.py        # 清理器：清理摄像机截取的图像避免堆积
│   │   │   ├── splicer.py        # 拼接器：拼接摄像头捕捉到的图像
│   │   │   └── tagger.py         # 标注器：标注图像中人物的五官点
│   │   │
│   │   ├── utils/                # 工具函数
│   │   ├── config.py             # 后端配置
│   │   └── main.py               # 后端主入口
│   │
│   ├── arduino_link/             # Arduino连接模块
│   │   └── __init__.py           # Arduino连接初始化
│   │
│   ├── comfyui_link/             # ComfyUI连接模块
│   │   └── __init__.py           # ComfyUI连接初始化
│   │
│   └── touchdesigner_link/       # TouchDesigner连接模块
│       └── __init__.py           # TouchDesigner连接初始化
│
├── .env                          # 环境变量
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── README-CN.md                  # 中文说明文档
├── README.md                     # 英文说明文档
└── requirements.txt              # Python依赖包列表
```

## 模块功能说明

### 后端核心模块

1. **截图器 (capture.py)**
   - 功能：检测人脸并截取摄像头图像
   - 职责：负责从摄像头获取原始图像并进行人脸检测

2. **清理器 (cleaner.py)**
   - 功能：清理摄像机截取的图像
   - 职责：避免图像在系统中堆积，管理存储空间

3. **拼接器 (splicer.py)**
   - 功能：拼接摄像头捕捉到的图像
   - 职责：将多个图像帧组合或拼接成完整序列

4. **标注器 (tagger.py)**
   - 功能：标注图像中人物的五官点
   - 职责：识别并标记面部特征点，为情感分析提供基础数据

### 智能体模块

1. **数据情感分析智能体 (dsa.py)**
   - 功能：专注于文本数据的情感分析
   - 职责：处理和分析文本内容中的情感表达

2. **视觉情感分析智能体 (jsa.py, vsa.py)**
   - 功能：专注于图像和视觉数据的情感识别
   - 职责：分析图像中的情感表达和视觉线索

3. **心理情感分析智能体 (pea.py)**
   - 功能：基于心理学理论进行深度情感分析
   - 职责：结合心理学模型解读情感数据

### 外部连接模块

1. **Arduino连接模块**
   - 功能：与Arduino硬件设备进行通信和数据交换

2. **ComfyUI连接模块**
   - 功能：与ComfyUI图形界面工具集成

3. **TouchDesigner连接模块**
   - 功能：与TouchDesigner视觉编程环境集成

### API集成

系统集成了多种AI服务API：
- Anthropic
- Face++
- Gemini
- OpenAI
- OpenRouter

这些API为系统提供了强大的AI能力支持，包括图像识别、自然语言处理和情感分析等功能。

## 数据流

1. 摄像头捕获图像 → 截图器处理 → 标注器标记特征点 → 情感分析智能体分析 → 结果展示
2. 需要时可通过拼接器组合图像，并由清理器管理图像存储

## 扩展性

系统设计为模块化架构，可以通过以下方式扩展：
1. 添加新的智能体模块处理不同类型的情感分析
2. 集成更多的外部API和服务
3. 通过Arduino、ComfyUI和TouchDesigner连接模块与外部系统和设备交互