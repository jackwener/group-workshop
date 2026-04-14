from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.dependencies import get_db
from app.schemas.common import BaseResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """详细健康检查"""
    components = {}
    
    # 检查数据库
    try:
        db.execute(text("SELECT 1"))
        components["database"] = "healthy"
    except Exception as e:
        components["database"] = f"unhealthy: {str(e)}"
    
    # LLM 服务状态（MVP 阶段未知）
    components["llm"] = "unknown"
    
    return {
        "status": "healthy" if all(v == "healthy" or v == "unknown" for v in components.values()) else "degraded",
        "components": components,
        "timestamp": datetime.utcnow().isoformat()
    }
