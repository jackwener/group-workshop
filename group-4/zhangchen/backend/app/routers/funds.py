from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models import Fund, FundPrice
from app.schemas import Fund as FundSchema, FundWithPrice, FundChartData
from app.routers.auth import get_current_active_user
from app.utils import get_fund_base_nav

router = APIRouter(prefix="/funds", tags=["基金"])


@router.get("", response_model=List[FundWithPrice])
def get_funds(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    fund_type: Optional[str] = None,
    company: Optional[str] = None,
    risk_level: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取基金列表"""
    query = db.query(Fund)
    
    # 应用筛选条件
    if fund_type:
        query = query.filter(Fund.type == fund_type)
    if company:
        query = query.filter(Fund.company == company)
    if risk_level:
        query = query.filter(Fund.risk_level == risk_level)
    if search:
        query = query.filter(
            (Fund.name.contains(search)) | (Fund.code.contains(search))
        )
    
    funds = query.offset(skip).limit(limit).all()
    
    # 获取最新净值
    result = []
    today = date.today()
    
    for fund in funds:
        latest_price = db.query(FundPrice).filter(
            FundPrice.fund_id == fund.id
        ).order_by(desc(FundPrice.date)).first()
        
        prev_price = None
        if latest_price:
            prev_price = db.query(FundPrice).filter(
                FundPrice.fund_id == fund.id,
                FundPrice.date < latest_price.date
            ).order_by(desc(FundPrice.date)).first()
        
        fund_data = FundWithPrice(
            id=fund.id,
            code=fund.code,
            name=fund.name,
            type=fund.type,
            company=fund.company,
            description=fund.description,
            risk_level=fund.risk_level,
            created_at=fund.created_at,
            latest_nav=latest_price.nav if latest_price else None,
            latest_date=latest_price.date if latest_price else None,
            daily_change=(float(latest_price.nav) - float(prev_price.nav)) if (latest_price and prev_price) else None,
            daily_change_rate=((float(latest_price.nav) - float(prev_price.nav)) / float(prev_price.nav) * 100) if (latest_price and prev_price) else None,
        )
        result.append(fund_data)
    
    return result


@router.get("/{fund_id}", response_model=FundWithPrice)
def get_fund(fund_id: int, db: Session = Depends(get_db)):
    """获取基金详情"""
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="基金不存在")
    
    # 获取最新净值
    latest_price = db.query(FundPrice).filter(
        FundPrice.fund_id == fund.id
    ).order_by(desc(FundPrice.date)).first()
    
    prev_price = None
    if latest_price:
        prev_price = db.query(FundPrice).filter(
            FundPrice.fund_id == fund.id,
            FundPrice.date < latest_price.date
        ).order_by(desc(FundPrice.date)).first()
    
    return FundWithPrice(
        id=fund.id,
        code=fund.code,
        name=fund.name,
        type=fund.type,
        company=fund.company,
        description=fund.description,
        risk_level=fund.risk_level,
        created_at=fund.created_at,
        latest_nav=latest_price.nav if latest_price else None,
        latest_date=latest_price.date if latest_price else None,
        daily_change=(float(latest_price.nav) - float(prev_price.nav)) if (latest_price and prev_price) else None,
        daily_change_rate=((float(latest_price.nav) - float(prev_price.nav)) / float(prev_price.nav) * 100) if (latest_price and prev_price) else None,
    )


@router.get("/{fund_id}/prices", response_model=List[dict])
def get_fund_prices(
    fund_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取基金历史净值"""
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="基金不存在")
    
    prices = db.query(FundPrice).filter(
        FundPrice.fund_id == fund_id
    ).order_by(desc(FundPrice.date)).limit(days).all()
    
    return [
        {
            "date": price.date.isoformat(),
            "nav": float(price.nav),
            "accum_nav": float(price.accum_nav) if price.accum_nav else None,
        }
        for price in prices
    ]


@router.get("/{fund_id}/chart", response_model=FundChartData)
def get_fund_chart(
    fund_id: int,
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """获取基金走势图数据"""
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="基金不存在")
    
    prices = db.query(FundPrice).filter(
        FundPrice.fund_id == fund_id
    ).order_by(FundPrice.date).limit(days).all()
    
    return FundChartData(
        dates=[price.date.isoformat() for price in prices],
        navs=[float(price.nav) for price in prices],
        accum_navs=[float(price.accum_nav) if price.accum_nav else float(price.nav) for price in prices],
    )


@router.get("/search/query", response_model=List[FundWithPrice])
def search_funds(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """搜索基金"""
    funds = db.query(Fund).filter(
        (Fund.name.contains(q)) | (Fund.code.contains(q))
    ).limit(limit).all()
    
    result = []
    for fund in funds:
        latest_price = db.query(FundPrice).filter(
            FundPrice.fund_id == fund.id
        ).order_by(desc(FundPrice.date)).first()
        
        fund_data = FundWithPrice(
            id=fund.id,
            code=fund.code,
            name=fund.name,
            type=fund.type,
            company=fund.company,
            description=fund.description,
            risk_level=fund.risk_level,
            created_at=fund.created_at,
            latest_nav=latest_price.nav if latest_price else None,
            latest_date=latest_price.date if latest_price else None,
        )
        result.append(fund_data)
    
    return result


@router.get("/types/list", response_model=List[str])
def get_fund_types(db: Session = Depends(get_db)):
    """获取基金类型列表"""
    types = db.query(Fund.type).distinct().all()
    return [t[0] for t in types if t[0]]


@router.get("/companies/list", response_model=List[str])
def get_fund_companies(db: Session = Depends(get_db)):
    """获取基金公司列表"""
    companies = db.query(Fund.company).distinct().all()
    return [c[0] for c in companies if c[0]]
