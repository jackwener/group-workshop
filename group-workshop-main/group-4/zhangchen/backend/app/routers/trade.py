from typing import List
from datetime import datetime
from decimal import Decimal, ROUND_HALF_DOWN
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Contest, ContestParticipant, Fund, FundPrice, Order, Holding, Transaction
from app.schemas import Order as OrderSchema, OrderCreate, OrderWithFund
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/trade", tags=["交易"])


def get_latest_nav(db: Session, fund_id: int) -> Decimal:
    """获取基金最新净值"""
    latest_price = db.query(FundPrice).filter(
        FundPrice.fund_id == fund_id
    ).order_by(desc(FundPrice.date)).first()
    
    if not latest_price:
        raise HTTPException(status_code=404, detail="基金净值数据不存在")
    
    return latest_price.nav


def update_participant_assets(db: Session, participant: ContestParticipant):
    """更新参赛者资产"""
    # 计算持仓市值
    holdings = db.query(Holding).filter(
        Holding.contest_id == participant.contest_id,
        Holding.user_id == participant.user_id
    ).all()
    
    total_market_value = Decimal("0")
    for holding in holdings:
        if holding.shares > 0:
            latest_nav = get_latest_nav(db, holding.fund_id)
            holding.current_nav = latest_nav
            holding.market_value = holding.shares * latest_nav
            holding.profit_loss = holding.market_value - (holding.shares * holding.avg_cost)
            if holding.avg_cost > 0:
                holding.return_rate = (holding.profit_loss / (holding.shares * holding.avg_cost)) * 100
            total_market_value += holding.market_value
    
    # 更新总资产和收益率
    participant.total_assets = participant.current_balance + total_market_value
    initial_balance = db.query(Contest).filter(Contest.id == participant.contest_id).first().initial_balance
    participant.total_return = ((participant.total_assets - initial_balance) / initial_balance) * 100
    
    db.commit()


@router.post("/buy", response_model=OrderSchema)
def buy_fund(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """买入基金"""
    # 验证比赛
    contest = db.query(Contest).filter(Contest.id == order_data.contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    if contest.status != "active":
        raise HTTPException(status_code=400, detail="比赛未开始或已结束")
    
    # 验证参赛者
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == order_data.contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=400, detail="您未参加此比赛")
    
    # 验证基金
    fund = db.query(Fund).filter(Fund.id == order_data.fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="基金不存在")
    
    # 验证金额
    if not order_data.amount or order_data.amount <= 0:
        raise HTTPException(status_code=400, detail="买入金额必须大于0")
    
    if order_data.amount > participant.current_balance:
        raise HTTPException(status_code=400, detail="余额不足")
    
    # 获取最新净值
    nav = get_latest_nav(db, order_data.fund_id)
    
    # 计算买入份额（扣除手续费，假设0.15%）
    fee_rate = Decimal("0.0015")
    fee = (order_data.amount * fee_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_DOWN)
    actual_amount = order_data.amount - fee
    shares = (actual_amount / nav).quantize(Decimal("0.0001"), rounding=ROUND_HALF_DOWN)
    
    # 创建订单
    order = Order(
        user_id=current_user.id,
        contest_id=order_data.contest_id,
        fund_id=order_data.fund_id,
        order_type="buy",
        amount=order_data.amount,
        nav=nav,
        status="completed",
        executed_at=datetime.now()
    )
    
    db.add(order)
    
    # 更新余额
    participant.current_balance -= order_data.amount
    
    # 更新或创建持仓
    holding = db.query(Holding).filter(
        Holding.user_id == current_user.id,
        Holding.contest_id == order_data.contest_id,
        Holding.fund_id == order_data.fund_id
    ).first()
    
    if holding:
        # 更新持仓
        total_cost = holding.shares * holding.avg_cost + actual_amount
        holding.shares += shares
        holding.avg_cost = (total_cost / holding.shares).quantize(Decimal("0.0001"), rounding=ROUND_HALF_DOWN)
    else:
        # 创建新持仓
        holding = Holding(
            user_id=current_user.id,
            contest_id=order_data.contest_id,
            fund_id=order_data.fund_id,
            shares=shares,
            avg_cost=nav,
            current_nav=nav,
            market_value=actual_amount,
            profit_loss=Decimal("0"),
            return_rate=Decimal("0")
        )
        db.add(holding)
    
    # 创建交易记录
    transaction = Transaction(
        user_id=current_user.id,
        contest_id=order_data.contest_id,
        fund_id=order_data.fund_id,
        transaction_type="buy",
        shares=shares,
        nav=nav,
        amount=actual_amount,
        fee=fee
    )
    db.add(transaction)
    
    # 更新资产
    update_participant_assets(db, participant)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/sell", response_model=OrderSchema)
def sell_fund(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """卖出基金"""
    # 验证比赛
    contest = db.query(Contest).filter(Contest.id == order_data.contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    if contest.status != "active":
        raise HTTPException(status_code=400, detail="比赛未开始或已结束")
    
    # 验证参赛者
    participant = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == order_data.contest_id,
        ContestParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=400, detail="您未参加此比赛")
    
    # 验证基金
    fund = db.query(Fund).filter(Fund.id == order_data.fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="基金不存在")
    
    # 验证持仓
    holding = db.query(Holding).filter(
        Holding.user_id == current_user.id,
        Holding.contest_id == order_data.contest_id,
        Holding.fund_id == order_data.fund_id
    ).first()
    
    if not holding or holding.shares <= 0:
        raise HTTPException(status_code=400, detail="您没有该基金的持仓")
    
    # 验证卖出份额
    if not order_data.shares or order_data.shares <= 0:
        raise HTTPException(status_code=400, detail="卖出份额必须大于0")
    
    if order_data.shares > holding.shares:
        raise HTTPException(status_code=400, detail="卖出份额超过持仓")
    
    # 获取最新净值
    nav = get_latest_nav(db, order_data.fund_id)
    
    # 计算卖出金额（扣除手续费，假设0.5%）
    fee_rate = Decimal("0.005")
    gross_amount = order_data.shares * nav
    fee = (gross_amount * fee_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_DOWN)
    actual_amount = gross_amount - fee
    
    # 创建订单
    order = Order(
        user_id=current_user.id,
        contest_id=order_data.contest_id,
        fund_id=order_data.fund_id,
        order_type="sell",
        shares=order_data.shares,
        nav=nav,
        status="completed",
        executed_at=datetime.now()
    )
    
    db.add(order)
    
    # 更新余额
    participant.current_balance += actual_amount
    
    # 更新持仓
    holding.shares -= order_data.shares
    if holding.shares == 0:
        holding.avg_cost = Decimal("0")
    
    # 创建交易记录
    transaction = Transaction(
        user_id=current_user.id,
        contest_id=order_data.contest_id,
        fund_id=order_data.fund_id,
        transaction_type="sell",
        shares=order_data.shares,
        nav=nav,
        amount=actual_amount,
        fee=fee
    )
    db.add(transaction)
    
    # 更新资产
    update_participant_assets(db, participant)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/orders", response_model=List[OrderWithFund])
def get_orders(
    contest_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单列表"""
    query = db.query(Order, Fund).join(Fund, Order.fund_id == Fund.id).filter(
        Order.user_id == current_user.id
    )
    
    if contest_id:
        query = query.filter(Order.contest_id == contest_id)
    
    orders = query.order_by(desc(Order.created_at)).all()
    
    result = []
    for order, fund in orders:
        result.append(OrderWithFund(
            id=order.id,
            user_id=order.user_id,
            contest_id=order.contest_id,
            fund_id=order.fund_id,
            order_type=order.order_type,
            amount=order.amount,
            shares=order.shares,
            nav=order.nav,
            status=order.status,
            created_at=order.created_at,
            executed_at=order.executed_at,
            fund_name=fund.name,
            fund_code=fund.code
        ))
    
    return result
