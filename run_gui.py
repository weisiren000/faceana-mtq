#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmoScan GUI应用启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'flet',
        'opencv-python',
        'pillow',
        'numpy',
        'requests'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'pillow':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\n或者安装完整依赖:")
        print("pip install -r requirements.txt")
        return False

    return True

def setup_environment():
    """设置环境"""
    # 创建必要的目录
    directories = [
        'data/capture',
        'data/tagger',
        'data/splicer',
        'data/temp',
        'src/_backend/app/assests/images',
        'src/_backend/app/assests/fonts'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    # 设置环境变量
    os.environ.setdefault('FACEANA_ENV', 'development')
    os.environ.setdefault('FACEANA_LOG_LEVEL', 'INFO')

def main():
    """主函数"""
    print("🚀 启动EmoScan GUI应用...")

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 设置环境
    setup_environment()

    try:
        # 导入并启动应用
        from src._backend.app.main import main as app_main
        print("✅ 依赖检查通过，启动GUI...")
        app_main()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保项目结构正确且所有模块都存在")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
