from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base

app = FastAPI(title="投研问答助手 API", version="0.1.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # 导入所有模型以确保 create_all 能创建表
    from app.models import User, Session, Message
    Base.metadata.create_all(bind=engine)
    
    # 创建默认用户（MVP 用）
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(User).first():
            default_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password="default_hash"
            )
            db.add(default_user)
            db.commit()
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "投研问答助手 API", "version": "0.1.0"}
