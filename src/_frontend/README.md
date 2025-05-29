# EmoScan Desktop App 🎭

> 基于AI的实时情感分析桌面应用

EmoScan是一个使用人工智能技术进行实时面部情感识别的桌面应用程序。通过摄像头捕获用户面部表情，分析情感状态并生成详细的心理分析报告。

## ✨ 主要功能

- 🎥 **实时摄像头捕获** - 使用用户摄像头进行视频流处理
- 🧠 **AI情感识别** - 识别7种标准情绪（愤怒、厌恶、恐惧、高兴、平静、悲伤、惊讶）
- 📊 **数据可视化** - 通过进度条和雷达图展示情感数据
- 📝 **AI分析报告** - 生成详细的心理分析报告
- 🎨 **科幻UI界面** - 黑绿配色的终端风格界面
- 💻 **跨平台支持** - Windows、macOS、Linux

## 🚀 快速启动指南

### 方法一：推荐的启动方式（已验证有效）

```powershell
# 1. 进入项目目录
Set-Location "D:\codee\faceana-mtq\src\_frontend"

# 2. 启动Next.js开发服务器（保持运行）
npm run dev

# 3. 新开一个PowerShell窗口，设置环境变量并启动Electron
Set-Location "D:\codee\faceana-mtq\src\_frontend"
$env:NODE_ENV="development"
npx electron .
```

### 方法二：一键启动（如果环境配置正确）

```powershell
Set-Location "D:\codee\faceana-mtq\src\_frontend"
npm run electron-dev
```

## 📋 系统要求

- **Node.js** 18+
- **npm** 9+
- **摄像头设备**
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## 🛠️ 安装依赖

```powershell
# 进入前端目录
Set-Location "D:\codee\faceana-mtq\src\_frontend"

# 安装依赖（如果遇到版本冲突）
npm install --legacy-peer-deps
```

## 📁 项目结构

```
src/_frontend/
├── app/                    # Next.js应用目录
│   ├── globals.css        # 全局样式
│   ├── layout.tsx         # 应用布局
│   └── page.tsx           # 主页面组件
├── electron/              # Electron相关文件
│   ├── main.js           # 主进程
│   └── preload.js        # 预加载脚本
├── components/            # React组件
├── hooks/                 # 自定义Hooks
├── lib/                   # 工具库
├── public/               # 静态资源
├── styles/               # 样式文件
├── package.json          # 项目配置和依赖
├── next.config.mjs       # Next.js配置
├── tailwind.config.ts    # Tailwind CSS配置
└── tsconfig.json         # TypeScript配置
```

## 🎮 可用命令

```powershell
# 开发相关
npm run dev              # 启动Next.js开发服务器
npm run build            # 构建Next.js应用
npm run export           # 导出静态文件
npm run start            # 启动生产服务器
npm run lint             # 代码检查

# Electron相关
npm run electron         # 启动Electron应用（生产模式）
npm run electron-dev     # 启动Electron开发模式
npm run electron-pack    # 打包桌面应用

# 工具命令
npx electron .           # 直接启动Electron
npx next dev            # 直接启动Next.js
```

## 🔧 故障排除

### 问题1: npm找不到package.json

**错误信息**:
```
npm error path D:\codee\faceana-mtq\package.json
npm error errno -4058
npm error enoent Could not read package.json
```

**解决方案**:
```powershell
# 确保在正确的目录中
Set-Location "D:\codee\faceana-mtq\src\_frontend"
# 然后运行命令
npm run dev
```

### 问题2: Electron加载错误的文件

**错误信息**:
```
electron: Failed to load URL: file:///D:/codee/faceana-mtq/src/_frontend/out/index.html with error: ERR_FILE_NOT_FOUND
```

**解决方案**:
```powershell
# 设置开发环境变量
$env:NODE_ENV="development"
npx electron .
```

### 问题3: 依赖版本冲突

**错误信息**:
```
npm error ERESOLVE unable to resolve dependency tree
```

**解决方案**:
```powershell
npm install --legacy-peer-deps
```

### 问题4: concurrently或wait-on命令未找到

**解决方案**:
```powershell
# 重新安装依赖
npm install --legacy-peer-deps

# 或者分步启动（推荐）
npm run dev  # 终端1
npx electron .  # 终端2
```

## 🎯 使用说明

1. **启动应用**后，您将看到三个主要面板：
   - **左侧**: 摄像头视频输入区域
   - **中间**: 情感分析数据可视化
   - **右侧**: AI分析输出区域

2. **点击"START SCAN"**开始摄像头捕获

3. **观察实时效果**:
   - 扫描线动画效果
   - 情感数据进度条
   - 雷达图可视化
   - AI分析报告生成

## 🛡️ 安全配置

应用采用了Electron的最佳安全实践：

- ✅ **禁用Node.js集成** (`nodeIntegration: false`)
- ✅ **启用上下文隔离** (`contextIsolation: true`)
- ✅ **使用预加载脚本** 安全暴露API
- ✅ **启用Web安全** (`webSecurity: true`)
- ✅ **外部链接保护** 防止恶意导航

## 🔄 开发模式 vs 生产模式

### 开发模式
- 连接到 `http://localhost:3000`
- 自动打开开发者工具
- 支持热重载
- 显示详细错误信息

### 生产模式
- 加载静态文件 `out/index.html`
- 优化性能
- 隐藏开发者工具
- 错误处理更加友好

## 🏗️ 技术栈

### 前端框架
- **Next.js** 15.2.4 - React全栈框架
- **React** 19 - UI库
- **TypeScript** 5 - 类型安全

### 样式和UI
- **Tailwind CSS** 3.4.17 - 原子化CSS框架
- **Radix UI** - 无障碍UI组件库
- **Lucide React** - 图标库

### 桌面化
- **Electron** 36.3.2 - 跨平台桌面应用框架
- **electron-builder** 26.0.12 - 应用打包工具

### 开发工具
- **concurrently** - 并发运行多个命令
- **wait-on** - 等待服务就绪
- **electron-reload** - 开发模式热重载

## 📦 打包分发

```powershell
# 构建并打包应用
npm run electron-pack

# 输出目录
dist-electron/
├── win-unpacked/     # Windows未打包版本
├── EmoScan Setup.exe # Windows安装程序
└── ...
```

## 🤝 开发贡献

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 获取帮助

如果遇到问题：

1. 查看本README的故障排除部分
2. 检查 [Issues](../../issues) 页面
3. 创建新的Issue描述问题

---

**开发状态**: ✅ Electron架构转换完成，UI优化进行中
**下一步**: 情绪识别API集成和桌面功能增强

*最后更新: 2025-05-29*
