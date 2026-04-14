"""
健康检查API
基于 05-用户故事与验收标准.md US-004
基于 09-API接口规格.md
"""
from fastapi import APIRouter
from datetime import datetime

from app.database import get_redis
from app.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["健康检查"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查
    AC-004-01: 系统健康检查接口返回正常状态
    AC-004-02: 依赖服务不可用时返回降级状态
    """
    dependencies = {}
    all_healthy = True
    
    # 检查MySQL
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        dependencies["mysql"] = "up"
    except Exception:
        dependencies["mysql"] = "down"
        all_healthy = False
    
    # 检查Redis
    try:
        redis_client = get_redis()
        if redis_client:
            redis_client.ping()
            dependencies["redis"] = "up"
        else:
            dependencies["redis"] = "down"
            all_healthy = False
    except Exception:
        dependencies["redis"] = "down"
        all_healthy = False
    
    # 检查Milvus（可选）
    dependencies["milvus"] = "unknown"
    
    # 检查LLM
    from app.config import settings
    dependencies["llm"] = "up" if settings.OPENAI_API_KEY else "down"
    
    # 确定状态
    if all_healthy:
        status = "healthy"
    elif dependencies["mysql"] == "up":
        status = "degraded"
    else:
        status = "unhealthy"
    
    return HealthResponse(
        status=status,
        dependencies=dependencies
    )
