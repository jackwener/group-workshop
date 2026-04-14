import re
import time
import logging
from typing import Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ReportParser:
    """研报解析引擎 - 解析 PDF/HTML 文件并提取关键信息"""

    # 评级关键词映射
    RATING_MAP = {
        "买入": ["买入", "强烈推荐", "强推"],
        "增持": ["增持", "推荐"],
        "中性": ["中性", "持有", "观望"],
        "减持": ["减持", "回避"],
        "卖出": ["卖出"],
    }

    def parse(self, file_path: str, file_type: str) -> dict:
        """
        解析研报文件，返回结构化结果

        Args:
            file_path: 文件路径
            file_type: 文件类型 'pdf' 或 'html'

        Returns:
            {
                "title": str,
                "rating": str | None,
                "target_price": str | None,
                "core_views": list (≤5条),
                "data_forecast": dict,
                "parse_time_ms": int
            }

        Raises:
            ValueError: 解析失败时
        """
        start_time = time.time()

        try:
            # 提取文本
            if file_type == 'pdf':
                text = self._parse_pdf(file_path)
            elif file_type == 'html':
                text = self._parse_html(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {file_type}")

            if not text or not text.strip():
                raise ValueError("文件内容为空")

            # 提取各字段
            title = self._extract_title(text)
            rating = self._extract_rating(text)
            target_price = self._extract_target_price(text)
            core_views = self._extract_core_views(text)
            data_forecast = self._extract_data_forecast(text)

            parse_time_ms = int((time.time() - start_time) * 1000)

            return {
                "title": title,
                "rating": rating,
                "target_price": target_price,
                "core_views": core_views[:5],  # 最多5条
                "data_forecast": data_forecast,
                "parse_time_ms": parse_time_ms,
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Report parsing failed: {e}")
            raise ValueError(f"研报解析失败: {str(e)}")

    def _parse_pdf(self, file_path: str) -> str:
        """提取 PDF 文本内容"""
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except ImportError:
                raise ValueError("缺少 PDF 解析库，请安装 pdfplumber 或 PyPDF2")
        except Exception as e:
            raise ValueError(f"PDF 解析失败: {str(e)}")

        return text

    def _parse_html(self, file_path: str) -> str:
        """提取 HTML 文本内容"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            # 移除 script 和 style 标签
            for tag in soup(['script', 'style']):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            raise ValueError(f"HTML 解析失败: {str(e)}")

    def _extract_title(self, text: str) -> str:
        """提取标题（取第一行非空文本）"""
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                return line[:200]  # 标题限制200字符
        return "未知标题"

    def _extract_rating(self, text: str) -> Optional[str]:
        """从文本中提取评级"""
        # 优先匹配带前缀的评级格式
        rating_patterns = [
            r'(?:投资评级|评级|投资建议)[：:\s]*([^\n,，。]{1,10})',
            r'(?:维持|给予|首次覆盖|上调|下调)["""]?(\S{1,4})["""]?(?:评级|的评级)',
        ]

        for pattern in rating_patterns:
            match = re.search(pattern, text)
            if match:
                matched_text = match.group(1).strip()
                for rating, keywords in self.RATING_MAP.items():
                    for kw in keywords:
                        if kw in matched_text:
                            return rating

        # 全文关键词扫描（从严到宽）
        for rating, keywords in self.RATING_MAP.items():
            for kw in keywords:
                if kw in text:
                    return rating

        return None

    def _extract_target_price(self, text: str) -> Optional[str]:
        """从文本中提取目标价"""
        patterns = [
            r'目标价[：:\s]*(\d+\.?\d*)\s*元',
            r'目标价[：:\s]*(?:人民币|RMB)?\s*(\d+\.?\d*)',
            r'目标价位?[：:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*元[/／]?(?:股|share)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price = match.group(1)
                return f"{price}元"

        return None

    def _extract_core_views(self, text: str) -> List[str]:
        """从文本中提取核心观点（≤5条）"""
        views = []

        # 匹配带序号的观点
        patterns = [
            r'[①②③④⑤⑥⑦⑧⑨⑩]\s*([^\n①②③④⑤⑥⑦⑧⑨⑩]{10,200})',
            r'(?:^|\n)\s*[1-5][.、）)]\s*([^\n]{10,200})',
            r'(?:核心观点|投资要点|核心要点|主要观点)[：:\s]*\n([\s\S]{10,1000}?)(?:\n\n|\Z)',
        ]

        for pattern in patterns[:2]:
            matches = re.findall(pattern, text)
            if matches:
                for m in matches[:5]:
                    view = m.strip()
                    if len(view) >= 10:
                        views.append(view)
                if views:
                    return views[:5]

        # 从核心观点段落提取
        for pattern in patterns[2:]:
            match = re.search(pattern, text)
            if match:
                section = match.group(1)
                sentences = re.split(r'[。；\n]', section)
                for s in sentences:
                    s = s.strip()
                    if len(s) >= 10:
                        views.append(s)
                    if len(views) >= 5:
                        break
                if views:
                    return views[:5]

        # 兜底：提取文本中较长的句子作为观点
        sentences = re.split(r'[。\n]', text)
        for s in sentences:
            s = s.strip()
            if 20 <= len(s) <= 200 and not re.match(r'^[\d\s.%]+$', s):
                views.append(s)
            if len(views) >= 5:
                break

        return views[:5]

    def _extract_data_forecast(self, text: str) -> dict:
        """从文本中提取数据预测"""
        forecast = {}

        # 营收增速
        rev_match = re.search(r'(?:营[收业]|收入)(?:增[速长率]|同比)[：:\s]*(\d+\.?\d*)[%％]', text)
        if rev_match:
            forecast["revenue_growth"] = f"{rev_match.group(1)}%"

        # PE
        pe_match = re.search(r'(?:PE|市盈率)[：:\s]*(\d+\.?\d*)[倍xX]?', text)
        if pe_match:
            forecast["pe"] = pe_match.group(1)

        # EPS
        eps_match = re.search(r'(?:EPS|每股收益)[：:\s]*(\d+\.?\d*)\s*元?', text)
        if eps_match:
            forecast["eps"] = eps_match.group(1)

        # 净利润
        profit_match = re.search(r'净利润[：:\s]*(\d+\.?\d*)\s*(?:亿|万)?', text)
        if profit_match:
            forecast["net_profit"] = profit_match.group(0)

        return forecast
