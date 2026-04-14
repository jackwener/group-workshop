from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models import Contest, ContestParticipant, User
from app.schemas import (
    Contest as ContestSchema, ContestCreate, ContestUpdate, 
    ContestDetail, ContestParticipant as ContestParticipantSchema,
    ContestParticipantWithUser
)
from app.routers.auth import get_current_active_user
from app.config import get_settings

router = APIRouter(prefix="/contests", tags=["比赛"])
settings = get_settings()


@router.get("", response_model=List[ContestSchema])
def get_contests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取比赛列表"""
    query = db.query(Contest)
    
    if status:
        query = query.filter(Contest.status == status)
    
    contests = query.order_by(desc(Contest.created_at)).offset(skip).limit(limit).all()
    return contests


@router.post("", response_model=ContestSchema, status_code=201)
def create_contest(
    contest_data: ContestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建比赛"""
    # 设置默认开始和结束时间
    start_date = contest_data.start_date or datetime.now()
    end_date = contest_data.end_date or (start_date + timedelta(days=settings.DEFAULT_CONTEST_DAYS))
    
    db_contest = Contest(
        name=contest_data.name,
        description=contest_data.description,
        initial_balance=contest_data.initial_balance or settings.DEFAULT_INITIAL_BALANCE,
        start_date=start_date,
        end_date=end_date,
        rules=contest_data.rules,
        created_by=current_user.id,
        status="pending"
    )
    
    db.add(db_contest)
    db.commit()
    db.refresh(db_contest)
    
    return db_contest


@router.get("/{contest_id}", response_model=ContestDetail)
def get_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取比赛详情"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 统计参赛人数
    participant_count = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id
    ).count()
    
    # 检查当前用户是否已参加
    my_participation = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    return ContestDetail(
        id=contest.id,
        name=contest.name,
        description=contest.description,
        initial_balance=contest.initial_balance,
        start_date=contest.start_date,
        end_date=contest.end_date,
        status=contest.status,
        rules=contest.rules,
        created_by=contest.created_by,
        created_at=contest.created_at,
        participant_count=participant_count,
        is_participating=my_participation is not None,
        my_rank=my_participation.rank if my_participation else None
    )


@router.put("/{contest_id}", response_model=ContestSchema)
def update_contest(
    contest_id: int,
    contest_update: ContestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新比赛"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 检查权限（只有创建者可以修改）
    if contest.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此比赛")
    
    # 更新字段
    if contest_update.name:
        contest.name = contest_update.name
    if contest_update.description is not None:
        contest.description = contest_update.description
    if contest_update.start_date:
        contest.start_date = contest_update.start_date
    if contest_update.end_date:
        contest.end_date = contest_update.end_date
    if contest_update.status:
        contest.status = contest_update.status
    if contest_update.rules is not None:
        contest.rules = contest_update.rules
    
    db.commit()
    db.refresh(contest)
    return contest


@router.delete("/{contest_id}")
def delete_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除比赛"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 检查权限
    if contest.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此比赛")
    
    db.delete(contest)
    db.commit()
    
    return {"message": "比赛已删除"}


@router.post("/{contest_id}/join", response_model=ContestParticipantSchema)
def join_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """参加比赛"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 检查比赛状态
    if contest.status == "ended":
        raise HTTPException(status_code=400, detail="比赛已结束")
    
    # 检查是否已参加
    existing = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="您已参加此比赛")
    
    # 创建参赛记录
    participant = ContestParticipant(
        contest_id=contest_id,
        user_id=current_user.id,
        current_balance=contest.initial_balance,
        total_assets=contest.initial_balance,
        total_return=0,
        rank=None
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    return participant


@router.get("/{contest_id}/participants", response_model=List[ContestParticipantWithUser])
def get_contest_participants(
    contest_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取比赛参与者列表"""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    participants = db.query(ContestParticipant, User).join(
        User, ContestParticipant.user_id == User.id
    ).filter(
        ContestParticipant.contest_id == contest_id
    ).order_by(
        ContestParticipant.rank
    ).offset(skip).limit(limit).all()
    
    result = []
    for participant, user in participants:
        result.append(ContestParticipantWithUser(
            id=participant.id,
            contest_id=participant.contest_id,
            user_id=participant.user_id,
            current_balance=participant.current_balance,
            total_assets=participant.total_assets,
            total_return=participant.total_return,
            rank=participant.rank,
            joined_at=participant.joined_at,
            username=user.username,
            nickname=user.nickname
        ))
    
    return result


@router.get("/{contest_id}/me", response_model=ContestParticipantSchema)
def get_my_contest_data(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的比赛数据"""
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="您未参加此比赛")
    
    return participant
