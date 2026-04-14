from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.funds import router as funds_router
from app.routers.contests import router as contests_router
from app.routers.trade import router as trade_router
from app.routers.portfolio import router as portfolio_router
from app.routers.rankings import router as rankings_router
from app.routers.transactions import router as transactions_router

__all__ = [
    "auth_router",
    "users_router",
    "funds_router",
    "contests_router",
    "trade_router",
    "portfolio_router",
    "rankings_router",
    "transactions_router",
]
