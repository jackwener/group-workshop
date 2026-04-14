from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.models import User, Fund, FundPrice, Contest, ContestParticipant, Order, Holding, Transaction
from app.routers import (
    auth_router, users_router, funds_router, contests_router,
    trade_router, portfolio_router, rankings_router, transactions_router
)
from app.utils import generate_mock_funds, generate_fund_prices, get_fund_base_nav
from app.config import get_settings
from sqlalchemy.orm import Session
from app.database import SessionLocal

settings = get_settings()


def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已有基金数据
        fund_count = db.query(Fund).count()
        if fund_count == 0:
            print("初始化基金数据...")
            # 生成模拟基金数据
            mock_funds = generate_mock_funds()
            
            for fund_data in mock_funds:
                fund = Fund(
                    code=fund_data["code"],
                    name=fund_data["name"],
                    type=fund_data["type"],
                    company=fund_data["company"],
                    description=fund_data["description"],
                    risk_level=fund_data["risk_level"]
                )
                db.add(fund)
                db.flush()  # 获取fund.id
                
                # 生成基金价格数据
                base_nav = get_fund_base_nav(fund_data["code"])
                prices = generate_fund_prices(fund.id, fund_data["type"], base_nav, days=365)
                
                for price_data in prices:
                    price = FundPrice(
                        fund_id=price_data["fund_id"],
                        nav=price_data["nav"],
                        accum_nav=price_data["accum_nav"],
                        date=price_data["date"]
                    )
                    db.add(price)
            
            db.commit()
            print(f"已初始化 {len(mock_funds)} 只基金数据")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    init_db()
    yield
    # 关闭时执行


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基金模拟投资大赛系统API",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(funds_router, prefix="/api")
app.include_router(contests_router, prefix="/api")
app.include_router(trade_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(rankings_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")


@app.get("/")
def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
