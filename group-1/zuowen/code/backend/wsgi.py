"""
投研问答助手 — WSGI 入口
启动命令: python -m flask --app wsgi run --port 5000
"""
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
