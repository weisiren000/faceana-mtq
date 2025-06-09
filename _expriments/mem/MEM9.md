# MEM9 - Electron前端与ComfyUI集成记忆

## 关键信息

1. **项目结构**
   - Electron前端位于`src/_frontend`目录
   - 主进程文件：`src/_frontend/electron/main.js`
   - 预加载脚本：`src/_frontend/electron/preload.js`
   - 主页面组件：`src/_frontend/app/page.tsx`

2. **ComfyUI集成**
   - ComfyUI服务器默认运行在`8188`端口
   - 连接API封装在`src/_frontend/lib/comfyui-api.ts`
   - 图像生成钩子：`src/_frontend/hooks/useImageGeneration.ts`
   - 图像生成面板：`src/_frontend/components/emotion-to-image/GenerationPanel.tsx`

3. **启动命令**
   - 开发模式：`npm run electron-dev`
   - 构建：`npm run electron-pack`

4. **已知问题**
   - 浏览器CORS限制导致无法直接从前端连接ComfyUI
   - Next.js端口动态变化需要特殊处理
   - Electron需要等待Next.js服务器完全启动

## 解决方案记录

1. **Electron与Next.js集成**
   - 使用`waitForNextServer`函数检测Next.js实际运行端口
   - 使用`wait-on`工具确保Next.js服务器启动后再加载Electron

2. **ComfyUI连接**
   - 默认端口已修改为`8188`
   - 添加了CORS代理选项
   - 使用模拟连接状态避免CORS错误

3. **类型安全**
   - 在`client-body-class.tsx`中添加了全局`window.electronAPI`类型声明
   - 使用可选链操作符安全访问属性

## 未来工作记录

1. **需要实现的功能**
   - 通过Electron主进程中转请求，实现真正的ComfyUI连接检测
   - 改进错误处理和重试机制
   - 考虑使用WebSocket保持与ComfyUI的实时连接

2. **已知待解决问题**
   - 当ComfyUI服务器不可用时，需要提供更明确的错误提示
   - 图像生成功能需要完善，目前使用的是模拟数据

## 用户偏好

- 用户已经安装并运行了ComfyUI服务器
- 用户希望能够在Electron应用中直接与ComfyUI交互
- 用户可能需要修改ComfyUI的连接地址 