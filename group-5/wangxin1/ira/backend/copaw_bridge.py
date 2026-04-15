"""
CoPaw 桥接模块
实现与 CoPaw 服务的 HTTP 桥接
"""
import os
import requests
from typing import Optional, Dict, Any


class CoPawBridge:
    """CoPaw HTTP 桥接"""
    
    def __init__(self):
        self.api_url = os.getenv('IRA_COPAW_API_URL', '')
        self.api_key = os.getenv('IRA_COPAW_API_KEY', '')
        self.timeout = 20  # 20秒超时
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_url and self.api_key)
    
    def ask(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """向 CoPaw 发送问答请求
        
        Args:
            query: 用户提问
            session_id: 会话 ID
            
        Returns:
            回答结果，如果失败返回 None
            {
                "answer": str,
                "model": str
            }
        """
        if not self.is_configured():
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "session_id": session_id
            }
            
            response = requests.post(
                f"{self.api_url}/ask",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "answer": data.get("answer", ""),
                    "model": data.get("model", "copaw-default")
                }
            else:
                return None
                
        except requests.Timeout:
            return None
        except Exception as e:
            print(f"CoPaw request error: {e}")
            return None
