# EmoScan 项目技术栈文档

## 项目概述
EmoScan 是一个基于人工智能的情感分析桌面应用，采用前后端分离架构，支持实时图像情感识别、多AI模型分析和ComfyUI图像生成。

## 🎯 项目架构
```
faceana-mtq/
├── src/
│   ├── _frontend/         # Next.js + Electron 前端桌面应用
│   └── _backend/          # FastAPI 后端API服务
├── comfyui/
│   └── custom_nodes/      # ComfyUI自定义节点
├── docs/                  # 项目文档
├── test/                  # 测试文件
├── _expriments/          # 开发经验记录
│   ├── exp/              # 经验总结
│   ├── sum/              # 对话总结
│   └── mem/              # 记忆存储
└── output/               # 输出文件
```

---

## 🖥️ 前端技术栈

### 核心框架
- **Next.js 15.2.4** - React全栈框架，支持SSG静态导出
- **React 19** - 用户界面库，最新版本
- **TypeScript 5** - 类型安全的JavaScript超集
- **Electron 36.3.2** - 跨平台桌面应用框架

### UI组件库
- **Radix UI** - 无样式、可访问的UI组件库
  - 包含40+组件：Dialog、Dropdown、Toast、Tabs、Accordion等
- **shadcn/ui** - 基于Radix UI的现代组件系统
- **Lucide React 0.454.0** - 现代图标库
- **Class Variance Authority** - 组件变体管理
- **CLSX** - 条件类名工具

### 样式系统
- **Tailwind CSS 3.4.17** - 实用优先的CSS框架
- **tailwindcss-animate** - Tailwind动画插件
- **PostCSS 8** - CSS后处理器
- **CSS Variables** - 动态主题系统
- **next-themes** - 主题切换管理

### 表单处理
- **React Hook Form 7.54.1** - 高性能表单库
- **Zod 3.24.1** - TypeScript优先的模式验证
- **@hookform/resolvers** - 表单验证解析器
- **Input OTP** - OTP输入组件

### 数据可视化
- **Recharts 2.15.0** - React图表库
- **Embla Carousel** - 轮播组件
- **React Day Picker** - 日期选择器

### 开发工具
- **Concurrently** - 并行运行多个命令
- **Wait-on** - 等待资源可用
- **Cross-env** - 跨平台环境变量
- **Electron Builder** - Electron应用打包工具
- **Electron Reload** - 开发时热重载

### 包管理器
- **npm** - 主要包管理器（package-lock.json）
- **pnpm** - 备用包管理器（pnpm-lock.yaml）

---

## 🔧 后端技术栈

### 核心框架
- **FastAPI 0.104.1+** - 现代、快速的Python Web框架
- **Uvicorn 0.24.0+** - ASGI服务器，支持标准扩展
- **Python 3.8+** - 编程语言

### 数据处理
- **Pydantic 2.5.0+** - 数据验证和序列化
- **Pillow 10.1.0+** - 图像处理库
- **aiofiles 23.2.1+** - 异步文件操作
- **aiohttp 3.9.0+** - 异步HTTP客户端

### HTTP客户端
- **Requests 2.31.0+** - HTTP库
- **python-multipart 0.0.6+** - 多部分表单数据处理

### AI集成
- **OpenAI 1.30.0+** - OpenAI API客户端
- **Face++ API** - 旷视科技情感识别服务
- **ComfyUI集成** - 工作流图像生成

### 配置管理
- **python-dotenv 1.0.0+** - 环境变量管理

### 测试框架
- **pytest 7.0.0+** - 测试框架
- **pytest-asyncio 0.21.0+** - 异步测试支持
- **httpx 0.25.0+** - 异步HTTP客户端

### 包管理器
- **uv** - 现代Python包管理器（主要）
- **pip** - 传统包管理器（备用）

---

## 🎨 ComfyUI集成

### 自定义节点
- **comfyui-jimeng-api** - 即梦API集成节点
- **文件保存节点** - 支持指定文件名覆盖
- **OSC发送节点** - 任务完成通知

### 工作流管理
- **情绪映射工作流** - 7种基础情绪对应的生成工作流
- **动态种子** - 每次生成使用随机种子
- **实时生成** - 无缓存，每次调用生成新图像

---

## 🏗️ 构建系统

### 前端构建
```json
{
  "dev": "next dev",                    // 开发服务器
  "build": "next build",               // 生产构建
  "export": "next build && next export", // 静态导出
  "electron-dev": "并行运行Next.js + Electron",
  "electron-pack": "打包桌面应用"
}
```

### 后端构建
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 🔌 API集成

### 内部API
- **FastAPI后端** - 本地情感分析服务
- **RESTful API** - 标准HTTP接口
- **ComfyUI API** - 图像生成工作流调用

### 外部API
- **OpenAI API** - GPT模型情感分析
- **Face++ API** - 旷视科技人脸情感识别
- **即梦API** - 图像生成服务

### API端点
```
GET  /health                           # 健康检查
POST /api/v1/analyze/image            # 单图情感分析
POST /api/v1/analyze/batch            # 批量情感分析
POST /api/v1/analyze-and-generate     # 分析+生成
POST /api/v1/generation/generate-from-analysis  # 基于分析生成图像
```

---

## 📦 部署配置

### Electron打包
```json
{
  "appId": "com.emoscan.desktop",
  "productName": "EmoScan",
  "targets": {
    "mac": "dmg",
    "win": "nsis",
    "linux": "AppImage"
  }
}
```

### 环境配置
- **开发环境**: Next.js dev server + Electron + ComfyUI
- **生产环境**: 静态文件 + Electron打包

---

## 🎨 设计系统

### 主题系统
- **Dark/Light模式** - 自动主题切换
- **CSS变量** - 动态颜色系统
- **HSL颜色空间** - 一致的颜色管理
- **科技风格** - 网格背景、扫描线效果

### 动画系统
- **Tailwind动画** - 预定义动画类
- **自定义动画** - 手风琴、渐变效果
- **滚动动画** - 3D透视效果
- **打字机效果** - AI输出文本动画
- **实时扫描** - 摄像头扫描线动画

### 响应式设计
- **桌面优化** - Electron窗口适配
- **三栏布局** - 摄像头、分析、输出
- **实时更新** - 情绪数据可视化

---

## 🔧 开发工具链

### 代码质量
- **TypeScript** - 静态类型检查
- **ESLint** - 代码规范检查
- **Prettier** - 代码格式化

### 版本控制
- **Git** - 版本控制系统
- **GitHub** - 代码托管平台

### 项目管理
- **分支策略**: main, developer, 功能分支
- **文档管理**: docs/, _expriments/
- **测试管理**: test/ 目录分类

---

## 📊 性能优化

### 前端优化
- **静态导出** - Next.js SSG
- **图片优化** - 禁用Next.js图片优化（Electron兼容）
- **代码分割** - 自动代码分割
- **Tree Shaking** - 死代码消除
- **防抖机制** - API调用锁定防重复

### 后端优化
- **异步处理** - FastAPI异步支持
- **并发请求** - 多AI模型并行调用
- **错误处理** - 优雅降级机制
- **静态文件服务** - 输出文件直接访问

---

## 🔒 安全考虑

### API安全
- **环境变量** - 敏感信息隔离
- **CORS配置** - 跨域请求控制
- **输入验证** - Pydantic数据验证
- **文件类型检查** - 图像格式验证

### 桌面应用安全
- **本地存储** - 安全的本地数据处理
- **网络请求** - HTTPS通信
- **文件访问** - 受限文件系统访问
- **摄像头权限** - 用户授权访问

---

## 📈 扩展性

### 模块化设计
- **组件化** - 可复用UI组件
- **服务分离** - 独立的AI服务模块
- **配置驱动** - 环境变量配置
- **插件架构** - ComfyUI自定义节点

### 未来扩展
- **多语言支持** - i18n国际化
- **插件系统** - 可扩展AI模型
- **云端部署** - 容器化部署支持
- **实时流处理** - 视频流情感分析

---

## 🧪 测试架构

### 测试分类
- **API测试** - 后端接口测试
- **前端测试** - 组件单元测试
- **集成测试** - 端到端测试
- **调试工具** - ComfyUI状态监控

### 测试工具
- **pytest** - Python测试框架
- **httpx** - 异步HTTP测试
- **Jest** - JavaScript测试框架（潜在）

---

*最后更新: 2025年6月8日*