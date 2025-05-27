#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装验证脚本
检查所有依赖是否正确安装
"""

import sys
import importlib
from pathlib import Path

def check_package(package_name, import_name=None):
    """检查单个包是否安装"""
    if import_name is None:
        import_name = package_name

    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')
        return True, version
    except ImportError:
        return False, None

def main():
    """主检查函数"""
    print("🔍 检查FaceAna-MTQ项目依赖安装状态...\n")

    # 定义要检查的包
    packages = [
        # GUI框架
        ('flet', 'flet'),

        # 图像处理
        ('opencv-python', 'cv2'),
        ('Pillow', 'PIL'),
        ('numpy', 'numpy'),

        # HTTP请求
        ('requests', 'requests'),
        ('httpx', 'httpx'),
        ('aiohttp', 'aiohttp'),

        # AI API SDKs
        ('google-generativeai', 'google.generativeai'),
        ('anthropic', 'anthropic'),
        ('openai', 'openai'),

        # 数据处理
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),

        # 配置管理
        ('python-dotenv', 'dotenv'),
        ('pydantic', 'pydantic'),

        # 异步处理
        ('asyncio-mqtt', 'asyncio_mqtt'),

        # 系统监控
        ('psutil', 'psutil'),

        # 工具库
        ('tqdm', 'tqdm'),
        ('colorama', 'colorama'),

        # 开发测试
        ('pytest', 'pytest'),
        ('pytest-asyncio', 'pytest_asyncio'),
        ('black', 'black'),
        ('flake8', 'flake8'),
    ]

    installed_count = 0
    total_count = len(packages)
    failed_packages = []

    print("📦 核心依赖检查:")
    print("-" * 60)

    for package_name, import_name in packages:
        is_installed, version = check_package(package_name, import_name)

        if is_installed:
            status = "✅"
            installed_count += 1
            print(f"{status} {package_name:<25} {version}")
        else:
            status = "❌"
            failed_packages.append(package_name)
            print(f"{status} {package_name:<25} 未安装")

    print("-" * 60)
    print(f"安装状态: {installed_count}/{total_count} ({installed_count/total_count*100:.1f}%)")

    # 检查可选依赖
    print("\n🔧 可选依赖检查:")
    print("-" * 60)

    optional_packages = [
        ('opencv-contrib-python', 'cv2'),
        ('scikit-image', 'skimage'),
        ('scikit-learn', 'sklearn'),
    ]

    for package_name, import_name in optional_packages:
        is_installed, version = check_package(package_name, import_name)
        status = "✅" if is_installed else "⚪"
        version_str = version if is_installed else "未安装 (可选)"
        print(f"{status} {package_name:<25} {version_str}")

    # 检查项目结构
    print("\n📁 项目结构检查:")
    print("-" * 60)

    required_dirs = [
        'src/_backend',
        'src/_backend/app',
        'src/_backend/core',
        'src/_backend/api',
        'src/_backend/robot',
        'data',
    ]

    structure_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (缺失)")
            structure_ok = False

    # 总结
    print("\n" + "=" * 60)
    if failed_packages:
        print("❌ 安装检查失败!")
        print(f"缺失的包: {', '.join(failed_packages)}")
        print("\n请运行以下命令安装缺失的依赖:")
        print("pip install -r requirements.txt")
        return False
    elif not structure_ok:
        print("⚠️  项目结构不完整!")
        print("请确保所有必要的目录都存在")
        return False
    else:
        print("✅ 所有依赖安装完成，项目结构正常!")
        print("可以运行以下命令启动GUI应用:")
        print("python run_gui.py")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
