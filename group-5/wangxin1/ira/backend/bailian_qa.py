"""
百炼 DashScope LLM 集成模块
"""
import os
from typing import Optional, Dict, Any


class BailianQA:
    """百炼 DashScope QA"""
    
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY', '')
        self.timeout = 120  # 120秒超时
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key)
    
    def ask(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """向百炼发送问答请求
        
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
            # 尝试导入 dashscope
            try:
                import dashscope
                from dashscope import Generation
            except ImportError:
                print("dashscope not installed, using mock response")
                return None
            
            dashscope.api_key = self.api_key
            
            response = Generation.call(
                model="qwen-max",
                messages=[
                    {"role": "system", "content": "你是一个专业的投研助手，帮助用户分析研报内容。"},
                    {"role": "user", "content": query}
                ],
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "answer": response.output.text,
                    "model": "qwen-max"
                }
            else:
                print(f"Bailian error: {response.message}")
                return None
                
        except Exception as e:
            print(f"Bailian request error: {e}")
            return None
