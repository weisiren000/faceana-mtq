# 记忆 - 图像生成与显示功能修复

## 项目架构
- 前端：Next.js + Electron
- 后端：FastAPI
- 图像生成：ComfyUI (端口8188)

## 关键修改
1. 在ComfyUIService中添加了输出目录配置
2. 在FastAPI应用中添加了静态文件服务
3. 改进了前端图像加载逻辑

## 重要路径
- 图像输出目录：项目根目录/output/
- 后端API：http://localhost:8000
- ComfyUI服务：http://localhost:8188

## 技术要点
1. FastAPI静态文件服务配置
   ```python
   app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
   ```

2. 前端轮询机制
   ```typescript
   // 每3秒检查一次状态
   pollInterval = setInterval(checkGenerationStatus, 3000);
   ```

3. 图像URL处理
   ```typescript
   // 如果是相对路径，拼接后端URL
   if (imageUrl.startsWith('/output/')) {
     imageUrl = `${backendUrl}${imageUrl}`;
   }
   ```

## 注意事项
1. 确保output目录有正确的写入权限
2. ComfyUI需要单独启动在8188端口
3. 图像生成可能需要较长时间，需要耐心等待 