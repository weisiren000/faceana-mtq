#!/usr/bin/env python3
"""
EmoScan Flutter应用启动脚本
自动检查环境、安装依赖并启动Flutter桌面应用
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

class FlutterAppRunner:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.system = platform.system().lower()
        
    def check_flutter_installation(self):
        """检查Flutter是否已安装"""
        print("🔍 检查Flutter环境...")
        try:
            result = subprocess.run(['flutter', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Flutter已安装")
                print(f"   版本信息: {result.stdout.split()[1]}")
                return True
            else:
                print("❌ Flutter未正确安装")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ 未找到Flutter命令")
            return False
    
    def check_desktop_support(self):
        """检查桌面平台支持"""
        print("🖥️  检查桌面平台支持...")
        try:
            result = subprocess.run(['flutter', 'config'], 
                                  capture_output=True, text=True)
            output = result.stdout.lower()
            
            desktop_enabled = False
            if self.system == 'windows' and 'enable-windows-desktop: true' in output:
                desktop_enabled = True
            elif self.system == 'darwin' and 'enable-macos-desktop: true' in output:
                desktop_enabled = True
            elif self.system == 'linux' and 'enable-linux-desktop: true' in output:
                desktop_enabled = True
            
            if desktop_enabled:
                print(f"✅ {self.system.title()}桌面支持已启用")
                return True
            else:
                print(f"⚠️  {self.system.title()}桌面支持未启用，正在启用...")
                return self.enable_desktop_support()
        except subprocess.SubprocessError:
            print("❌ 无法检查桌面支持状态")
            return False
    
    def enable_desktop_support(self):
        """启用桌面平台支持"""
        try:
            if self.system == 'windows':
                cmd = ['flutter', 'config', '--enable-windows-desktop']
            elif self.system == 'darwin':
                cmd = ['flutter', 'config', '--enable-macos-desktop']
            elif self.system == 'linux':
                cmd = ['flutter', 'config', '--enable-linux-desktop']
            else:
                print(f"❌ 不支持的平台: {self.system}")
                return False
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {self.system.title()}桌面支持已启用")
                return True
            else:
                print(f"❌ 启用桌面支持失败: {result.stderr}")
                return False
        except subprocess.SubprocessError as e:
            print(f"❌ 启用桌面支持时出错: {e}")
            return False
    
    def install_dependencies(self):
        """安装Flutter依赖"""
        print("📦 安装Flutter依赖...")
        try:
            os.chdir(self.app_dir)
            result = subprocess.run(['flutter', 'pub', 'get'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 依赖安装完成")
                return True
            else:
                print(f"❌ 依赖安装失败: {result.stderr}")
                return False
        except subprocess.SubprocessError as e:
            print(f"❌ 安装依赖时出错: {e}")
            return False
    
    def get_target_platform(self):
        """获取目标平台"""
        if self.system == 'windows':
            return 'windows'
        elif self.system == 'darwin':
            return 'macos'
        elif self.system == 'linux':
            return 'linux'
        else:
            return None
    
    def run_app(self, debug=True):
        """运行Flutter应用"""
        target = self.get_target_platform()
        if not target:
            print(f"❌ 不支持的平台: {self.system}")
            return False
        
        print(f"🚀 启动EmoScan应用 ({target})...")
        try:
            os.chdir(self.app_dir)
            
            # 构建运行命令
            cmd = ['flutter', 'run', '-d', target]
            if not debug:
                cmd.append('--release')
            
            # 启动应用
            print(f"   执行命令: {' '.join(cmd)}")
            print("   请等待应用启动...")
            print("   按 Ctrl+C 停止应用")
            print("-" * 50)
            
            process = subprocess.Popen(cmd)
            process.wait()
            
            return True
        except KeyboardInterrupt:
            print("\n⏹️  应用已停止")
            return True
        except subprocess.SubprocessError as e:
            print(f"❌ 启动应用失败: {e}")
            return False
    
    def build_app(self):
        """构建发布版本"""
        target = self.get_target_platform()
        if not target:
            print(f"❌ 不支持的平台: {self.system}")
            return False
        
        print(f"🔨 构建发布版本 ({target})...")
        try:
            os.chdir(self.app_dir)
            result = subprocess.run(['flutter', 'build', target], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 构建完成")
                print(f"   输出目录: build/{target}/")
                return True
            else:
                print(f"❌ 构建失败: {result.stderr}")
                return False
        except subprocess.SubprocessError as e:
            print(f"❌ 构建时出错: {e}")
            return False
    
    def show_help(self):
        """显示帮助信息"""
        print("""
EmoScan Flutter应用启动器

用法:
    python run_flutter_app.py [选项]

选项:
    --help, -h      显示此帮助信息
    --build, -b     构建发布版本
    --release, -r   以发布模式运行
    --check, -c     仅检查环境，不启动应用

示例:
    python run_flutter_app.py              # 以调试模式运行
    python run_flutter_app.py --release    # 以发布模式运行
    python run_flutter_app.py --build      # 构建发布版本
    python run_flutter_app.py --check      # 检查环境
        """)
    
    def run(self):
        """主运行方法"""
        print("=" * 50)
        print("🎯 EmoScan Flutter应用启动器")
        print("=" * 50)
        
        # 解析命令行参数
        args = sys.argv[1:]
        
        if '--help' in args or '-h' in args:
            self.show_help()
            return
        
        # 检查环境
        if not self.check_flutter_installation():
            print("\n❌ 请先安装Flutter SDK")
            print("   下载地址: https://flutter.dev/docs/get-started/install")
            return
        
        if not self.check_desktop_support():
            print("\n❌ 桌面支持配置失败")
            return
        
        if not self.install_dependencies():
            print("\n❌ 依赖安装失败")
            return
        
        # 仅检查环境
        if '--check' in args or '-c' in args:
            print("\n✅ 环境检查完成，一切正常！")
            return
        
        # 构建应用
        if '--build' in args or '-b' in args:
            self.build_app()
            return
        
        # 运行应用
        debug_mode = not ('--release' in args or '-r' in args)
        mode_text = "调试" if debug_mode else "发布"
        print(f"\n🎮 以{mode_text}模式启动应用...")
        
        self.run_app(debug=debug_mode)

if __name__ == '__main__':
    runner = FlutterAppRunner()
    runner.run()
