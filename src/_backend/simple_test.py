# -*- coding: utf-8 -*-
"""
简单的API测试脚本
"""

import requests

def test_health():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root():
    """测试根端点"""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing EmoScan API...")
    print("-" * 30)
    
    # 测试根端点
    test_root()
    print()
    
    # 测试健康检查
    test_health()
    
    print("-" * 30)
    print("Test completed!")