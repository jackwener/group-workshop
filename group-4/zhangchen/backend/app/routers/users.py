from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, ContestParticipant, Contest
from app.schemas import User as UserSchema, UserUpdate, UserProfile
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/profile", response_model=UserSchema)
def get_profile(current_user: User = Depends(get_current_active_user)):
    """获取用户资料"""
    return current_user


@router.put("/profile", response_model=UserSchema)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    if user_update.nickname is not None:
        current_user.nickname = user_update.nickname
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/statistics", response_model=UserProfile)
def get_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户统计数据"""
    # 统计参加的比赛数量
    total_contests = db.query(ContestParticipant).filter(
        ContestParticipant.user_id == current_user.id
    ).count()
    
    # 统计活跃的比赛数量
    active_contests = db.query(ContestParticipant).join(Contest).filter(
        ContestParticipant.user_id == current_user.id,
        Contest.status == "active"
    ).count()
    
    # 计算总收益率（所有比赛的平均）
    avg_return = db.query(func.avg(ContestParticipant.total_return)).filter(
        ContestParticipant.user_id == current_user.id
    ).scalar() or 0.0
    
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        total_contests=total_contests,
        active_contests=active_contests,
        total_return=float(avg_return)
    )
