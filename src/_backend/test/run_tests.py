#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试执行和报告功能
"""

import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """检查测试依赖"""
    required_packages = ['pytest', 'numpy', 'opencv-python', 'pillow']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.info("请运行: pip install " + " ".join(missing_packages))
        return False

    return True


def run_unit_tests(verbose=False, coverage=False):
    """运行单元测试"""
    logger.info("开始运行单元测试...")

    test_dir = Path(__file__).parent
    cmd = ['python', '-m', 'pytest', str(test_dir)]

    if verbose:
        cmd.append('-v')

    if coverage:
        cmd.extend(['--cov=src._backend', '--cov-report=html', '--cov-report=term'])

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("单元测试通过 ✅")
            if verbose:
                print(result.stdout)
        else:
            logger.error("单元测试失败 ❌")
            print(result.stdout)
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        logger.error(f"运行测试时出错: {e}")
        return False


def run_specific_test(test_file, test_function=None, verbose=False):
    """运行特定测试"""
    logger.info(f"运行测试: {test_file}")

    test_path = Path(__file__).parent / test_file
    if not test_path.exists():
        logger.error(f"测试文件不存在: {test_path}")
        return False

    cmd = ['python', '-m', 'pytest', str(test_path)]

    if test_function:
        cmd.append(f"::{test_function}")

    if verbose:
        cmd.append('-v')

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"测试 {test_file} 通过 ✅")
        else:
            logger.error(f"测试 {test_file} 失败 ❌")

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        logger.error(f"运行测试时出错: {e}")
        return False


def run_integration_tests(verbose=False):
    """运行集成测试"""
    logger.info("开始运行集成测试...")

    test_dir = Path(__file__).parent
    cmd = ['python', '-m', 'pytest', str(test_dir), '-m', 'integration']

    if verbose:
        cmd.append('-v')

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("集成测试通过 ✅")
        else:
            logger.error("集成测试失败 ❌")

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        logger.error(f"运行集成测试时出错: {e}")
        return False


def generate_test_report():
    """生成测试报告"""
    logger.info("生成测试报告...")

    test_dir = Path(__file__).parent
    report_dir = project_root / "test_reports"
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"test_report_{timestamp}.html"

    cmd = [
        'python', '-m', 'pytest', str(test_dir),
        '--html', str(report_file),
        '--self-contained-html',
        '--cov=src._backend',
        '--cov-report=html:' + str(report_dir / f"coverage_{timestamp}")
    ]

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if report_file.exists():
            logger.info(f"测试报告已生成: {report_file}")
        else:
            logger.warning("测试报告生成失败")

        return result.returncode == 0

    except Exception as e:
        logger.error(f"生成测试报告时出错: {e}")
        return False


def run_quick_smoke_test():
    """运行快速冒烟测试"""
    logger.info("运行快速冒烟测试...")

    try:
        # 测试基本导入
        from src._backend.config import config
        from src._backend.utils.function.data_converter import image_to_base64
        from src._backend.utils.classpy.data_models import EmotionResult

        logger.info("✅ 基本导入测试通过")

        # 测试配置
        assert config.PROJECT_ROOT.exists()
        logger.info("✅ 配置测试通过")

        # 测试数据模型
        result = EmotionResult(
            agent="TEST",
            timestamp="2024-12-01T10:00:00",
            emotion_category="positive",
            dominant_emotion="happiness",
            polarity_score=0.8,
            confidence=0.9,
            intensity="high",
            reliability="high",
            summary="测试"
        )
        assert result.is_positive()
        logger.info("✅ 数据模型测试通过")

        logger.info("🎉 快速冒烟测试全部通过")
        return True

    except Exception as e:
        logger.error(f"冒烟测试失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="FaceAna-MTQ 测试运行器")
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--smoke', action='store_true', help='运行快速冒烟测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--file', type=str, help='运行特定测试文件')
    parser.add_argument('--function', type=str, help='运行特定测试函数')
    parser.add_argument('--report', action='store_true', help='生成测试报告')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--check-deps', action='store_true', help='检查依赖')

    args = parser.parse_args()

    # 检查依赖
    if args.check_deps or not check_dependencies():
        if not check_dependencies():
            return 1
        else:
            logger.info("所有依赖都已安装 ✅")
            return 0

    success = True

    try:
        if args.smoke:
            success &= run_quick_smoke_test()

        elif args.unit:
            success &= run_unit_tests(verbose=args.verbose, coverage=args.coverage)

        elif args.integration:
            success &= run_integration_tests(verbose=args.verbose)

        elif args.file:
            success &= run_specific_test(args.file, args.function, verbose=args.verbose)

        elif args.report:
            success &= generate_test_report()

        elif args.all:
            logger.info("运行完整测试套件...")
            success &= run_quick_smoke_test()
            success &= run_unit_tests(verbose=args.verbose, coverage=args.coverage)
            success &= run_integration_tests(verbose=args.verbose)

            if success:
                logger.info("🎉 所有测试通过！")
            else:
                logger.error("❌ 部分测试失败")

        else:
            # 默认运行冒烟测试
            success &= run_quick_smoke_test()

    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        return 1
    except Exception as e:
        logger.error(f"运行测试时发生错误: {e}")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
