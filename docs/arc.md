# FaceAna-MTQ 项目架构文档

## 项目概述

**项目名称**: FaceAna-MTQ (Face Analysis - Multi-Technology Queue)
**项目类型**: 基于多AI技术栈的情感分析系统
**核心功能**: 通过摄像头实时捕获人脸图像，利用多种AI API进行情感分析，并支持与外部创意工具集成

## 技术栈

### 后端技术
- **主语言**: Python
- **包管理**: uv (替代pip)
- **架构模式**: 模块化微服务架构

### 前端技术
- **框架**: Python Flet
- **交互方式**: 桌面应用程序

### AI服务集成
- **Face++**: 人脸检测与分析
- **OpenAI**: GPT系列模型
- **Anthropic**: Claude系列模型
- **Google Gemini**: 多模态AI模型
- **OpenRouter**: AI模型路由服务

## 项目目录结构

```
faceana-mtq/
├── docs/                           # 项目文档
│   ├── api/                        # API文档
│   │   ├── anthropic/              # Anthropic API相关
│   │   ├── facepp/                 # Face++ API相关
│   │   ├── gemini/                 # Gemini API相关
│   │   └── openai/                 # OpenAI API相关
│   ├── vision-api/                 # 视觉API技术文档
│   │   ├── anthropic-vision-api.md
│   │   ├── face-detection-tech.md
│   │   ├── gemini-vision-api.md
│   │   └── openai-vision-api.md
│   ├── agent.md                    # 智能体文档
│   ├── api-documents.md            # API密钥配置
│   ├── arc.md                      # 项目架构文档(本文件)
│   ├── idea.md                     # 项目创意文档
│   └── init.md                     # 初始化文档
├── obsidian/                       # Obsidian笔记
│   └── 程序执行流程.canvas         # 程序流程图
├── rules/                          # 项目规则
│   └── first_principles.md         # 第一性原理思考框架
├── src/                            # 源代码目录
│   ├── _backend/                   # 后端核心模块
│   │   ├── api/                    # API集成模块
│   │   │   ├── anthropic.py        # Anthropic API封装
│   │   │   ├── facepp.py          # Face++ API封装
│   │   │   ├── gemini.py          # Gemini API封装
│   │   │   ├── openai.py          # OpenAI API封装
│   │   │   └── openrouter.py      # OpenRouter API封装
│   │   ├── app/                    # 前端应用
│   │   │   ├── assets/            # 静态资源
│   │   │   │   ├── fonts/         # 字体文件
│   │   │   │   ├── images/        # 图片资源
│   │   │   │   ├── utils/         # 工具组件
│   │   │   │   └── views/         # 视图组件
│   │   │   └── main.py            # 前端主程序
│   │   ├── core/                   # 核心功能模块
│   │   │   ├── capture.py         # 图像捕获器
│   │   │   ├── cleaner.py         # 图像清理器
│   │   │   ├── splicer.py         # 图像拼接器
│   │   │   └── tagger.py          # 人脸标注器
│   │   ├── robot/                  # AI智能体模块
│   │   │   ├── dsa.py             # 数据情感分析智能体
│   │   │   ├── jsa.py             # 情感裁定者智能体

│   │   │   └── vsa.py             # 视觉情感分析智能体
│   │   ├── test/                   # 测试模块
│   │   ├── utils/                  # 工具模块
│   │   │   ├── class/             # 工具类
│   │   │   ├── function/          # 工具函数
│   │   │   ├── model.py           # 模型定义
│   │   │   └── prompt.py          # 提示词模板
│   │   ├── config.py              # 后端配置
│   │   └── main.py                # 后端主程序

│   ├── comfyui_link/              # ComfyUI集成模块
│   ├── touchdesigner_link/        # TouchDesigner集成模块
│   ├── config.py                  # 全局配置
│   └── main.py                    # 项目主入口
├── requirements.txt               # Python依赖
├── README.md                      # 项目说明(英文)
└── README-CN.md                   # 项目说明(中文)
```

## 核心模块详解

### 1. 图像处理流水线 (Core Pipeline)

#### Capture (图像捕获器)
- **功能**: 检测到人脸时自动截取摄像头图像
- **技术**: 实时视频流处理，人脸检测触发机制
- **输出**: 原始人脸图像数据

#### Tagger (人脸标注器)
- **功能**: 标注人脸关键点和五官位置
- **技术**: 人脸关键点检测算法
- **输出**: 带有标注信息的图像数据

#### Splicer (图像拼接器)
- **功能**: 拼接多帧捕获的图像，形成完整分析序列
- **技术**: 图像序列处理和时间轴管理
- **输出**: 拼接后的图像序列

#### Cleaner (图像清理器)
- **功能**: 清理临时图像文件，避免存储空间堆积
- **技术**: 文件生命周期管理，自动垃圾回收
- **输出**: 系统资源优化

### 2. AI智能体协作系统 (Robot Collaboration)

#### DSA (Data Sentiment Analyzer) - 数据情感分析智能体
- **专长**: 文本数据的情感分析
- **技术**: NLP情感分类，文本特征提取
- **输入**: 文本描述、标签信息
- **输出**: 文本情感评分和分类

#### VSA (Visual Sentiment Analyzer) - 视觉情感分析智能体
- **专长**: 图像和视觉数据的情感识别
- **技术**: 计算机视觉，面部表情识别
- **输入**: 人脸图像、表情特征
- **输出**: 视觉情感评分和分类



#### JSA (Judgment Sentiment Arbiter) - 情感裁定者智能体
- **专长**: 综合多个智能体的分析结果，做出最终判断
- **技术**: 多源数据融合，决策算法
- **输入**: 各智能体的分析结果
- **输出**: 最终情感分析报告

### 3. API集成层 (API Integration Layer)

#### 多AI服务支持
- **Face++**: 专业人脸检测和分析
- **OpenAI**: 强大的语言理解和生成
- **Anthropic**: 安全可靠的AI助手
- **Gemini**: 多模态AI能力
- **OpenRouter**: 统一的AI模型访问接口

#### API管理特性
- 统一的API调用接口
- 错误处理和重试机制
- 负载均衡和故障转移
- API密钥安全管理

### 4. 外部系统集成 (External Integration)



#### TouchDesigner Link
- **用途**: 创意视觉效果和交互设计
- **应用场景**: 实时视觉反馈，艺术装置控制
- **通信方式**: OSC协议，网络通信

#### ComfyUI Link
- **用途**: AI图像生成和处理工作流
- **应用场景**: 情感可视化，艺术创作
- **通信方式**: API调用，工作流触发

## 系统工作流程

### 1. 数据采集阶段
```
摄像头监控 → 人脸检测 → 图像捕获 → 关键点标注
```

### 2. 数据处理阶段
```
图像预处理 → 特征提取 → 多模态分析 → 数据清理
```

### 3. AI分析阶段
```
DSA文本分析 ↘
VSA视觉分析 → JSA综合裁定 → 最终结果
```

### 4. 结果输出阶段
```
分析报告 → 可视化展示 → 外部系统联动 → 数据存储
```

## 技术特色

### 1. 多智能体协作
- 专业化分工，各司其职
- 协同决策，提高准确性
- 可扩展架构，易于添加新智能体

### 2. 多API集成
- 降低单一服务依赖风险
- 充分利用各AI服务优势
- 成本优化和性能平衡

### 3. 实时处理能力
- 低延迟图像捕获
- 流式数据处理
- 实时结果反馈

### 4. 创意工具集成
- 支持艺术创作应用
- 跨平台协作能力
- 丰富的输出形式

## 部署和配置

### 环境要求
- Python 3.8+
- 摄像头设备
- 网络连接(API调用)
- 充足的计算资源

### 配置步骤
1. 安装依赖: `uv install`
2. 配置API密钥
3. 设置摄像头权限
4. 启动后端服务
5. 启动前端应用

### 扩展性考虑
- 模块化设计便于功能扩展
- 标准化接口支持新API集成
- 插件化架构支持自定义智能体
- 配置化管理支持多环境部署

---

*本文档基于第一性原理思考框架，从项目基础架构出发，系统性地分析了FaceAna-MTQ项目的技术架构和实现方案。*
