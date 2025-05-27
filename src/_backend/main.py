"""
FaceAna-MTQ 后端主程序
提供命令行接口和程序入口点
"""

import argparse
import logging
import json
import sys
import signal
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from .config import config
from .core.caller import run_emotion_analysis, run_batch_emotion_analysis
from .core.cleaner import clean_all_files
from .robot.jsa import run_complete_emotion_analysis

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOGS_DIR / 'main.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class FaceAnalysisApp:
    """人脸情绪分析应用程序"""

    def __init__(self):
        """初始化应用程序"""
        self.running = True
        self.setup_signal_handlers()

        # 验证配置
        if not config.validate_config():
            logger.error("配置验证失败，请检查API密钥配置")
            sys.exit(1)

        logger.info("FaceAna-MTQ 后端程序启动")

    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"接收到信号 {signum}，正在优雅关闭...")
            self.running = False
            self.cleanup_and_exit()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def cleanup_and_exit(self):
        """清理资源并退出"""
        logger.info("正在清理资源...")
        try:
            # 清理临时文件
            clean_all_files(keep_splicer_final=True)
            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")

        logger.info("程序退出")
        sys.exit(0)

    def progress_callback(self, status: Dict):
        """进度回调函数"""
        current_step = status.get('current_step', '')
        progress = status.get('success_rate', 0)

        print(f"\r进度: {current_step} - {progress:.1f}%", end='', flush=True)

        if status.get('completed_steps', 0) == status.get('total_steps', 0):
            print()  # 换行

    def run_analysis(self, workflow_type: str = "complete", show_progress: bool = True) -> Dict:
        """运行情绪分析"""
        logger.info(f"开始运行 {workflow_type} 工作流程")

        progress_callback = self.progress_callback if show_progress else None

        try:
            result = run_emotion_analysis(workflow_type, progress_callback)

            if result.get('success', False):
                logger.info("分析完成")
                self.print_analysis_result(result)
            else:
                logger.error(f"分析失败: {result.get('error', '未知错误')}")

            return result

        except Exception as e:
            error_msg = f"分析过程中发生异常: {e}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def print_analysis_result(self, result: Dict):
        """打印分析结果"""
        print("\n" + "="*60)
        print("情绪分析结果")
        print("="*60)

        # 基本信息
        workflow_type = result.get('workflow_type', 'unknown')
        timestamp = result.get('timestamp', '')
        print(f"工作流类型: {workflow_type}")
        print(f"分析时间: {timestamp}")

        # 工作流摘要
        workflow_summary = result.get('workflow_summary', {})
        if workflow_summary:
            duration = workflow_summary.get('duration_seconds', 0)
            success_rate = workflow_summary.get('success_rate', 0)
            print(f"执行时长: {duration:.2f} 秒")
            print(f"成功率: {success_rate:.1f}%")

        # 最终判定结果
        final_result = result.get('final_result', {})
        if final_result:
            print("\n最终判定:")
            print(f"  情绪类别: {final_result.get('final_label', 'N/A')}")
            print(f"  主要情绪: {final_result.get('final_emotion', 'N/A')}")
            print(f"  情绪强度: {final_result.get('final_intensity_label', 'N/A')}")
            print(f"  可信度: {final_result.get('final_reliability_label', 'N/A')}")
            print(f"  极性分数: {final_result.get('final_polarity', 0):.3f}")
            print(f"  置信度: {final_result.get('adjusted_confidence', 0):.3f}")

            summary = final_result.get('summary', '')
            if summary:
                print(f"\n摘要: {summary}")

        # 摘要文本
        summary_text = result.get('summary_text', '')
        if summary_text and summary_text != final_result.get('summary', ''):
            print(f"\n总结: {summary_text}")

        print("="*60)

    def interactive_mode(self):
        """交互模式"""
        print("\n欢迎使用 FaceAna-MTQ 人脸情绪分析系统")
        print("交互模式 - 输入 'help' 查看帮助，输入 'quit' 退出")

        while self.running:
            try:
                command = input("\nfaceana> ").strip().lower()

                if command == 'quit' or command == 'exit':
                    break
                elif command == 'help':
                    self.print_help()
                elif command == 'analyze' or command == 'run':
                    self.run_analysis()
                elif command == 'basic':
                    self.run_analysis('basic')
                elif command == 'analysis':
                    self.run_analysis('analysis')
                elif command == 'clean':
                    self.clean_files()
                elif command == 'status':
                    self.show_status()
                elif command == '':
                    continue
                else:
                    print(f"未知命令: {command}，输入 'help' 查看帮助")

            except KeyboardInterrupt:
                print("\n使用 'quit' 命令退出")
            except EOFError:
                break

        self.cleanup_and_exit()

    def print_help(self):
        """打印帮助信息"""
        help_text = """
可用命令:
  analyze, run  - 运行完整的情绪分析流程
  basic         - 运行基础流程（不包含AI分析）
  analysis      - 仅运行AI分析（需要已有图像）
  clean         - 清理临时文件
  status        - 显示系统状态
  help          - 显示此帮助信息
  quit, exit    - 退出程序
        """
        print(help_text)

    def clean_files(self):
        """清理文件"""
        print("正在清理临时文件...")
        try:
            result = clean_all_files(keep_splicer_final=True)
            total_cleaned = result.get('total', 0)
            print(f"清理完成，共删除 {total_cleaned} 个文件")
        except Exception as e:
            print(f"清理失败: {e}")

    def show_status(self):
        """显示系统状态"""
        print("\n系统状态:")
        print(f"  项目根目录: {config.PROJECT_ROOT}")
        print(f"  数据目录: {config.DATA_DIR}")
        print(f"  日志目录: {config.LOGS_DIR}")
        print(f"  配置有效: {'是' if config.validate_config() else '否'}")

        # 检查目录状态
        directories = [
            ('capture', config.CAPTURE_DIR),
            ('tagger', config.TAGGER_DIR),
            ('splicer', config.SPLICER_DIR),
            ('logs', config.LOGS_DIR)
        ]

        print("\n目录状态:")
        for name, path in directories:
            exists = path.exists()
            file_count = len(list(path.glob('*'))) if exists else 0
            print(f"  {name}: {'存在' if exists else '不存在'} ({file_count} 个文件)")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="FaceAna-MTQ 人脸情绪分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m src._backend.main                    # 交互模式
  python -m src._backend.main --analyze          # 运行完整分析
  python -m src._backend.main --basic            # 运行基础流程
  python -m src._backend.main --clean            # 清理临时文件
        """
    )

    # 工作流选项
    workflow_group = parser.add_mutually_exclusive_group()
    workflow_group.add_argument(
        '--analyze', '--run',
        action='store_true',
        help='运行完整的情绪分析流程'
    )
    workflow_group.add_argument(
        '--basic',
        action='store_true',
        help='运行基础流程（图像捕获、标注、拼接，不包含AI分析）'
    )
    workflow_group.add_argument(
        '--analysis',
        action='store_true',
        help='仅运行AI分析（需要已有图像文件）'
    )
    workflow_group.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='启动交互模式（默认）'
    )

    # 其他选项
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='不显示进度信息'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='清理临时文件'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='显示系统状态'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        app = FaceAnalysisApp()

        # 处理命令行参数
        if args.clean:
            app.clean_files()
        elif args.status:
            app.show_status()
        elif args.analyze:
            app.run_analysis("complete", not args.no_progress)
        elif args.basic:
            app.run_analysis("basic", not args.no_progress)
        elif args.analysis:
            app.run_analysis("analysis", not args.no_progress)
        else:
            # 默认启动交互模式
            app.interactive_mode()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行时发生错误: {e}")
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
