#!/usr/bin/env python3
"""
后端服务启动脚本
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50, flush=True)
    print("投研智能问答助手 - 后端服务", flush=True)
    print("=" * 50, flush=True)
    print("API 地址: http://localhost:5000/api/v1/agent", flush=True)
    print("=" * 50, flush=True)
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
