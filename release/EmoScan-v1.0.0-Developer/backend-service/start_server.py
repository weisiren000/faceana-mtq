"""
EmoScan后端服务器启动脚本
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"🚀 启动EmoScan API服务器...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔧 调试模式: {debug}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )