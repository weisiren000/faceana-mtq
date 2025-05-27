#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能依赖安装脚本
自动处理依赖冲突和兼容性问题
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """运行命令并处理错误"""
    print(f"🔄 {description}")
    print(f"执行: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} 成功")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误信息: {e.stderr}")
        return False, e.stderr

def check_pip_tool():
    """检查可用的pip工具"""
    tools = ['uv pip', 'pip']
    
    for tool in tools:
        try:
            result = subprocess.run(
                f"{tool} --version", 
                shell=True, 
                check=True, 
                capture_output=True
            )
            print(f"✅ 找到包管理工具: {tool}")
            return tool
        except subprocess.CalledProcessError:
            continue
    
    print("❌ 未找到可用的pip工具")
    return None

def install_with_strategy(pip_tool, strategy="main"):
    """使用不同策略安装依赖"""
    strategies = {
        "main": {
            "file": "requirements.txt",
            "description": "完整依赖安装"
        },
        "minimal": {
            "file": "requirements_minimal.txt", 
            "description": "最小依赖安装"
        },
        "individual": {
            "packages": [
                "flet>=0.21.0",
                "opencv-python>=4.8.0",
                "Pillow>=10.0.0", 
                "numpy>=1.26.0,<2.0.0",
                "requests>=2.31.0",
                "python-dotenv>=1.0.0",
                "psutil>=5.9.0"
            ],
            "description": "逐个安装核心包"
        }
    }
    
    if strategy == "individual":
        print(f"🚀 开始{strategies[strategy]['description']}...")
        for package in strategies[strategy]["packages"]:
            success, output = run_command(
                f"{pip_tool} install {package}",
                f"安装 {package}"
            )
            if not success:
                print(f"⚠️  {package} 安装失败，继续安装其他包...")
        return True
    else:
        req_file = strategies[strategy]["file"]
        if not Path(req_file).exists():
            print(f"❌ 依赖文件 {req_file} 不存在")
            return False
        
        print(f"🚀 开始{strategies[strategy]['description']}...")
        success, output = run_command(
            f"{pip_tool} install -r {req_file}",
            f"从 {req_file} 安装依赖"
        )
        return success

def upgrade_pip(pip_tool):
    """升级pip"""
    if "uv" in pip_tool:
        # uv不需要升级pip
        return True
    
    success, _ = run_command(
        f"{pip_tool} install --upgrade pip",
        "升级pip"
    )
    return success

def main():
    """主安装流程"""
    print("🚀 FaceAna-MTQ 依赖安装脚本")
    print("=" * 50)
    
    # 检查pip工具
    pip_tool = check_pip_tool()
    if not pip_tool:
        print("请先安装pip或uv")
        sys.exit(1)
    
    # 升级pip (如果需要)
    if "pip" in pip_tool:
        print("\n📦 升级pip...")
        upgrade_pip(pip_tool)
    
    # 尝试不同的安装策略
    strategies = ["main", "minimal", "individual"]
    
    for strategy in strategies:
        print(f"\n📋 尝试策略: {strategy}")
        print("-" * 30)
        
        success = install_with_strategy(pip_tool, strategy)
        
        if success:
            print(f"\n✅ 使用 {strategy} 策略安装成功!")
            break
        else:
            print(f"\n❌ {strategy} 策略失败，尝试下一个策略...")
    else:
        print("\n💥 所有安装策略都失败了!")
        print("\n🔧 手动安装建议:")
        print("1. 检查Python版本 (建议3.9+)")
        print("2. 更新pip: pip install --upgrade pip")
        print("3. 清理缓存: pip cache purge")
        print("4. 逐个安装核心包:")
        print("   pip install flet opencv-python numpy requests")
        sys.exit(1)
    
    # 验证安装
    print("\n🔍 验证安装...")
    if Path("check_installation.py").exists():
        success, output = run_command(
            "python check_installation.py",
            "运行安装验证"
        )
        if success:
            print("\n🎉 所有依赖安装完成并验证成功!")
            print("\n🚀 现在可以运行:")
            print("   python run_gui.py")
        else:
            print("\n⚠️  安装完成但验证失败，请检查具体问题")
    else:
        print("\n✅ 依赖安装完成!")
        print("请运行 python run_gui.py 启动应用")

if __name__ == "__main__":
    main()
