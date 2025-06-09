# EmoScan 桌面应用安装指南

## 📦 安装方式

由于网络环境限制，我们提供了源码安装方式：

### 方式一：源码运行 (推荐)

1. **安装Node.js** (v18.0+)
   - 下载: https://nodejs.org/
   - 验证: `node --version`

2. **安装依赖**
   ```bash
   npm install --legacy-peer-deps
   ```

3. **运行开发模式**
   ```bash
   # 确保后端服务已启动 (http://localhost:8000)
   npm run electron-dev
   ```

4. **构建生产版本**
   ```bash
   npm run build
   npm run electron
   ```

### 方式二：手动打包

如果需要生成安装包，请执行：

```bash
# Windows
npm run electron-pack

# 或者指定平台
npx electron-builder --win
npx electron-builder --mac  
npx electron-builder --linux
```

## 🔧 配置说明

### 环境要求
- Node.js 18.0+
- npm 或 pnpm
- 后端服务运行在 http://localhost:8000

### 网络配置
如果遇到下载问题，可以配置镜像：

```bash
# 设置npm镜像
npm config set registry https://registry.npmmirror.com

# 设置Electron镜像
npm config set electron_mirror https://npmmirror.com/mirrors/electron/
```

## 🚀 启动流程

1. **启动后端服务**
   ```bash
   cd ../backend-service
   # Windows
   start.bat
   # Linux/Mac
   ./start.sh
   ```

2. **启动桌面应用**
   ```bash
   npm run electron-dev
   ```

## 📁 文件说明

```
desktop-app/
├── web-files/          # Next.js构建的静态文件
├── electron/           # Electron主进程文件
│   ├── main.js         # 主进程入口
│   └── preload.js      # 预加载脚本
├── package.json        # 项目配置
└── README.md          # 本文件
```

## 🔍 故障排除

### 常见问题

**Q: 应用启动后显示空白页面**
A: 检查后端服务是否正常运行，确保 http://localhost:8000 可访问

**Q: 摄像头无法访问**
A: 检查系统权限设置，允许应用访问摄像头

**Q: 依赖安装失败**
A: 使用 `npm install --legacy-peer-deps` 解决依赖冲突

**Q: Electron打包失败**
A: 检查网络连接，或使用镜像源

### 开发模式调试

1. **打开开发者工具**
   - 快捷键: `Ctrl+Shift+I` (Windows/Linux) 或 `Cmd+Option+I` (Mac)

2. **查看控制台日志**
   - 检查网络请求状态
   - 查看JavaScript错误

3. **重新加载应用**
   - 快捷键: `Ctrl+R` (Windows/Linux) 或 `Cmd+R` (Mac)

## 🎯 性能优化

### 生产环境优化
- 使用 `npm run build` 构建优化版本
- 启用代码分割和Tree Shaking
- 压缩静态资源

### 内存优化
- 关闭不必要的开发者工具
- 定期清理摄像头缓存
- 限制并发API调用

## 📞 技术支持

如果遇到问题，请：
1. 查看控制台错误日志
2. 检查后端服务状态
3. 确认网络连接正常
4. 提交Issue到GitHub仓库

---

**版本**: v1.0.0  
**更新日期**: 2025年6月10日
