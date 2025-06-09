# EmoScan v1.0.0 开发者版本安装指南

## 🚀 快速安装

### 第一步：环境准备

1. **安装Python 3.8+**
   ```bash
   # 检查Python版本
   python --version
   # 或
   python3 --version
   ```

2. **安装Node.js 18.0+**
   ```bash
   # 检查Node.js版本
   node --version
   npm --version
   ```

### 第二步：后端服务安装

1. **进入后端目录**
   ```bash
   cd backend-service
   ```

2. **安装Python依赖**
   ```bash
   # 创建虚拟环境（推荐）
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **配置API密钥**
   ```bash
   # 复制配置模板
   cp .env.example .env
   
   # 编辑.env文件，添加你的API密钥
   # OPENAI_API_KEY=your_openai_key_here
   # FACEPP_API_KEY=your_facepp_key_here
   # FACEPP_API_SECRET=your_facepp_secret_here
   ```

4. **启动后端服务**
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   ./start.sh
   
   # 或直接运行
   python start_server.py
   ```

### 第三步：桌面应用安装

1. **进入桌面应用目录**
   ```bash
   cd ../desktop-app
   ```

2. **安装Node.js依赖**
   ```bash
   npm install --legacy-peer-deps
   ```

3. **启动桌面应用**
   ```bash
   # 开发模式（推荐）
   npm run electron-dev
   
   # 或分步启动
   npm run dev        # 启动Next.js开发服务器
   npm run electron   # 启动Electron应用
   ```

## 🔧 高级配置

### ComfyUI集成（可选）

1. **安装ComfyUI**
   - 下载ComfyUI: https://github.com/comfyanonymous/ComfyUI
   - 安装到 `C:\sw\ComfyUI\` 或修改配置路径

2. **安装自定义节点**
   ```bash
   # 复制自定义节点到ComfyUI
   cp -r comfyui-nodes/custom_nodes/* /path/to/ComfyUI/custom_nodes/
   ```

3. **启动ComfyUI**
   ```bash
   cd /path/to/ComfyUI
   python main.py
   ```

### 网络配置

如果遇到网络问题，可以配置镜像源：

```bash
# npm镜像
npm config set registry https://registry.npmmirror.com

# pip镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📋 验证安装

### 检查后端服务
1. 访问 http://localhost:8000
2. 查看API文档 http://localhost:8000/docs
3. 测试健康检查 http://localhost:8000/health

### 检查桌面应用
1. 应用正常启动
2. 摄像头权限获取成功
3. 主题切换功能正常
4. 与后端API连接正常

## 🔍 故障排除

### 后端问题
- **端口占用**: 修改 `start_server.py` 中的端口号
- **依赖缺失**: 重新运行 `pip install -r requirements.txt`
- **API密钥错误**: 检查 `.env` 文件配置

### 前端问题
- **依赖冲突**: 使用 `--legacy-peer-deps` 参数
- **Electron启动失败**: 检查Node.js版本
- **摄像头无法访问**: 检查浏览器权限设置

### 网络问题
- **下载失败**: 使用镜像源或代理
- **API调用超时**: 检查网络连接和API密钥

## 📞 获取帮助

- 📖 查看完整文档: `README.md`
- 🏗️ 了解架构设计: `ARCHITECTURE.md`
- 🔧 技术栈详情: `TECH-STACK.md`
- 📝 更新日志: `CHANGELOG.md`
- 🐛 问题反馈: GitHub Issues

---

**安装完成后，你将拥有一个功能完整的AI情感分析桌面应用！**

祝你使用愉快！ 🎉
