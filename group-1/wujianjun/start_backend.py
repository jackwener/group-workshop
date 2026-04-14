#!/usr/bin/env python3
"""
后端服务启动脚本
"""
import sys
import os

# 切换到后端目录
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# 添加到路径
sys.path.insert(0, backend_dir)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 创建应用
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("投研智能问答助手 - 后端服务")
    print("=" * 50)
    print("API 地址: http://localhost:5000/api/v1/agent")
    print("=" * 50)
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False  # 避免重复启动
    )
