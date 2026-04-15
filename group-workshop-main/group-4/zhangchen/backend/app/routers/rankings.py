from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models import Contest, ContestParticipant, User
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/rankings", tags=["排行榜"])


@router.get("")
def get_global_rankings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取总排行榜"""
    # 获取所有参赛者的总收益排名
    rankings = db.query(
        ContestParticipant,
        User.username,
        User.nickname,
        Contest.name.label("contest_name")
    ).join(
        User, ContestParticipant.user_id == User.id
    ).join(
        Contest, ContestParticipant.contest_id == Contest.id
    ).order_by(
        desc(ContestParticipant.total_return)
    ).offset(skip).limit(limit).all()
    
    result = []
    for idx, (participant, username, nickname, contest_name) in enumerate(rankings, start=skip+1):
        result.append({
            "rank": idx,
            "user_id": participant.user_id,
            "username": username,
            "nickname": nickname,
            "contest_id": participant.contest_id,
            "contest_name": contest_name,
            "total_assets": float(participant.total_assets),
            "total_return": float(participant.total_return),
        })
    
    return result


@router.get("/{contest_id}")
def get_contest_rankings(
    contest_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定比赛排行榜"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 获取比赛内的排名
    rankings = db.query(
        ContestParticipant,
        User.username,
        User.nickname
    ).join(
        User, ContestParticipant.user_id == User.id
    ).filter(
        ContestParticipant.contest_id == contest_id
    ).order_by(
        desc(ContestParticipant.total_return)
    ).offset(skip).limit(limit).all()
    
    result = []
    for idx, (participant, username, nickname) in enumerate(rankings, start=skip+1):
        result.append({
            "rank": idx,
            "user_id": participant.user_id,
            "username": username,
            "nickname": nickname,
            "total_assets": float(participant.total_assets),
            "total_return": float(participant.total_return),
            "is_me": participant.user_id == current_user.id
        })
    
    return {
        "contest_id": contest_id,
        "contest_name": contest.name,
        "rankings": result,
        "my_rank": next((r["rank"] for r in result if r["is_me"]), None)
    }


@router.get("/{contest_id}/daily")
def get_daily_rankings(
    contest_id: int,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取日收益排行"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 获取参赛者列表（实际应该计算日收益，这里简化处理）
    rankings = db.query(
        ContestParticipant,
        User.username,
        User.nickname
    ).join(
        User, ContestParticipant.user_id == User.id
    ).filter(
        ContestParticipant.contest_id == contest_id
    ).order_by(
        desc(ContestParticipant.total_return)
    ).limit(20).all()
    
    result = []
    for idx, (participant, username, nickname) in enumerate(rankings, start=1):
        # 模拟日收益（实际应该根据前一日数据计算）
        daily_return = float(participant.total_return) / 30  # 简化计算
        
        result.append({
            "rank": idx,
            "user_id": participant.user_id,
            "username": username,
            "nickname": nickname,
            "daily_return": round(daily_return, 4),
            "is_me": participant.user_id == current_user.id
        })
    
    return {
        "contest_id": contest_id,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "rankings": result
    }


@router.get("/{contest_id}/weekly")
def get_weekly_rankings(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取周收益排行"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 获取参赛者列表
    rankings = db.query(
        ContestParticipant,
        User.username,
        User.nickname
    ).join(
        User, ContestParticipant.user_id == User.id
    ).filter(
        ContestParticipant.contest_id == contest_id
    ).order_by(
        desc(ContestParticipant.total_return)
    ).limit(20).all()
    
    result = []
    for idx, (participant, username, nickname) in enumerate(rankings, start=1):
        # 模拟周收益
        weekly_return = float(participant.total_return) / 4  # 简化计算
        
        result.append({
            "rank": idx,
            "user_id": participant.user_id,
            "username": username,
            "nickname": nickname,
            "weekly_return": round(weekly_return, 4),
            "is_me": participant.user_id == current_user.id
        })
    
    return {
        "contest_id": contest_id,
        "rankings": result
    }


@router.post("/update/{contest_id}")
def update_rankings(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新比赛排名（手动触发）"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 获取所有参赛者并按收益率排序
    participants = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id
    ).order_by(desc(ContestParticipant.total_return)).all()
    
    # 更新排名
    for idx, participant in enumerate(participants, start=1):
        participant.rank = idx
    
    db.commit()
    
    return {"message": "排名更新成功", "participant_count": len(participants)}
