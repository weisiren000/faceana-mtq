#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入脚本
检查各个模块是否可以正常导入
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_import(module_path, description):
    """测试单个模块导入"""
    try:
        __import__(module_path)
        print(f"✅ {description}: {module_path}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_path}")
        print(f"   错误: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: {module_path}")
        print(f"   其他错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 测试模块导入...")
    print("=" * 50)
    
    # 测试基础模块
    tests = [
        ("src._backend.config", "配置模块"),
        ("src._backend.config_performance", "性能配置模块"),
        ("src._backend.core.caller", "工作流调用模块"),
        ("src._backend.app.components.camera_preview", "摄像头预览组件"),
        ("src._backend.app.components.emotion_chart", "情绪图表组件"),
        ("src._backend.app.components.agent_progress", "智能体进度组件"),
        ("src._backend.app.components.llm_output", "LLM输出组件"),
        ("src._backend.app.components.confidence_display", "置信度显示组件"),
        ("src._backend.app.views.main_view", "主视图"),
        ("src._backend.app.main", "主应用"),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for module_path, description in tests:
        if test_import(module_path, description):
            success_count += 1
    
    print("=" * 50)
    print(f"导入测试结果: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ 所有模块导入成功!")
        
        # 测试GUI应用启动
        print("\n🚀 测试GUI应用启动...")
        try:
            from src._backend.app.main import main as app_main
            print("✅ GUI应用模块导入成功!")
            print("注意: 实际启动需要显示环境，这里只测试导入")
            return True
        except Exception as e:
            print(f"❌ GUI应用启动测试失败: {e}")
            return False
    else:
        print("❌ 存在导入失败的模块，请检查依赖和文件结构")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
