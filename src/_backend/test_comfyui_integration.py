#!/usr/bin/env python3
"""
ComfyUI集成测试脚本
测试后端ComfyUI服务的各项功能
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from app.services.comfyui_service import ComfyUIService
from app.models.comfyui import GenerationRequest


async def test_comfyui_integration():
    """测试ComfyUI集成功能"""
    print("🚀 ComfyUI集成测试开始")
    print("=" * 60)
    
    # 创建服务实例
    service = ComfyUIService()
    
    # 1. 测试服务状态
    print("\n1. 测试ComfyUI服务状态...")
    status = await service.check_status()
    print(f"   服务可用: {status.available}")
    if status.available:
        print(f"   运行队列: {status.queue_running}")
        print(f"   等待队列: {status.queue_pending}")
        if status.system_stats:
            print(f"   系统状态: {json.dumps(status.system_stats, indent=2)}")
    else:
        print(f"   错误信息: {status.error_message}")
        print("\n❌ ComfyUI服务不可用，请确保：")
        print("   1. ComfyUI正在运行")
        print("   2. 端口8188可访问")
        print("   3. 没有防火墙阻止连接")
        return
    
    # 2. 测试工作流列表
    print("\n2. 测试工作流列表...")
    workflows = await service.list_workflows()
    print(f"   找到 {len(workflows)} 个工作流:")
    for workflow in workflows:
        status_icon = "✅" if workflow.exists else "❌"
        print(f"   {status_icon} {workflow.name} ({workflow.emotion}) - {workflow.path}")
    
    # 3. 测试加载工作流
    print("\n3. 测试加载工作流...")
    test_emotions = ["happy", "sad", "angry"]
    
    for emotion in test_emotions:
        workflow = await service.load_workflow(emotion)
        if workflow:
            print(f"   ✅ 成功加载 {emotion} 工作流")
            # 显示工作流的基本信息
            node_count = len(workflow)
            print(f"      节点数量: {node_count}")
        else:
            print(f"   ❌ 加载 {emotion} 工作流失败")
    
    # 4. 测试图像生成（如果有可用的工作流）
    available_workflows = [w for w in workflows if w.exists and w.emotion != "default"]
    
    if available_workflows:
        print("\n4. 测试图像生成...")
        test_emotion = available_workflows[0].emotion
        print(f"   使用情绪: {test_emotion}")
        
        # 创建生成请求
        request = GenerationRequest(
            emotion=test_emotion,
            seed=12345  # 使用固定种子便于测试
        )
        
        print("   开始生成图像...")
        result = await service.generate_image(request)
        
        if result.success:
            print(f"   ✅ 图像生成成功!")
            print(f"      提示ID: {result.prompt_id}")
            print(f"      生成时间: {result.generation_time:.2f}秒")
            print(f"      图像数量: {len(result.images or [])}")
            
            if result.images:
                for i, img in enumerate(result.images, 1):
                    print(f"      图像{i}: {img.filename}")
                    print(f"              URL: {img.url}")
        else:
            print(f"   ❌ 图像生成失败: {result.error_message}")
    else:
        print("\n4. 跳过图像生成测试 - 没有可用的工作流")
    
    print("\n" + "=" * 60)
    print("✨ ComfyUI集成测试完成")


async def test_emotion_mapping():
    """测试情绪映射功能"""
    print("\n🧠 测试情绪映射...")
    
    from app.models.comfyui import get_workflow_filename, validate_emotion
    
    test_emotions = ["happy", "sad", "angry", "surprised", "neutral", "disgusted", "fearful", "invalid"]
    
    for emotion in test_emotions:
        is_valid = validate_emotion(emotion)
        workflow_file = get_workflow_filename(emotion)
        status_icon = "✅" if is_valid else "❌"
        print(f"   {status_icon} {emotion} -> {workflow_file} (有效: {is_valid})")


async def main():
    """主测试函数"""
    try:
        await test_comfyui_integration()
        await test_emotion_mapping()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
