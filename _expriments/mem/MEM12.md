# 记忆文件 MEM12

## ComfyUI调用逻辑重构

### 关键信息

1. **工作流目录位置**：
   - 实际工作流文件位于 `/src/_backend/workflows` 目录
   - 包含多个情绪特定的工作流文件（happy.json, sad.json, angry.json等）

2. **工作流文件格式**：
   - 使用ComfyUI导出的原始API格式JSON文件
   - 关键节点应该有标题（_meta.title）以便于查找和修改

3. **ComfyUIService核心功能**：
   - 加载和修改工作流文件
   - 查找特定节点（通过标题或类型）
   - 发送工作流到ComfyUI API
   - 通过WebSocket等待和获取生成结果

4. **API路由**：
   - `/api/v1/generation/from-emotion`：从情绪数据生成图像
   - `/api/v1/generation/status/{prompt_id}`：获取生成状态
   - `/api/v1/generation/result/{prompt_id}`：获取生成结果

### 实现细节

1. **工作流查找逻辑**：
   ```python
   # 尝试加载情绪特定的工作流
   workflow_filename = f"{emotion.lower()}.json"
   workflow = self.load_workflow_from_file(workflow_filename)
   
   # 如果没有找到情绪特定的工作流，使用默认工作流
   if not workflow:
       workflow = self.load_workflow_from_file("test.json")
   
   # 如果还是加载失败，使用硬编码的默认工作流
   if not workflow:
       return self._create_default_workflow(...)
   ```

2. **节点查找方法**：
   ```python
   # 通过标题查找节点
   def find_node_by_title(self, workflow_data, target_title):
       for node_id, node_info in workflow_data.items():
           if node_info.get("_meta", {}).get("title") == target_title:
               return node_id
       return None
   
   # 通过类型查找节点
   def find_node_by_class_type(self, workflow_data, class_type):
       found_nodes = [node_id for node_id, node_info in workflow_data.items() 
                     if node_info["class_type"] == class_type]
       if len(found_nodes) == 1:
           return found_nodes[0]
       return None
   ```

3. **提示词处理**：
   - 保留工作流文件中的原始提示词
   - 只在用户提供自定义提示词时，将其添加到原始提示词之后

### 待完成事项

1. 调整工作流目录路径配置，确保与实际项目结构一致
2. 测试不同情绪类型的工作流加载和修改
3. 实现图像生成结果的存储和管理
4. 添加更多的错误处理和日志记录

### 注意事项

1. 工作流文件格式必须符合ComfyUI API要求
2. 关键节点应该有明确的标题，如"PositivePromptNode"、"NegativePromptNode"等
3. 默认工作流文件（test.json）应该始终存在，作为回退选项
4. 自定义提示词会添加到原始提示词之后，而不是替换原始提示词 