"""
投研问答助手 - WSGI 入口
模块编号: M1-QA
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app

# 创建应用实例
application = create_app()

if __name__ == "__main__":
    # 开发服务器配置
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    application.run(host="0.0.0.0", port=port, debug=debug)
