import asyncio
import random
from typing import AsyncGenerator

from app.llm.provider import LLMProvider


class MockProvider(LLMProvider):
    """Mock LLM Provider，用于开发和演示"""
    
    # 投研相关的回复模板
    TEMPLATES = {
        "market_analysis": """## 市场分析

根据最新数据，当前市场呈现以下特征：

**大盘走势**
- 上证指数近期在3000-3100点区间震荡
- 成交量维持在8000亿左右，市场情绪较为谨慎
- 北向资金本周净流入约120亿元

**行业热点**
1. 新能源板块：光伏产业链价格企稳，储能需求持续增长
2. 人工智能：大模型应用落地加速，算力需求旺盛
3. 医药生物：创新药出海逻辑持续验证

**投资建议**
建议关注业绩确定性较强的龙头标的，控制仓位，逢低布局。""",
        
        "investment_advice": """## 投资建议

基于当前市场环境，为您提供以下配置建议：

**资产配置（建议比例）**
- 权益类：60%（其中成长型30%，价值型30%）
- 固收类：30%
- 现金及等价物：10%

**重点关注方向**
1. **高股息策略**：银行、电力、运营商等防御性板块
2. **科技成长**：AI算力、半导体设备、机器人
3. **消费复苏**：白酒、免税、医美等可选消费

**风险提示**
- 关注美联储货币政策变化
- 地缘政治风险可能影响市场情绪
- 建议分散投资，控制单一行业 exposure""",
        
        "risk_warning": """## 风险提示

⚠️ **重要风险提醒**

**市场风险**
- 当前市场估值处于历史中位数附近，存在波动风险
- 宏观经济复苏节奏可能不及预期
- 海外市场波动可能传导至A股

**行业风险**
- 部分热门赛道估值较高，需警惕回调风险
- 政策变化可能对特定行业产生影响
- 技术迭代可能导致部分企业竞争力下降

**操作建议**
1. 设置止损线，控制单笔亏损不超过10%
2. 避免追高，等待回调后的布局机会
3. 定期复盘，及时调整投资组合

投资有风险，入市需谨慎。以上分析仅供参考，不构成投资建议。""",
        
        "fund_analysis": """## 基金分析

**基金概况**
- 基金类型：偏股混合型基金
- 成立时间：2019年3月
- 管理规模：85亿元
- 基金经理：从业12年，年化收益15.3%

**业绩表现**
| 时间段 | 收益率 | 同类排名 |
|--------|--------|----------|
| 近1月 | 2.5% | 前30% |
| 近3月 | 8.2% | 前20% |
| 近1年 | 18.6% | 前15% |
| 近3年 | 45.3% | 前10% |

**持仓分析**
- 前十大重仓占比：58%
- 行业分布：科技(35%)、消费(25%)、医药(20%)、其他(20%)
- 换手率：120%，属于中等水平

**综合评价**
该基金长期业绩优秀，基金经理投资风格稳健，适合作为核心配置持有。""",
        
        "default": """您好！我是您的投研问答助手。

针对您的问题，我提供以下分析：

**核心观点**
当前市场环境复杂多变，建议采取"稳中求进"的投资策略。

**关键因素分析**
1. **宏观层面**：国内经济持续复苏，政策面保持积极
2. **流动性**：货币政策维持稳健，市场资金面相对宽松
3. **企业盈利**：上市公司业绩整体改善，结构性机会显现

**后续关注要点**
- 关注即将发布的宏观经济数据
- 跟踪行业政策变化
- 留意海外市场动向

如需更详细的分析，请告诉我您关注的具体板块或标的。"""
    }
    
    def __init__(self):
        self._name = "mock"
    
    @property
    def name(self) -> str:
        return self._name
    
    def _select_template(self, messages: list[dict]) -> str:
        """根据用户问题选择回复模板"""
        # 获取最后一条用户消息
        user_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_content = msg.get("content", "").lower()
                break
        
        # 关键词匹配
        if any(kw in user_content for kw in ["市场", "行情", "大盘", "走势", "指数"]):
            return self.TEMPLATES["market_analysis"]
        elif any(kw in user_content for kw in ["建议", "配置", "投资", "买入", "卖出", "持仓"]):
            return self.TEMPLATES["investment_advice"]
        elif any(kw in user_content for kw in ["风险", "警告", "注意", "警惕", "回调"]):
            return self.TEMPLATES["risk_warning"]
        elif any(kw in user_content for kw in ["基金", "经理", "业绩", "排名", "持仓"]):
            return self.TEMPLATES["fund_analysis"]
        else:
            return self.TEMPLATES["default"]
    
    async def generate(self, messages: list[dict], model: str = None) -> dict:
        """同步生成回复"""
        content = self._select_template(messages)
        
        # 模拟延迟
        await asyncio.sleep(0.5)
        
        # 估算 token 数量（简单估算：中文字符按1.5个token，英文按1个token）
        tokens_input = sum(len(m.get("content", "")) for m in messages)
        tokens_output = int(len(content) * 1.2)
        
        return {
            "content": content,
            "model": model or "mock-model",
            "tokens_input": tokens_input,
            "tokens_output": tokens_output
        }
    
    async def stream_generate(self, messages: list[dict], model: str = None) -> AsyncGenerator[str, None]:
        """流式生成回复，每5个字符 yield 一次，间隔50ms"""
        content = self._select_template(messages)
        
        # 每5个字符分块
        chunk_size = 5
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.05)  # 50ms 延迟
    
    async def health_check(self) -> bool:
        """健康检查 - Mock Provider 始终可用"""
        return True
