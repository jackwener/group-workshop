"""
Agent 编排模块 - 三级降级策略
CoPaw → 百炼 → Demo
"""
import os
import time
import json
import requests
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


class ReportAgent:
    """研报智能分析 Agent"""
    
    def __init__(self):
        self.copaw_url = os.getenv("IRA_COPAW_API_URL", "")
        self.copaw_key = os.getenv("IRA_COPAW_API_KEY", "")
        self.bailian_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.model = "qwen-max"
        print(f"[Agent初始化] bailian_key={'已配置' if self.bailian_key else '未配置'}, copaw_url={'已配置' if self.copaw_url else '未配置'}")
    
    def ask(self, query: str, file_content: Optional[str] = None) -> Tuple[str, bool, Optional[str], str]:
        """
        提交问题并获取回答
        
        Args:
            query: 用户问题
            file_content: 研报内容（可选）
        
        Returns:
            (answer, llm_used, model, answer_source)
        """
        # 构建提示词
        prompt = self._build_prompt(query, file_content)
        
        # 尝试 CoPaw
        if self.copaw_url:
            try:
                answer = self._call_copaw(prompt)
                if answer:
                    return answer, True, "copaw", "copaw"
            except Exception as e:
                print(f"CoPaw 调用失败: {e}")
        
        # 降级到百炼
        if self.bailian_key:
            print(f"[Agent] 尝试调用百炼 API...")
            try:
                answer = self._call_bailian(prompt)
                if answer:
                    print(f"[Agent] 百炼调用成功")
                    return answer, True, self.model, "bailian"
                else:
                    print(f"[Agent] 百炼返回空结果")
            except Exception as e:
                print(f"百炼调用失败: {e}")
        else:
            print(f"[Agent] bailian_key 为空，跳过百炼")
        
        # 降级到 Demo 模式
        answer = self._call_demo(query, file_content)
        return answer, False, None, "demo"
    
    def _build_prompt(self, query: str, file_content: Optional[str]) -> str:
        """构建提示词"""
        if file_content:
            return f"""请基于以下研报内容回答问题：

研报内容：
{file_content[:3000]}

用户问题：{query}

请提供专业、准确的回答："""
        else:
            return query
    
    def _call_copaw(self, prompt: str) -> Optional[str]:
        """
        调用 CoPaw API
        
        Args:
            prompt: 提示词
        
        Returns:
            回答内容，失败返回 None
        """
        if not self.copaw_url:
            return None
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.copaw_key:
            headers["Authorization"] = f"Bearer {self.copaw_key}"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 2000
        }
        
        response = requests.post(
            self.copaw_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get("response") or data.get("text") or data.get("content")
    
    def _call_bailian(self, prompt: str) -> Optional[str]:
        """
        调用阿里云百炼 API
        
        Args:
            prompt: 提示词
        
        Returns:
            回答内容，失败返回 None
        """
        if not self.bailian_key:
            return None
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bailian_key}"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": 2000
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # 解析百炼响应
        if "output" in data and "choices" in data["output"]:
            choices = data["output"]["choices"]
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                return message.get("content")
        
        return None
    
    def _call_demo(self, query: str, file_content: Optional[str]) -> str:
        """
        Demo 模式 - 返回模拟回答
        
        Args:
            query: 用户问题
            file_content: 研报内容
        
        Returns:
            模拟回答
        """
        # 模拟一些常见问题的回答
        demo_responses = {
            "评级": "根据研报分析，该股票获得【增持】评级。分析师认为公司基本面良好，未来增长潜力较大。",
            "目标价": "研报给出的目标价为 XX 元，较当前价格有 XX% 的上涨空间。",
            "业绩": "公司近期业绩表现稳健，营收同比增长 XX%，净利润同比增长 XX%。",
            "风险": "主要风险包括：1）宏观经济波动；2）行业竞争加剧；3）原材料价格波动。",
            "前景": "行业前景向好，公司在细分领域具有竞争优势，长期发展值得期待。",
        }
        
        # 尝试匹配关键词
        for keyword, response in demo_responses.items():
            if keyword in query:
                return response
        
        # 默认回答
        if file_content:
            return f"""基于研报内容的分析：

您的问题是：{query}

研报核心观点：
1. 公司基本面稳健，盈利能力持续提升
2. 行业景气度较高，市场需求旺盛
3. 估值处于合理区间，具备投资价值

【注意】这是演示模式回答。配置 CoPaw 或百炼 API 后可获得智能分析结果。"""
        else:
            return f"""您的问题是：{query}

【演示模式】
这是离线演示回答。请配置 LLM API 以获得智能分析：
- CoPaw API: 设置 IRA_COPAW_API_URL
- 百炼 API: 设置 DASHSCOPE_API_KEY

当前支持功能：
- 会话管理（创建、删除、查看历史）
- 文件上传（PDF/Word）
- 问答记录保存
"""
    
    def get_capabilities(self) -> Dict:
        """获取当前配置的能力状态"""
        return {
            "copaw_configured": bool(self.copaw_url),
            "bailian_configured": bool(self.bailian_key),
            "model": self.model if self.bailian_key else None
        }


# 全局 Agent 实例
_agent = None


def get_agent() -> ReportAgent:
    """获取全局 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = ReportAgent()
    return _agent
