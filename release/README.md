# EmoScan v1.0.0 - 智能情感分析桌面应用

## 📦 发布包说明

本发布包包含两个版本：
- **开发者版本** - 适合技术用户，可自定义配置
- **一键安装版本** - 适合普通用户，双击即用

## 🚀 快速开始

### 开发者版本安装

1. **安装Python环境** (Python 3.8+)
2. **安装后端依赖**
   ```bash
   cd backend-service
   pip install -r requirements.txt
   ```
3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加你的API密钥
   ```
4. **启动后端服务**
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   ./start.sh
   ```
5. **安装桌面应用**
   - Windows: 运行 `desktop-app/EmoScan-Setup.exe`
   - macOS: 打开 `desktop-app/EmoScan.dmg`
   - Linux: 运行 `desktop-app/EmoScan.AppImage`

### 一键安装版本

1. **Windows用户**
   ```
   双击运行 EmoScan-Installer.exe
   ```
2. **启动应用**
   ```
   安装完成后，桌面会出现 EmoScan 图标
   双击启动即可使用
   ```

## ⚙️ 配置说明

### 必需的API密钥

在 `.env` 文件中配置以下API密钥：

```env
# OpenAI API (必需)
OPENAI_API_KEY=your_openai_api_key_here

# Face++ API (必需)
FACEPP_API_KEY=your_facepp_api_key_here
FACEPP_API_SECRET=your_facepp_api_secret_here

# 即梦API (可选，用于图像生成)
JIMENG_API_KEY=your_jimeng_api_key_here
```

### 获取API密钥

1. **OpenAI API**
   - 访问: https://platform.openai.com/api-keys
   - 注册账号并创建API密钥

2. **Face++ API**
   - 访问: https://www.faceplusplus.com/
   - 注册开发者账号获取API密钥

3. **即梦API** (可选)
   - 访问: https://www.jimeng.ai/
   - 注册账号获取API密钥

## 🎮 使用指南

### 基本操作

1. **启动应用** - 确保后端服务已启动
2. **选择模式** - 快速模式(~5秒) 或 详细模式(~20秒)
3. **开始扫描** - 点击"START SCAN"按钮
4. **查看结果** - 实时查看情感分析和生成的图像

### 功能特性

- 🎥 **实时摄像头捕获** - 高质量视频流
- 🧠 **多AI情感分析** - OpenAI + Face++ 双重分析
- 🎨 **ComfyUI图像生成** - 基于情感生成艺术图像
- 📊 **可视化分析** - 情感数据图表和雷达图
- 🌓 **主题切换** - 深色/浅色主题
- ⚡ **双模式分析** - 快速/详细模式选择

## 🔧 故障排除

### 常见问题

**Q: 后端服务启动失败**
A: 检查Python环境和依赖安装，确保端口8000未被占用

**Q: 摄像头无法访问**
A: 检查摄像头权限，确保没有其他应用占用摄像头

**Q: API调用失败**
A: 检查网络连接和API密钥配置，确保密钥有效且有余额

**Q: 图像生成失败**
A: 检查ComfyUI服务是否运行，或使用模拟数据模式

### 技术支持

- 📧 邮箱: support@emoscan.com
- 🐛 问题反馈: https://github.com/your-username/faceana-mtq/issues
- 📖 文档: https://github.com/your-username/faceana-mtq/docs

## 📄 许可证

本软件采用 MIT 许可证开源。详见 LICENSE 文件。

## 🙏 致谢

感谢以下开源项目和服务：
- OpenAI - AI模型支持
- Face++ - 人脸识别服务
- ComfyUI - 图像生成框架
- Next.js - React框架
- FastAPI - Python Web框架

---

**EmoScan Team**  
版本: v1.0.0  
发布日期: 2025年6月10日
