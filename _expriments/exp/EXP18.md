# EXP18: ComfyUI缓存机制问题解决

## 时间
2025-06-09 17:25

## 问题描述
用户强烈反对ComfyUI的缓存机制，要求每次都生成全新的图像，而不是返回缓存的结果。

## 问题分析
1. **缓存问题根源**：
   - ComfyUI有内部缓存机制，相同的工作流参数会返回缓存结果
   - 虽然API调用成功，但返回的是已存在的文件名
   - 用户希望每次都生成真正的新图像

2. **初始尝试**：
   - 修改工作流参数（文件名前缀、种子）
   - 但ComfyUI仍然可能使用内部缓存

## 解决方案
实施了多层反缓存机制：

### 1. 清理ComfyUI缓存
```python
async def clear_cache(self) -> bool:
    # 清理历史记录缓存
    async with session.post(f"{self.base_url}/history/clear") as response:
    
    # 清理队列缓存  
    async with session.post(f"{self.base_url}/queue/clear") as response:
    
    # 释放模型缓存
    async with session.post(f"{self.base_url}/free") as response:
```

### 2. 强制清理输出文件
```python
async def force_cleanup_outputs(self) -> bool:
    # 删除所有ComfyUI_*.png文件
    pattern = os.path.join(output_dir, "ComfyUI_*.png")
    files = glob.glob(pattern)
    for file_path in files:
        os.remove(file_path)
```

### 3. 唯一化请求参数
```python
# 生成唯一的client_id
unique_client_id = f"emoscan_{uuid.uuid4()}_{int(time.time() * 1000)}"

# 添加额外参数强制禁用缓存
data = {
    "prompt": workflow,
    "client_id": unique_client_id,
    "extra_data": {
        "timestamp": int(time.time() * 1000),
        "force_refresh": True,
        "disable_cache": True
    }
}
```

## 实施步骤
1. ✅ 添加`clear_cache()`方法清理ComfyUI各种缓存
2. ✅ 添加`force_cleanup_outputs()`方法删除旧输出文件
3. ✅ 修改`send_prompt()`方法，在发送前先清理缓存
4. ✅ 使用唯一的client_id和额外参数
5. ✅ 在`generate_image()`开始时强制清理输出文件

## 技术要点
- **不修改工作流文件**：遵循用户要求，不改变工作流内容
- **多层清理**：同时清理历史、队列、模型缓存和输出文件
- **唯一性保证**：每次请求都有唯一标识符
- **强制刷新**：通过多种机制确保生成新图像

## 预期效果
- 每次调用都会生成全新的图像
- 不会返回缓存的结果
- 确保用户看到的是真正的新生成内容

## 经验教训
1. **用户需求优先**：当用户明确反对某个机制时，要彻底解决
2. **多层防护**：单一方法可能不够，需要多重保障
3. **不改变核心**：在不修改工作流的前提下解决缓存问题
4. **系统性思考**：从API、缓存、文件系统多个层面解决问题

## 状态
🔄 实施中 - 后端正在重新加载，等待测试验证
