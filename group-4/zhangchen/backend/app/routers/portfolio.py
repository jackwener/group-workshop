from typing import List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models import User, Contest, ContestParticipant, Fund, FundPrice, Holding, Transaction
from app.schemas import HoldingWithFund
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/portfolio", tags=["投资组合"])


def get_latest_nav(db: Session, fund_id: int) -> Decimal:
    """获取基金最新净值"""
    latest_price = db.query(FundPrice).filter(
        FundPrice.fund_id == fund_id
    ).order_by(desc(FundPrice.date)).first()
    
    return latest_price.nav if latest_price else Decimal("0")


@router.get("/overview")
def get_portfolio_overview(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取投资组合概览"""
    # 验证比赛
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 获取参赛者信息
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="您未参加此比赛")
    
    # 获取持仓
    holdings = db.query(Holding, Fund).join(Fund, Holding.fund_id == Fund.id).filter(
        Holding.user_id == current_user.id,
        Holding.contest_id == contest_id,
        Holding.shares > 0
    ).all()
    
    # 计算持仓市值
    total_market_value = Decimal("0")
    total_cost = Decimal("0")
    holding_list = []
    
    for holding, fund in holdings:
        latest_nav = get_latest_nav(db, holding.fund_id)
        market_value = holding.shares * latest_nav
        cost = holding.shares * holding.avg_cost
        profit_loss = market_value - cost
        return_rate = (profit_loss / cost * 100) if cost > 0 else Decimal("0")
        
        total_market_value += market_value
        total_cost += cost
        
        holding_list.append({
            "fund_id": holding.fund_id,
            "fund_code": fund.code,
            "fund_name": fund.name,
            "fund_type": fund.type,
            "shares": float(holding.shares),
            "avg_cost": float(holding.avg_cost),
            "current_nav": float(latest_nav),
            "market_value": float(market_value),
            "profit_loss": float(profit_loss),
            "return_rate": float(return_rate),
        })
    
    # 计算总资产和收益率
    total_assets = participant.current_balance + total_market_value
    total_profit_loss = total_market_value - total_cost
    total_return_rate = (total_profit_loss / total_cost * 100) if total_cost > 0 else Decimal("0")
    
    return {
        "contest_id": contest_id,
        "contest_name": contest.name,
        "cash_balance": float(participant.current_balance),
        "market_value": float(total_market_value),
        "total_assets": float(total_assets),
        "total_profit_loss": float(total_profit_loss),
        "total_return_rate": float(total_return_rate),
        "rank": participant.rank,
        "holdings": holding_list,
        "holding_count": len(holding_list)
    }


@router.get("/holdings", response_model=List[HoldingWithFund])
def get_holdings(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取持仓列表"""
    holdings = db.query(Holding, Fund).join(Fund, Holding.fund_id == Fund.id).filter(
        Holding.user_id == current_user.id,
        Holding.contest_id == contest_id,
        Holding.shares > 0
    ).all()
    
    result = []
    for holding, fund in holdings:
        latest_nav = get_latest_nav(db, holding.fund_id)
        market_value = holding.shares * latest_nav
        profit_loss = market_value - (holding.shares * holding.avg_cost)
        return_rate = (profit_loss / (holding.shares * holding.avg_cost) * 100) if holding.avg_cost > 0 else Decimal("0")
        
        result.append(HoldingWithFund(
            id=holding.id,
            user_id=holding.user_id,
            contest_id=holding.contest_id,
            fund_id=holding.fund_id,
            shares=holding.shares,
            avg_cost=holding.avg_cost,
            current_nav=latest_nav,
            market_value=market_value,
            profit_loss=profit_loss,
            return_rate=return_rate,
            updated_at=holding.updated_at,
            fund_name=fund.name,
            fund_code=fund.code,
            fund_type=fund.type
        ))
    
    return result


@router.get("/profit")
def get_profit_curve(
    contest_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取收益曲线数据"""
    # 获取参赛者信息
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="您未参加此比赛")
    
    # 获取交易记录
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.contest_id == contest_id,
        Transaction.transaction_date >= start_date
    ).order_by(Transaction.transaction_date).all()
    
    # 生成每日收益数据（简化版，实际应该每日计算）
    dates = []
    daily_returns = []
    cumulative_returns = []
    
    current_date = start_date
    cumulative_return = 0.0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 只计算工作日
            dates.append(current_date.strftime("%Y-%m-%d"))
            # 模拟日收益（实际应该根据持仓计算）
            daily_return = float(participant.total_return) / days if days > 0 else 0
            daily_returns.append(round(daily_return, 4))
            cumulative_return += daily_return
            cumulative_returns.append(round(cumulative_return, 4))
        
        current_date += timedelta(days=1)
    
    return {
        "dates": dates,
        "daily_returns": daily_returns,
        "cumulative_returns": cumulative_returns,
        "total_return": float(participant.total_return)
    }


@router.get("/distribution")
def get_asset_distribution(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取资产配置分布"""
    # 获取参赛者信息
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="您未参加此比赛")
    
    # 获取持仓
    holdings = db.query(Holding, Fund).join(Fund, Holding.fund_id == Fund.id).filter(
        Holding.user_id == current_user.id,
        Holding.contest_id == contest_id,
        Holding.shares > 0
    ).all()
    
    # 按基金类型统计
    type_distribution = {}
    total_market_value = Decimal("0")
    
    for holding, fund in holdings:
        latest_nav = get_latest_nav(db, holding.fund_id)
        market_value = holding.shares * latest_nav
        total_market_value += market_value
        
        fund_type = fund.type or "其他"
        if fund_type not in type_distribution:
            type_distribution[fund_type] = Decimal("0")
        type_distribution[fund_type] += market_value
    
    # 计算比例
    total_assets = participant.current_balance + total_market_value
    
    distribution = []
    for fund_type, value in type_distribution.items():
        percentage = (value / total_assets * 100) if total_assets > 0 else 0
        distribution.append({
            "type": fund_type,
            "value": float(value),
            "percentage": round(float(percentage), 2)
        })
    
    # 添加现金
    cash_percentage = (participant.current_balance / total_assets * 100) if total_assets > 0 else 0
    distribution.append({
        "type": "现金",
        "value": float(participant.current_balance),
        "percentage": round(float(cash_percentage), 2)
    })
    
    return {
        "total_assets": float(total_assets),
        "distribution": distribution
    }


@router.get("/analysis")
def get_portfolio_analysis(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取投资分析报表"""
    # 获取参赛者信息
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="您未参加此比赛")
    
    # 统计交易数据
    total_buy = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.contest_id == contest_id,
        Transaction.transaction_type == "buy"
    ).scalar() or Decimal("0")
    
    total_sell = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.contest_id == contest_id,
        Transaction.transaction_type == "sell"
    ).scalar() or Decimal("0")
    
    total_fee = db.query(func.sum(Transaction.fee)).filter(
        Transaction.user_id == current_user.id,
        Transaction.contest_id == contest_id
    ).scalar() or Decimal("0")
    
    transaction_count = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.contest_id == contest_id
    ).count()
    
    # 获取持仓盈亏统计
    holdings = db.query(Holding).filter(
        Holding.user_id == current_user.id,
        Holding.contest_id == contest_id,
        Holding.shares > 0
    ).all()
    
    profit_count = sum(1 for h in holdings if h.profit_loss and h.profit_loss > 0)
    loss_count = sum(1 for h in holdings if h.profit_loss and h.profit_loss < 0)
    
    return {
        "total_buy": float(total_buy),
        "total_sell": float(total_sell),
        "total_fee": float(total_fee),
        "transaction_count": transaction_count,
        "current_rank": participant.rank,
        "total_return": float(participant.total_return),
        "profit_holdings": profit_count,
        "loss_holdings": loss_count,
        "win_rate": round(profit_count / (profit_count + loss_count) * 100, 2) if (profit_count + loss_count) > 0 else 0
    }
