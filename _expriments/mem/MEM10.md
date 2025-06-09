# MEM10 - ComfyUI集成与工作流配置记忆

## 关键信息

1. **项目结构**
   - 后端API位于`src/_backend`目录
   - ComfyUI工作流文件存储在`src/_backend/workflows`目录
   - 前端Electron应用位于`src/_frontend`目录
   - ComfyUI集成API位于`src/_frontend/lib/comfyui-api.ts`

2. **ComfyUI服务**
   - ComfyUI服务默认运行在`8188`端口
   - 生成的图像保存在ComfyUI安装目录的`output`文件夹中
   - 图像文件命名格式：`emoscan_{emotion}_{timestamp}.png`
   - 图像URL格式：`http://localhost:8188/view?filename=文件名`

3. **工作流配置**
   - 工作流文件采用JSON格式
   - 文件命名约定：`{emotion}.json`（如`happy.json`、`sad.json`等）
   - 默认工作流文件：`test.json`
   - 工作流节点链：KSampler → VAEDecode → SaveImage

4. **API接口**
   - 后端API端点：`http://localhost:8000/api/v1/generation/from-emotion`
   - 请求格式：
     ```json
     {
       "emotion": "happy",
       "intensity": 0.8,
       "custom_prompt": "可选的自定义提示词",
       "comfyui_url": "http://localhost:8188"
     }
     ```
   - 响应格式：
     ```json
     {
       "success": true,
       "prompt_id": "生成ID",
       "prompt": "实际使用的提示词",
       "status": "generating"
     }
     ```

## 工作流结构

ComfyUI工作流是一个JSON对象，包含多个节点及其连接关系。一个典型的图像生成工作流包含以下节点：

1. **CheckpointLoaderSimple (节点4)**
   - 加载模型权重
   - 输出：模型、CLIP模型、VAE模型

2. **EmptyLatentImage (节点5)**
   - 创建空白潜在图像
   - 设置宽度、高度和批次大小

3. **CLIPTextEncode (节点6 - 正面提示词)**
   - 将正面提示词文本转换为CLIP嵌入
   - 输入：文本、CLIP模型
   - 输出：正面条件

4. **CLIPTextEncode (节点7 - 负面提示词)**
   - 将负面提示词文本转换为CLIP嵌入
   - 输入：文本、CLIP模型
   - 输出：负面条件

5. **KSampler (节点3)**
   - 执行扩散采样过程
   - 输入：模型、正面条件、负面条件、空白潜在图像
   - 输出：潜在图像

6. **VAEDecode (节点8)**
   - 将潜在图像转换为RGB图像
   - 输入：潜在图像、VAE模型
   - 输出：RGB图像

7. **SaveImage (节点9)**
   - 保存生成的图像
   - 输入：RGB图像、文件名前缀
   - 输出：无

## 情绪到提示词映射

系统使用以下映射将情绪转换为生成提示词：

| 情绪 | 提示词 |
|------|--------|
| happy | a joyful scene with bright colors, sunshine, smiling people |
| sad | a melancholic scene with rain, dark colors, lonely figure |
| angry | a dramatic scene with intense red colors, stormy weather |
| surprised | a scene with unexpected elements, bright contrasts |
| neutral | a balanced scene with natural colors, calm atmosphere |
| disgusted | a scene with unsettling elements, sickly green tones |
| fearful | a dark scene with shadows, fog, mysterious elements |

## 常见问题与解决方案

1. **导入错误**
   - 问题：`ImportError: attempted relative import beyond top-level package`
   - 解决方案：使用绝对导入替代相对导入

2. **工作流节点连接错误**
   - 问题：`Required input is missing: images`
   - 解决方案：确保SaveImage节点的输入来自VAEDecode节点的输出

3. **ComfyUI连接问题**
   - 问题：`Cannot connect to host localhost:8188`
   - 解决方案：确保ComfyUI服务正在运行，并且端口配置正确

4. **CORS错误**
   - 问题：浏览器阻止跨域请求
   - 解决方案：通过Electron主进程中转请求或使用CORS代理

## 未来扩展记录

1. **情绪特定工作流**
   - 为每种情绪创建专门的工作流文件
   - 可以为不同情绪使用不同的模型、采样器和参数

2. **工作流编辑功能**
   - 开发一个简单的工作流编辑界面
   - 允许用户在应用内创建和修改工作流

3. **结果回传功能**
   - 实现从ComfyUI获取生成结果
   - 将生成的图像显示在应用中

4. **实时进度更新**
   - 使用WebSocket与ComfyUI保持实时连接
   - 显示图像生成的实时进度 