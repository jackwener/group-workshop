import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict


# 模拟基金数据
MOCK_FUNDS = [
    {"code": "000001", "name": "华夏成长混合", "type": "混合型", "company": "华夏基金", "risk_level": 3, "base_nav": 1.5000},
    {"code": "000002", "name": "华夏大盘精选", "type": "股票型", "company": "华夏基金", "risk_level": 4, "base_nav": 2.3000},
    {"code": "000003", "name": "中海可转债债券A", "type": "债券型", "company": "中海基金", "risk_level": 2, "base_nav": 1.1000},
    {"code": "000004", "name": "嘉实稳健混合", "type": "混合型", "company": "嘉实基金", "risk_level": 3, "base_nav": 1.8000},
    {"code": "000005", "name": "嘉实增长混合", "type": "混合型", "company": "嘉实基金", "risk_level": 3, "base_nav": 2.1000},
    {"code": "000006", "name": "嘉实服务增值行业", "type": "股票型", "company": "嘉实基金", "risk_level": 4, "base_nav": 1.9500},
    {"code": "000007", "name": "鹏华货币A", "type": "货币型", "company": "鹏华基金", "risk_level": 1, "base_nav": 1.0000},
    {"code": "000008", "name": "嘉实中证500ETF联接", "type": "指数型", "company": "嘉实基金", "risk_level": 3, "base_nav": 1.6500},
    {"code": "000009", "name": "易方达天天理财货币A", "type": "货币型", "company": "易方达基金", "risk_level": 1, "base_nav": 1.0000},
    {"code": "000010", "name": "易方达增强回报债券A", "type": "债券型", "company": "易方达基金", "risk_level": 2, "base_nav": 1.2500},
    {"code": "000011", "name": "华夏大盘精选混合", "type": "混合型", "company": "华夏基金", "risk_level": 3, "base_nav": 2.8000},
    {"code": "000012", "name": "华安创新混合", "type": "混合型", "company": "华安基金", "risk_level": 3, "base_nav": 1.7200},
    {"code": "000013", "name": "易方达安心回报债券A", "type": "债券型", "company": "易方达基金", "risk_level": 2, "base_nav": 1.3800},
    {"code": "000014", "name": "华夏债券A", "type": "债券型", "company": "华夏基金", "risk_level": 2, "base_nav": 1.1500},
    {"code": "000015", "name": "华夏纯债债券A", "type": "债券型", "company": "华夏基金", "risk_level": 2, "base_nav": 1.0800},
    {"code": "000016", "name": "华夏沪深300ETF联接", "type": "指数型", "company": "华夏基金", "risk_level": 3, "base_nav": 1.4200},
    {"code": "000017", "name": "财通可持续发展主题股票", "type": "股票型", "company": "财通基金", "risk_level": 4, "base_nav": 1.6800},
    {"code": "000018", "name": "财通纯债债券A", "type": "债券型", "company": "财通基金", "risk_level": 2, "base_nav": 1.1200},
    {"code": "000019", "name": "景顺长城能源基建混合", "type": "混合型", "company": "景顺长城基金", "risk_level": 3, "base_nav": 2.1500},
    {"code": "000020", "name": "景顺长城品质成长混合", "type": "混合型", "company": "景顺长城基金", "risk_level": 3, "base_nav": 1.8900},
]


def generate_mock_funds() -> List[Dict]:
    """生成模拟基金数据"""
    funds = []
    for fund_data in MOCK_FUNDS:
        fund = {
            "code": fund_data["code"],
            "name": fund_data["name"],
            "type": fund_data["type"],
            "company": fund_data["company"],
            "description": f"{fund_data['name']}是由{fund_data['company']}管理的{fund_data['type']}基金，风险等级为{fund_data['risk_level']}级。",
            "risk_level": fund_data["risk_level"],
        }
        funds.append(fund)
    return funds


def generate_fund_prices(fund_id: int, fund_type: str, base_nav: float, days: int = 365) -> List[Dict]:
    """生成基金历史净值数据
    
    Args:
        fund_id: 基金ID
        fund_type: 基金类型，影响波动率
        base_nav: 基础净值
        days: 生成天数
    """
    prices = []
    
    # 根据基金类型设置波动率
    volatility_map = {
        "货币型": 0.0001,
        "债券型": 0.002,
        "混合型": 0.015,
        "股票型": 0.025,
        "指数型": 0.020,
    }
    volatility = volatility_map.get(fund_type, 0.01)
    
    # 生成随机游走数据
    current_nav = base_nav
    current_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        # 跳过周末
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # 随机游走
        change = random.gauss(0.0002, volatility)  # 略微正向漂移
        current_nav = current_nav * (1 + change)
        
        # 确保净值不为负
        current_nav = max(current_nav, 0.0001)
        
        price = {
            "fund_id": fund_id,
            "nav": Decimal(str(current_nav)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            "accum_nav": Decimal(str(current_nav * 1.05)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            "date": current_date.date(),
        }
        prices.append(price)
        
        current_date += timedelta(days=1)
    
    return prices


def get_fund_base_nav(fund_code: str) -> float:
    """获取基金基础净值"""
    for fund in MOCK_FUNDS:
        if fund["code"] == fund_code:
            return fund["base_nav"]
    return 1.0000
