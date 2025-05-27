# EmoScan GUI 应用

基于Flet框架的多智能体情绪识别桌面应用。

## 🚀 快速开始

### 1. 安装依赖

#### 方法一：自动安装（推荐）
```bash
# 使用智能安装脚本，自动处理依赖冲突
python install_dependencies.py
```

#### 方法二：手动安装
```bash
# 使用uv（更快）
uv pip install -r requirements.txt

# 或使用传统pip
pip install -r requirements.txt

# 如果遇到版本冲突，使用最小依赖
pip install -r requirements_minimal.txt
```

#### 方法三：验证安装
```bash
# 检查依赖安装状态
python check_installation.py
```

### 2. 配置API密钥

创建 `.env` 文件并配置API密钥：

```bash
# Face++ API
FACEPP_API_KEY=your_facepp_api_key
FACEPP_API_SECRET=your_facepp_api_secret

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key

# Gemini API
GEMINI_API_KEY=your_gemini_api_key
```

### 3. 运行应用

```bash
# 使用启动脚本（推荐）
python run_gui.py

# 或直接运行
python -m src._backend.app.main
```

## 🎨 界面功能

### 主要组件

1. **摄像头预览** - 实时显示摄像头画面，支持人脸检测框
2. **情绪分析图表** - 柱状图显示各种情绪的强度
3. **智能体进度** - 显示DSA、VSA、JSA三个智能体的工作状态
4. **LLM输出** - 实时显示分析过程和结果
5. **置信度显示** - 显示综合分析的置信度

### 操作流程

1. 点击"开始分析"按钮
2. 系统自动捕获摄像头图像
3. 三个智能体依次进行分析
4. 实时显示分析进度和结果
5. 点击"停止分析"结束分析

## 🛠️ 技术架构

### GUI框架
- **Flet**: 基于Flutter的Python GUI框架
- **响应式设计**: 支持不同屏幕尺寸
- **实时更新**: 支持异步数据更新

### 核心组件
- **CameraPreviewComponent**: 摄像头预览和人脸检测
- **EmotionChartComponent**: 情绪分析结果可视化
- **AgentProgressComponent**: 智能体工作进度显示
- **LLMOutputComponent**: 文本输出和日志显示
- **ConfidenceDisplayComponent**: 置信度数值显示

### 数据流
```
摄像头 → 图像捕获 → 人脸检测 → API分析 → 智能体处理 → 结果显示
```

## 📁 项目结构

```
src/_backend/app/
├── main.py                 # 主应用入口
├── views/
│   └── main_view.py       # 主视图
├── components/
│   ├── camera_preview.py  # 摄像头组件
│   ├── emotion_chart.py   # 情绪图表组件
│   ├── agent_progress.py  # 智能体进度组件
│   ├── llm_output.py      # LLM输出组件
│   └── confidence_display.py # 置信度显示组件
├── utils/                 # 工具模块
└── assests/              # 资源文件
    ├── images/           # 图片资源
    └── fonts/            # 字体资源
```

## 🔧 配置选项

### 性能配置
- GPU加速支持
- 多线程处理
- 内存优化
- 缓存机制

### 界面配置
- 主题颜色
- 字体大小
- 窗口尺寸
- 组件布局

## 🐛 故障排除

### 常见问题

1. **摄像头无法启动**
   - 检查摄像头权限
   - 确认摄像头未被其他应用占用
   - 尝试更换摄像头索引

2. **API调用失败**
   - 检查网络连接
   - 验证API密钥配置
   - 查看错误日志

3. **界面显示异常**
   - 检查屏幕分辨率
   - 更新显卡驱动
   - 重启应用

### 日志查看
应用运行时会在控制台输出详细日志，包括：
- 系统状态信息
- API调用记录
- 错误和警告信息
- 性能监控数据

## 🚧 开发状态

当前版本：**v0.8.0-alpha**

### 已完成功能
- ✅ 基础GUI框架
- ✅ 摄像头预览
- ✅ 组件架构设计
- ✅ 主题和样式

### 开发中功能
- 🔄 实时数据更新
- 🔄 动画效果
- 🔄 用户交互优化

### 计划功能
- 📋 配置管理界面
- 📋 历史记录查看
- 📋 导出功能
- 📋 多语言支持

## 📞 技术支持

如有问题或建议，请：
1. 查看项目文档
2. 检查已知问题列表
3. 提交Issue或联系开发团队

---
**更新时间**: 2024-12-28
