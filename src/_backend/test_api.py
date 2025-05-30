"""
测试EmoScan API的情绪分析功能
"""

import requests
import json
from pathlib import Path

def test_emotion_analysis():
    """测试情绪分析API"""
    
    # API端点
    url = "http://localhost:8000/api/v1/analyze/image"
    
    # 测试图像路径
    image_path = Path("../../test/image/test_img.png")
    
    if not image_path.exists():
        print(f"❌ 测试图像不存在: {image_path}")
        return
    
    print(f"测试情绪分析API...")
    print(f"使用图像: {image_path}")
    
    try:
        # 读取图像文件
        with open(image_path, "rb") as f:
            files = {"file": ("test_img.png", f, "image/png")}
            
            # 发送请求
            response = requests.post(url, files=files, timeout=60)
            
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功!")
            print(f"📊 分析结果:")
            print(f"   成功: {result['success']}")
            
            if result['success']:
                print(f"   情绪数据:")
                for emotion in result['emotion_data']:
                    print(f"     {emotion['emotion']}: {emotion['percentage']:.1f}%")
                
                print(f"\n📝 AI分析报告:")
                print(result['analysis_text'][:200] + "..." if len(result['analysis_text']) > 200 else result['analysis_text'])
            else:
                print(f"   错误信息: {result.get('error_message', '未知错误')}")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_health_check():
    """测试健康检查API"""
    print("🏥 测试健康检查API...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查通过!")
            print(f"   状态: {result['status']}")
            print(f"   服务: {result['service']}")
            print(f"   版本: {result['version']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

if __name__ == "__main__":
    print("开始测试EmoScan API...")
    print("=" * 50)

    # 测试健康检查
    test_health_check()
    print()

    # 测试情绪分析
    test_emotion_analysis()

    print("=" * 50)
    print("测试完成!")