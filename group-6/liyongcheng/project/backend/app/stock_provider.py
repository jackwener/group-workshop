"""股价查询提供者模块"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.config import config


class BaseStockProvider(ABC):
    """股价提供者基类"""
    
    @abstractmethod
    def get_price(self, code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票价格
        
        Args:
            code: 股票代码（6位数字）
            
        Returns:
            股价数据字典
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供者是否可用"""
        pass
    
    @property
    @abstractmethod
    def source(self) -> str:
        """返回来源标识"""
        pass


class SinaStockProvider(BaseStockProvider):
    """新浪财经股价提供者"""
    
    def __init__(self):
        self.timeout = config.STOCK_API_TIMEOUT
    
    def is_available(self) -> bool:
        return True  # 新浪接口公开可用
    
    @property
    def source(self) -> str:
        return 'sina'
    
    def get_price(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            # 新浪财经API
            url = f"https://hq.sinajs.cn/list={'sh' if code.startswith('6') else 'sz'}{code}"
            response = requests.get(
                url,
                headers={
                    'Referer': 'https://finance.sina.com.cn',
                },
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                return self._parse_response(code, response.text)
            return None
        except Exception:
            return None
    
    def _parse_response(self, code: str, text: str) -> Optional[Dict[str, Any]]:
        """解析新浪接口响应"""
        try:
            # 格式：var hq_str_sh600519="贵州茅台,1850.00,..."
            import re
            match = re.search(r'="([^"]*)"', text)
            if not match:
                return None
            
            parts = match.group(1).split(',')
            if len(parts) < 32:
                return None
            
            name = parts[0]
            open_price = float(parts[1]) if parts[1] else 0
            last_close = float(parts[2]) if parts[2] else 0
            price = float(parts[3]) if parts[3] else 0
            high = float(parts[4]) if parts[4] else 0
            low = float(parts[5]) if parts[5] else 0
            volume = int(float(parts[8])) if parts[8] else 0
            amount = float(parts[9]) if parts[9] else 0
            
            change = price - last_close if last_close > 0 else 0
            change_percent = (change / last_close * 100) if last_close > 0 else 0
            
            return {
                'code': code,
                'name': name,
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'volume': volume,
                'amount': round(amount / 10000, 2),  # 转为万元
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'source': self.source,
            }
        except Exception:
            return None


class TencentStockProvider(BaseStockProvider):
    """腾讯财经股价提供者"""
    
    def __init__(self):
        self.timeout = config.STOCK_API_TIMEOUT
    
    def is_available(self) -> bool:
        return True
    
    @property
    def source(self) -> str:
        return 'tencent'
    
    def get_price(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            market = 'sh' if code.startswith('6') else 'sz'
            url = f"https://web.sqt.gtimg.cn/q=r_{market}{code}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return self._parse_response(code, response.text)
            return None
        except Exception:
            return None
    
    def _parse_response(self, code: str, text: str) -> Optional[Dict[str, Any]]:
        """解析腾讯接口响应"""
        try:
            import re
            match = re.search(r'="([^"]*)"', text)
            if not match:
                return None
            
            parts = match.group(1).split('~')
            if len(parts) < 45:
                return None
            
            name = parts[1]
            price = float(parts[3]) if parts[3] else 0
            last_close = float(parts[4]) if parts[4] else 0
            open_price = float(parts[5]) if parts[5] else 0
            volume = int(float(parts[6])) if parts[6] else 0
            high = float(parts[33]) if parts[33] else 0
            low = float(parts[34]) if parts[34] else 0
            amount = float(parts[37]) if parts[37] else 0
            
            change = price - last_close if last_close > 0 else 0
            change_percent = (change / last_close * 100) if last_close > 0 else 0
            
            return {
                'code': code,
                'name': name,
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'volume': volume,
                'amount': round(amount / 10000, 2),
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'source': self.source,
            }
        except Exception:
            return None


class MockStockProvider(BaseStockProvider):
    """模拟股价提供者"""
    
    def is_available(self) -> bool:
        return True  # 始终可用
    
    @property
    def source(self) -> str:
        return 'mock'
    
    def get_price(self, code: str) -> Optional[Dict[str, Any]]:
        """返回模拟股价数据"""
        return {
            'code': code,
            'name': f'股票{code}',
            'price': 100.00,
            'change': 1.50,
            'change_percent': 1.52,
            'open': 99.00,
            'high': 101.50,
            'low': 98.50,
            'volume': 1000000,
            'amount': 10000.00,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'source': self.source,
        }


class StockProviderChain:
    """股价提供者降级链"""
    
    def __init__(self):
        self.providers = [
            SinaStockProvider(),
            TencentStockProvider(),
            MockStockProvider(),
        ]
    
    def get_price(self, code: str) -> Dict[str, Any]:
        """
        按顺序尝试获取股价
        
        Returns:
            股价数据字典
        """
        for provider in self.providers:
            if provider.is_available():
                result = provider.get_price(code)
                if result:
                    return result
        
        # 兜底：返回模拟数据
        return MockStockProvider().get_price(code)


# 全局股价提供者链实例
stock_chain = StockProviderChain()
