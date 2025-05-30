"""
测试批量分析API的功能
"""

import requests
import json
from pathlib import Path

def test_batch_emotion_analysis():
    """测试批量情绪分析API"""
    
    # API端点
    url = "http://localhost:8000/api/v1/analyze/batch"
    
    # 测试图像路径
    image_path = Path("../../test/image/test_img.png")
    
    if not image_path.exists():
        print(f"❌ 测试图像不存在: {image_path}")
        return
    
    print(f"测试批量情绪分析API...")
    print(f"使用图像: {image_path}")
    
    try:
        # 准备多个文件（使用同一张图片模拟5张图片）
        files = []
        for i in range(3):  # 测试3张图片
            with open(image_path, "rb") as f:
                files.append(("files", (f"test_img_{i+1}.png", f.read(), "image/png")))
        
        # 发送请求
        response = requests.post(url, files=files, timeout=120)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            print("✅ 批量API调用成功!")
            print(f"📊 分析结果:")
            print(f"   成功: {result['success']}")
            
            if result['success']:
                print(f"   情绪数据:")
                for emotion in result['emotion_data']:
                    print(f"     {emotion['emotion']}: {emotion['percentage']:.1f}%")
                
                print(f"\n📝 AI分析报告:")
                analysis_text = result['analysis_text']
                # 只显示前500个字符
                if len(analysis_text) > 500:
                    print(analysis_text[:500] + "...")
                else:
                    print(analysis_text)
                
                print(f"\n🔍 详细结果:")
                for detail in result.get('detailed_results', []):
                    image_id = detail['image_id']
                    print(f"   图像 {image_id}:")
                    if detail.get('facepp_result'):
                        facepp = detail['facepp_result']
                        print(f"     Face++: {facepp['dominant_emotion']} ({facepp['confidence']:.2f})")
                    if detail.get('gemini_result'):
                        gemini = detail['gemini_result']
                        print(f"     Gemini: {gemini['dominant_emotion']} ({gemini['confidence']:.2f})")
                
                print(f"\n⚖️ 裁判员AI判断:")
                judge = result.get('judge_result')
                if judge:
                    print(f"   最终情绪: {judge.get('final_emotion', 'unknown')}")
                    print(f"   置信度: {judge.get('confidence', 0):.2f}")
                    print(f"   判断依据: {judge.get('reasoning', '无')}")
                else:
                    print("   裁判员AI未返回结果")
                    
            else:
                print(f"   错误信息: {result.get('error_message', '未知错误')}")
                
        else:
            print(f"❌ 批量API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端服务正常运行")
            print(f"   状态: {data['status']}")
            print(f"   服务: {data['service']}")
            print(f"   版本: {data['version']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")

if __name__ == "__main__":
    print("🧪 开始测试批量分析API...")
    print("=" * 50)
    
    # 先检查服务状态
    test_health_check()
    print()
    
    # 测试批量分析
    test_batch_emotion_analysis()
    
    print("=" * 50)
    print("🏁 测试完成!")
