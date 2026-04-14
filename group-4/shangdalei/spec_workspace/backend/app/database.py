"""
数据库连接模块
基于 10-数据模型与存储规格.md
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# MySQL引擎
engine = create_engine(
    settings.mysql_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    from app.models import Session, QARecord
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表初始化完成")


# Redis客户端
redis_client = None


def get_redis():
    """获取Redis客户端"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            redis_client = None
    return redis_client
