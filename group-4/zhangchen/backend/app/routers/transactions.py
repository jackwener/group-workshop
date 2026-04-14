from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models import User, Transaction, Fund
from app.schemas import TransactionWithFund, TransactionSummary
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/transactions", tags=["交易记录"])


@router.get("", response_model=List[TransactionWithFund])
def get_transactions(
    contest_id: Optional[int] = None,
    fund_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取交易记录列表"""
    query = db.query(Transaction, Fund).join(Fund, Transaction.fund_id == Fund.id).filter(
        Transaction.user_id == current_user.id
    )
    
    # 应用筛选条件
    if contest_id:
        query = query.filter(Transaction.contest_id == contest_id)
    if fund_id:
        query = query.filter(Transaction.fund_id == fund_id)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    transactions = query.order_by(desc(Transaction.transaction_date)).offset(skip).limit(limit).all()
    
    result = []
    for transaction, fund in transactions:
        result.append(TransactionWithFund(
            id=transaction.id,
            user_id=transaction.user_id,
            contest_id=transaction.contest_id,
            fund_id=transaction.fund_id,
            transaction_type=transaction.transaction_type,
            shares=transaction.shares,
            nav=transaction.nav,
            amount=transaction.amount,
            fee=transaction.fee,
            transaction_date=transaction.transaction_date,
            fund_name=fund.name,
            fund_code=fund.code
        ))
    
    return result


@router.get("/summary", response_model=TransactionSummary)
def get_transaction_summary(
    contest_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取交易汇总统计"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if contest_id:
        query = query.filter(Transaction.contest_id == contest_id)
    
    # 统计买入总额
    total_buy = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "buy"
    )
    if contest_id:
        total_buy = total_buy.filter(Transaction.contest_id == contest_id)
    total_buy = total_buy.scalar() or 0
    
    # 统计卖出总额
    total_sell = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "sell"
    )
    if contest_id:
        total_sell = total_sell.filter(Transaction.contest_id == contest_id)
    total_sell = total_sell.scalar() or 0
    
    # 统计手续费
    total_fee = db.query(func.sum(Transaction.fee)).filter(
        Transaction.user_id == current_user.id
    )
    if contest_id:
        total_fee = total_fee.filter(Transaction.contest_id == contest_id)
    total_fee = total_fee.scalar() or 0
    
    # 统计交易次数
    transaction_count = query.count()
    
    return TransactionSummary(
        total_buy=total_buy,
        total_sell=total_sell,
        total_fee=total_fee,
        transaction_count=transaction_count
    )


@router.get("/recent")
def get_recent_transactions(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取最近交易记录"""
    start_date = datetime.now() - timedelta(days=days)
    
    transactions = db.query(Transaction, Fund).join(Fund, Transaction.fund_id == Fund.id).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= start_date
    ).order_by(desc(Transaction.transaction_date)).limit(10).all()
    
    result = []
    for transaction, fund in transactions:
        result.append({
            "id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "fund_code": fund.code,
            "fund_name": fund.name,
            "shares": float(transaction.shares),
            "nav": float(transaction.nav),
            "amount": float(transaction.amount),
            "fee": float(transaction.fee),
            "transaction_date": transaction.transaction_date.isoformat()
        })
    
    return result
