# 项目结构

```
src/
├── _backend/                 # 后端代码
│   ├── app/                  # FastAPI应用
│   │   ├── api/              # API路由
│   │   │   └── v1/           # API v1版本
│   │   │       ├── emotion.py - 情感分析API路由
│   │   │       ├── generation.py - 图像生成API路由
│   │   │       └── visualization.py - 可视化API路由
│   │   ├── models/           # 数据模型
│   │   │   ├── comfyui.py    # ComfyUI相关模型
│   │   │   ├── emotion.py    # 情感分析数据模型
│   │   │   └── visualization.py - 可视化数据模型
│   │   ├── services/         # 服务层
│   │   │   ├── comfyui_service.py # ComfyUI服务
│   │   │   ├── emotion_service.py - 情感分析服务
│   │   │   └── visualization_service.py - 可视化服务
│   │   └── main.py - 后端应用入口
│   ├── config/               # 配置文件
│   ├── workflows/            # ComfyUI工作流文件
│   │   ├── test.json         # 默认工作流模板
│   │   ├── happy.json        # 快乐情绪工作流（可选）
│   │   ├── sad.json          # 悲伤情绪工作流（可选）
│   │   ├── angry.json        # 愤怒情绪工作流（可选）
│   │   ├── surprised.json    # 惊讶情绪工作流（可选）
│   │   ├── neutral.json      # 中性情绪工作流（可选）
│   │   ├── disgusted.json    # 厌恶情绪工作流（可选）
│   │   └── fearful.json      # 恐惧情绪工作流（可选）
│   └── start_server.py       # 服务启动脚本
└── _frontend/                # 前端代码
    ├── app/                  # Next.js应用页面
    │   ├── client-body-class.tsx  # Electron客户端类处理
    │   ├── globals.css       # 全局样式
    │   ├── layout.tsx        # 布局组件
    │   └── page.tsx          # 主页面组件
    ├── components/           # React组件
    │   └── emotion-to-image/ # 情绪图像生成组件
    │       └── GenerationPanel.tsx # ComfyUI集成面板
    ├── electron/             # Electron相关代码
    │   ├── main.js           # Electron主进程
    │   └── preload.js        # Electron预加载脚本
    ├── hooks/                # React钩子
    │   ├── useImageGeneration.ts # 图像生成钩子
    │   ├── use-mobile.tsx    # 移动设备检测钩子
    │   └── use-toast.ts      # 通知提示钩子
    ├── lib/                  # 工具库
    │   └── comfyui-api.ts    # ComfyUI API客户端
    ├── package.json          # 前端依赖配置
    └── next-env.d.ts         # Next.js类型声明

output/                       # 生成图像输出目录
    └── *.png                 # 生成的图像文件

_expriments/                  # 项目经验和记忆
    ├── exp/                  # 经验总结
    ├── sum/                  # 对话总结
    └── mem/                  # 记忆存储
```

# 项目概述

这是一个基于Electron和Next.js的桌面应用程序，用于情感分析和情绪图像生成。主要功能包括：

1. 情感分析：分析用户表情和情绪状态
2. 情绪可视化：将分析结果以图表形式展示
3. 情绪图像生成：通过ComfyUI将情绪转化为艺术图像

## 技术栈

- **前端**：Next.js + React + TypeScript
- **桌面应用**：Electron
- **图像生成**：ComfyUI (端口8188)
- **UI组件**：自定义组件

## 主要功能模块

### 1. Electron集成

- `electron/main.js`：主进程，负责创建窗口和管理应用生命周期
- `electron/preload.js`：预加载脚本，提供渲染进程与主进程通信的API

### 2. 情感分析界面

- `app/page.tsx`：主界面，包含情感分析和结果展示

### 3. 图像生成集成

- `components/emotion-to-image/GenerationPanel.tsx`：ComfyUI集成面板
- `hooks/useImageGeneration.ts`：图像生成逻辑钩子
- `lib/comfyui-api.ts`：ComfyUI API客户端
- `_backend/workflows/`：情绪特定的ComfyUI工作流配置
  - 支持为每种情绪类型（happy、sad、angry等）创建专用的工作流文件
  - 命名格式为`{emotion}.json`，例如`happy.json`
  - 如果特定情绪的工作流文件不存在，将使用默认的`test.json`

### 4. 图像输出

- `output/`：生成的图像输出目录
  - 图像文件命名格式为`emoscan_{emotion}_{timestamp}.png`
  - 通过FastAPI静态文件服务提供图像访问
  - 前端通过HTTP请求访问图像

## 启动方式

- 开发模式：`npm run electron-dev`
- 构建应用：`npm run electron-pack`

## 注意事项

- ComfyUI需要单独启动，默认端口为8188
- 由于浏览器安全限制，前端无法直接检测ComfyUI连接状态
- 开发时需要注意CORS跨域问题
- 后端API服务需要单独启动：`cd src/_backend && python start_server.py`
- 生成的图像保存在项目根目录的output文件夹中
- 可以通过在`workflows`目录中添加情绪特定的工作流文件来自定义不同情绪的图像生成效果

## 项目架构说明

### 后端 (_backend)

#### API路由
- **emotion.py**: 提供情感分析API，接收图像或文本，返回情感分析结果
- **generation.py**: 提供图像生成API，根据情感数据生成对应的图像
- **visualization.py**: 提供可视化API，将情感数据转换为可视化图表

#### 服务
- **comfyui_service.py**: 与ComfyUI交互的服务，负责发送提示词、获取生成结果等
- **emotion_service.py**: 情感分析服务，处理情感识别和分析
- **visualization_service.py**: 可视化服务，生成情感数据的可视化表示

#### 数据模型
- **comfyui.py**: ComfyUI相关的数据模型，如生成请求和响应
- **emotion.py**: 情感分析相关的数据模型
- **visualization.py**: 可视化相关的数据模型

#### 工作流文件 (workflows)
- 包含多个情绪特定的ComfyUI工作流JSON文件
- 每个情绪类型对应一个工作流文件（如happy.json, sad.json等）
- 工作流文件定义了图像生成的节点和参数配置
- 通过标题（如"PositivePromptNode"）标识关键节点，便于动态修改

### 前端 (_frontend)

#### 组件
- **EmotionAnalysis**: 情感分析组件，用于捕获和分析情感
- **ImageGeneration**: 图像生成组件，展示和控制图像生成
- **Visualization**: 可视化组件，展示情感数据的可视化结果

#### 页面
- **index.js**: 应用主页，提供导航和概述
- **analysis.js**: 情感分析页面，用于进行情感分析
- **generation.js**: 图像生成页面，用于生成和展示图像

### 主要功能流程

1. **情感分析流程**
   - 通过前端捕获用户图像或文本
   - 调用情感分析API进行分析
   - 返回情感分析结果和可视化数据

2. **图像生成流程**
   - 基于情感分析结果选择对应的工作流文件
   - 根据需要修改工作流参数（如提示词、种子等）
   - 通过ComfyUI API发送工作流并生成图像
   - 通过WebSocket监控生成进度并获取结果
   - 在前端展示生成的图像
   - 图像保存到output目录，便于后续访问和下载

## 🔍 架构分析与优化建议 (2025-06-09)

### 当前架构优势
✅ **清晰的分层架构** - 前端层 → API层 → 服务层 → 外部API层
✅ **多API融合策略** - Face++ (60%) + Gemini/OpenRouter (40%)，提高准确性
✅ **完善的容错机制** - 自动切换备用API，确保服务可用性
✅ **现代化技术栈** - TypeScript、热重载、组件化开发
✅ **良好的项目文档** - 完整的README和经验总结
✅ **ComfyUI集成** - 支持基于情绪分析结果生成艺术图像

### 识别的主要问题
⚠️ **代码组织问题** - 前端主组件过于庞大(page.tsx 1093行)
⚠️ **配置管理分散** - API端点硬编码，环境变量管理不统一
⚠️ **错误处理不一致** - 前后端错误处理策略不统一
⚠️ **性能优化空间** - 大量DOM操作，组件重渲染频繁

### 优化建议优先级

#### 🔥 高优先级 (立即实施)
1. **前端组件拆分** - 将page.tsx拆分为CameraPanel、EmotionVisualization、AIOutputPanel等
2. **配置管理统一** - 使用Pydantic进行配置验证，集中管理环境变量
3. **错误处理标准化** - 建立统一的错误码体系和处理机制

#### 🔶 中优先级 (近期实施)
1. **性能优化** - React.memo、虚拟滚动、防抖节流机制
2. **状态管理优化** - 使用Context API或Zustand统一状态管理
3. **测试覆盖** - 添加自动化测试和代码覆盖率检查

#### 🔷 低优先级 (长期规划)
1. **微服务化** - 拆分为独立的情感分析、可视化、报告服务
2. **CI/CD流程** - 自动化构建测试和部署
3. **监控日志** - 性能监控和结构化日志系统

### 预期收益
- **短期**: 代码可维护性提升50%，开发效率提升30%，Bug修复时间减少40%
- **长期**: 系统扩展性大幅提升，团队协作效率提高，产品迭代速度加快

### 建议的重构路径
1. **第一阶段**: 前端组件拆分 + 配置管理统一
2. **第二阶段**: 性能优化 + 状态管理重构
3. **第三阶段**: 测试覆盖 + 错误处理标准化
4. **第四阶段**: 微服务化 + CI/CD + 监控系统

## 🎨 ComfyUI集成功能 (2025-06-09)

### 新增功能
- **情绪驱动图像生成**: 根据情绪分析结果自动选择对应工作流生成艺术图像
- **多工作流支持**: 为每种情绪类型配置专用的ComfyUI工作流
- **异步图像生成**: 非阻塞的图像生成流程，支持实时状态监控
- **容错机制**: ComfyUI服务不可用时不影响核心情绪分析功能

### API端点
- `GET /api/v1/generation/status` - 获取ComfyUI服务状态
- `GET /api/v1/generation/workflows` - 列出所有可用工作流
- `POST /api/v1/generation/generate` - 根据情绪生成图像
- `POST /api/v1/generation/generate-from-analysis` - 基于情绪分析结果生成图像
- `POST /api/v1/analyze-and-generate` - 一键完成情绪分析和图像生成

### 工作流配置
- 支持7种标准情绪的专用工作流：happy.json, sad.json, angry.json, surprised.json, neutral.json, disgusted.json, fearful.json
- 自动文件名前缀：`emoscan_{emotion}_{timestamp}`
- 支持自定义种子和参数
- 默认工作流：test.json（当特定情绪工作流不存在时使用）

### 技术特性
- **异步处理**: 使用aiohttp进行非阻塞HTTP请求
- **状态监控**: 实时监控ComfyUI队列状态和生成进度
- **错误处理**: 完善的异常处理和错误信息反馈
- **类型安全**: 完整的TypeScript/Python类型注解